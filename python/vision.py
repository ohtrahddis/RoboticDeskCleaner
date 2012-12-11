from SimpleCV import *
from numpy import *
from numpy.linalg import *
from IK import *

import time

CAMERA_PROPERTIES = {'width':1280, 'height':720}
EDGE_THRESHOLD = 0.1
BLOB_AREA_THRESH = 800 #reject blobs smaller than
BINARY = (80,80,80)
TABLE_LENGTH = 38; #table length in cm
TABLE_HEIGHT = 27; #table height in cm
GPTS = [(0,0), (0,TABLE_HEIGHT), (TABLE_LENGTH,TABLE_HEIGHT), (TABLE_LENGTH,0)] #ground points clockwise from btm-left

SQUARE_BIN = (10,10)
RECT_BIN = (15,15)
STICK_BIN = (20,20)
MISC_BIN = (25,25)
TYPE_TO_BIN = {'square': SQUARE_BIN, 'rectangle': RECT_BIN, 'stick': STICK_BIN, 'misc': MISC_BIN}

class ImageProcessor:

	def __init__(self):
		self.camera = Camera(camera_index=1)
		self.bg = self.camera.getImage()

	def calibrate(self):
		bg = self.camera.getImage()
		bg = self.camera.getImage()
		self.bg = bg.copy()
		self.disp = self.bg.show()
		self.corners = self.get_corners(self.disp)
		self.H = self.compute_H(self.corners)
		self.Q = inv(self.H)
		self.bg = self.bg.binarize(thresh=BINARY)
		
	def check(self):
		fg = self.camera.getImage()
		fg = self.camera.getImage()
		self.fg = fg.copy()
		self.fg.show()
		self.fg = self.fg.binarize(thresh=BINARY)
		result = None
		if self.bg:
			result = self.fg - self.bg
			result = result.applyGaussianFilter()
			#result = result.binarize(thresh=BINARY)
			#some interesting opencv segmentation + bg/fg stuff
		return result
	
	def find_objects(self, img):
		i = img
		blobs = i.findBlobs()
		result = []
		if blobs is not None:
			for b in blobs:
				if b.area() > BLOB_AREA_THRESH:
					#bcoord = (b.minRectX(),b.minRectY())
					bcoord = b.centroid()
					(x,y) = self.image_to_real(bcoord)
					width = b.minRectWidth()
					height = b.minRectHeight()
					angle = b.angle()
					ratio = width/height
					area = b.area()
					if(ratio<1):
						ratio = 1/ratio
					result.append([(x,y), width, height, angle, ratio, area, b])
					b.draw()
					b.drawMinRect(color=Color.CYAN)
					i.drawCircle(bcoord,3,color=Color.RED,thickness=-1)
					#blobs[-1].hullImage().show()
		i.show()
		return result


	#compute image Homography, ipts is a list of 4 image coords of corners
	#ipts should be list of tuples [(),(),(),()]
	def compute_H(self, ipts):
		
		print ipts
		x0 = GPTS[0][0]
		y0 = GPTS[0][1]
		x1 = GPTS[1][0]
		y1 = GPTS[1][1]
		x2 = GPTS[2][0]
		y2 = GPTS[2][1]
		x3 = GPTS[3][0]
		y3 = GPTS[3][1]

		u0 = ipts[0][0]
		v0 = ipts[0][1]
		u1 = ipts[1][0]
		v1 = ipts[1][1]
		u2 = ipts[2][0]
		v2 = ipts[2][1]
		u3 = ipts[3][0]
		v3 = ipts[3][1]

		A = array([[x0,y0,1,0,0,0,-u0*x0, -u0*y0], [0,0,0,x0,y0,1,-v0*x0,-v0*y0], [x1,y1,1,0,0,0,-u1*x1,-u1*y1], [0,0,0,x1,y1,1,-v1*x1,-v1*y1], [x2,y2,1,0,0,0,-u2*x2,-u2*y2], [0,0,0,x2,y2,1,-v2*x2,-v2*y2], [x3,y3,1,0,0,0,-u3*x3,-u3*y3], [0,0,0,x3,y3,1,-v3*x3,-v3*y3]])
		b = array([[u0],[v0],[u1],[v1],[u2],[v2],[u3],[v3]])

		x = solve(A,b)

		h11 = x[0]
		h12 = x[1]
		h13 = x[2]
		h21 = x[3]
		h22 = x[4]
		h23 = x[5]
		h31 = x[6]
		h32 = x[7]

		H = array([[h11,h12,h13], [h21,h22,h23], [h31,h32, 1]])
		return H
	
	def get_corners(self, disp):
		corners = []
		while(disp.isNotDone()):
			time.sleep(0.001)
			up = disp.leftButtonUpPosition()
			if(len(corners)>=4):
				disp.quit()
				break

			if(up):
				corners.append(up)
		return corners

	def real_to_image(self, coord):
		x = coord[0]
		y = coord[1]
		if self.H.all():
			H = self.H
			u = (H[0][0]*x + H[0][1]*y + H[0][2])/(H[2][0]*x + H[2][1]*y + 1)
			v = (H[1][0]*x + H[1][1]*y + H[1][2])/(H[2][0]*x + H[2][1]*y + 1)
		return (u,v)

	def image_to_real(self, coord):
		u = coord[0]
		v = coord[1]
		if self.Q.all():
			Q = self.Q
			x = (Q[0][0]*u + Q[0][1]*v + Q[0][2])/(Q[2][0]*u + Q[2][1]*v + Q[2][2])
			y = (Q[1][0]*u + Q[1][1]*v + Q[1][2])/(Q[2][0]*u + Q[2][1]*v + Q[2][2])
		return (x,y)

	def categorize(self, ratio):
		if ratio >= 1 and ratio <= 1.2:
			return "square"
		elif ratio > 1.2 and ratio <= 5:
			return "rectangle"
		elif ratio > 5:
			return "stick"
		return "misc"

