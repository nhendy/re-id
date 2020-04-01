import numpy as np
import cv2
import operator

def coord_extraction (img):
    '''
    This function takes in an image with blue reference points. It filters out all pixels with the color blue 
    and then group those points by x-coordinates. It returns the average x,y value of each group as a set of 
    reference points
    '''
    # Load the image
    image = cv2.imread(img)
    width = image.shape[1]
    height= image.shape[0]
    if width < 200 or height < 200:
        resize_factor = 10
        dwidth = int(width*resize_factor)
        dheight= int(height*resize_factor)
        dim = (dwidth,dheight)
        resized = cv2.resize(image,dim)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    else:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Filter blue color
    lower_blue = np.array([35, 140, 60])
    upper_blue = np.array([255, 255, 180])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)  
    coord=cv2.findNonZero(mask)

    if width < 200 or height < 200:
        res = cv2.bitwise_and(resized,resized, mask= mask)
    else:
        res = cv2.bitwise_and(image,image, mask= mask)

    x_coordinate = np.array([])
    y_coordinate = np.array([])

    # Put all coordinates that are blue in a list
    for pt in coord:
        x,y = np.split(pt[0],2)
        x_coordinate = np.append(x_coordinate,x[0])
        y_coordinate = np.append(y_coordinate,y[0])

    coord_list = []
    for i in range (0,x_coordinate.size):
        coord_list.append((x_coordinate[i],y_coordinate[i]))

    coord_list.sort(key = operator.itemgetter(0))

    # Group the coordinates
    x_coordinate = []
    y_coordinate = []
    for pt in coord_list:
        x,y = pt
        x_coordinate.append(x)
        y_coordinate.append(y)

    x_coord = [[]]
    x_coord[0].append(x_coordinate[0])
    axis_value = 0

    for i in range(1,len(x_coordinate)):
        if np.abs(x_coordinate[i] - x_coordinate[i-1]) >= 100:
            x_coord.append([])
            axis_value += 1
        x_coord[axis_value].append(x_coordinate[i])

    y_coord = [[]]
    y_coord[0].append(y_coordinate[0])
    axis_value = 0
    incr = 1

    for j in range(1,len(y_coordinate)):
        if incr == len(x_coord[axis_value]):
            y_coord.append([])
            axis_value += 1
            incr = 0
        y_coord[axis_value].append(y_coordinate[j])
        incr += 1

    pt_x = []
    pt_y = []

    # Calculate average of x/y values of each group
    for x in x_coord:
        if width < 200 or height < 200:
            mean = np.mean(x)
            mean = int(mean/10)
        else:
            mean = int(np.mean(x))
        pt_x.append(mean)

    for y in y_coord:
        if width < 200 or height < 200:
            mean = np.mean(y)
            mean = int(mean/10)
        else:
            mean = int(np.mean(y))
        pt_y.append(mean)


    pts = np.stack((pt_x, pt_y), axis=-1)
    return pts

def transform_2d(frame_data):
	#Camera and floor plan hard coded points
	camera_pts = coord_extraction('camera_reference.jpg')
	fl_plan_pts = coord_extraction('2d_reference.png')

	#Open camera and floor plan
	cam_img = cv2.imread('00000.jpg',cv2.IMREAD_COLOR)
	fl_plan_img = cv2.imread('floor_plan.png',cv2.IMREAD_COLOR)
	h,w,l = fl_plan_img.shape
	size = (w,h)

	#Calculate H matrix
	H,stat = cv2.findHomography(camera_pts,fl_plan_pts)

	c = 1
	img_array = []

	for frame in frame_data:
		for data in frame:
			#pt is the point to 2D map
			pt = np.array([[data[0],data[1]]], dtype='float32')
			pt = np.array([pt])

			#get the mapping array
			req_map = cv2.perspectiveTransform(pt,H)
			circle_rad = 5
			circ_col = (255,0,0)
			thickness = -1

			mapp = req_map[0]

			#Draw the points on camera and floor plan
			for cord in mapp:
				center = (int(cord[0]),int(cord[1]))
				fl_plan_img = cv2.circle(fl_plan_img,center,circle_rad,circ_col,thickness)
				fl_plan_img = cv2.putText(fl_plan_img,str(data[2]),(int(cord[0]),int(cord[1])),cv2.FONT_HERSHEY_SIMPLEX,1,color=(0, 255, 0),thickness=1)
		#TODO: save img in gallery and reset img
		#img_name = "frame"+str(c)+".jpg"
		#cv2.imwrite("data/"+img_name,fl_plan_img)
		img_array.append(fl_plan_img)
		fl_plan_img = cv2.imread('floor_plan.png',cv2.IMREAD_COLOR)
		c=c+1
	video = cv2.VideoWriter('2d_proj_vid.avi',cv2.VideoWriter_fourcc(*'DIVX'),30,size)
	for i in img_array:
		video.write(i)
	video.release()

def main():
	transform_2d()

if __name__=="__main__":
	main()