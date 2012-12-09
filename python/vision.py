from SimpleCV import *
from numpy import *
from nump.linalg import *

import time

CAMERA_PROPERTIES = {'width':1280, 'height':720}
EDGE_THRESHOLD = 0.1
BLOB_AREA_THRESH = 700
BINARY = (80,80,80)
TABLE_LENGTH = 38; #table length in cm
TABLE_HEIGHT = 27; #table height in cm
GPTS = [(0,0), (0,TABLE_HEIGHT), (TABLE_LENGTH,TABLE_HEIGHT), (TABLE_LENGTH,0)] #ground points clockwise from btm-left

class ImageProcessor:

	def __init__(self):
		cam = Camera(camera_index=1, prop_set=CAMERA_PROPERTIES)
		self.camera = Camera(prop_set=CAMERA_PROPERTIES)
		if cam:
			self.camera = cam
		self.bg = self.camera.getImage()

	def calibrate(self):
		bg = self.camera.getImage()
		bg = self.camera.getImage()
		self.bg = bg.copy()
		self.bg.show()
		self.bg = self.bg.binarize(thresh=BINARY)
		
	def check(self):
		fg = self.camera.getImage()
		fg = self.camera.getImage()
		self.fg = fg.copy()
		self.fg.show()
		self.fg = self.fg.binarize(thresh=BINARY)
		result = None
		if self.bg is not None:
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
					result.append([b.minRectX(), b.minRectY(), b])
					b.draw()
					b.drawMinRect(color=Color.CYAN)
					#blobs[-1].hullImage().show()
		i.show()
		return result


	#compute image Homography, ipts is a list of 4 image coords of corners
	#ipts should be list of tuples [(),(),(),()]
	def compute_H(self, ipts):
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
		self.H = H
def main():
	ip = ImageProcessor()
	print "Enter to take Background Image!"
	sys.stdin.readline()
	ip.calibrate()

	print "Enter to take Foreground Image!"
	sys.stdin.readline()
	#ip.calibrate()
	res = ip.check()
	
	print "Enter to find blobs!"
	sys.stdin.readline()
	#res = ip.check()

	print "Finding Blobs:"
	objList = ip.find_objects(res)
	for a in objList:
		print "({0},{1}) W,H,A: {2},{3},{4}".format(a[0],a[1],a[2].minRectWidth(),a[2].minRectHeight(),a[2].area())
		#print "(" + str(a[0]) + "," + str(a[1]) + ")" + " W,H,A: "  + str(a[2].minRectWidth()) + "," + str(a[2].minRectHeight() + "," + str(a[2].area()
	
	print "Enter to Quit"
	sys.stdin.readline()
	ip = None

main()
