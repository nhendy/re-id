import opt
from PIL import Image
import os
import cv2

def getLoader(path):
    # check if path exists
    if not os.path.exists(path):
        raise ValueError("path: {} does not exist".format(path))
    contents = os.listdir(path)

    # check if path is empty
    if len(contents) == 0:
        raise ValueError("nothing in {}".format(path))

    # if working with frames create loader with directories
    if options[opt.args.loader] == "frames":
        contents = [name for name in contents if os.path.isdir(os.path.join(path, name))]
        frames = {cont: os.listdir("{}/{}".format(path, cont)) for cont in contents}

        # the least number of frames a video has
        minlen = min([len(cont) for cont in frames.values()])

        #clipping all videos to match
        frames = {key: cont[0: minlen] for key, cont in frames.items()}
        return FrameLoader(path, frames)

    elif options[opt.args.loader] == "videos":
        contents = [name for name in contents if not os.path.isdir(os.path.join(path, name))]
        return VideoLoader(path, contents)

class Loader:
    def __init__(self):
        pass

    def getVidNames(self):
        return self.videos.keys()


class FrameLoader(Loader):
    def __init__(self, path, frames):
        super().__init__()
        self.path = path
        self.videos = frames
        self.index = 0
        self.length = len(list(frames.values())[0])

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= self.length:
            raise StopIteration
        frames = {key: frames[self.index] for key, frames in self.videos.items()}
        frames = {key: Image.open(os.path.join(self.path, key, img)) for key, img in frames.items()}
        intosend = self.index
        self.index = self.index + opt.args.interval
        return intosend, frames

    def __len__(self):
        return int(self.length / opt.args.interval)


class VideoLoader(Loader):
    def __init__(self, path, vids):
        super().__init__()
        self.path = path
        names = ['.'.join(key.split('.')[:-1]) for key in vids]
        self.videos = {name: cv2.VideoCapture(os.path.join(path, file)) for name, file in zip(names, vids)}
        self.index = 0
        self.length = min([vid.get(cv2.CAP_PROP_FRAME_COUNT) for name, vid in self.videos.items()])

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= self.length:
            raise StopIteration
        retval = dict()
        for name, vid in self.videos.items():
            vid.set(cv2.CAP_PROP_POS_FRAMES, self.index)
            _, retval[name] = vid.read()
        indtosend = self.index
        self.index = self.index + opt.args.interval
        return indtosend, retval

    def __len__(self):
        return int(self.length / opt.args.interval)


options = {
    opt.defaultkey: "frames",
    "frames": "frames",
    "videos": "videos"
}

