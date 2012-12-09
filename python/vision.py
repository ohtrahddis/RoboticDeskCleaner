from SimpleCV import *

import time
import os
import socket

CAMERA_PROPERTIES = {'width':1280, 'height':720}
EDGE_THRESHOLD = 0.1
BLOB_AREA_THRESH = 700

class ImageProcessor:

	def __init__(self):
		cam = Camera(camera_index=1, prop_set=CAMERA_PROPERTIES)
		self.camera = Camera(prop_set=CAMERA_PROPERTIES)
		if cam:
			self.camera = cam
		self.bg = self.camera.getImage()

	def calibrate(self):
		bg = self.camera.getImage()
		self.bg = bg.copy()
		self.bg.show()
		
	def check(self):
		fg = self.camera.getImage()
		self.fg = fg.copy()
		self.fg.show()
		result = None
		if self.bg is not None:
			result = self.fg - self.bg
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
					b.drawMinRect(color=Color.WHITE)
					#blobs[-1].hullImage().show()
		i.show()
		return result

def main():
	ip = ImageProcessor()
	print "Enter to take Background Image!"
	sys.stdin.readline()
	ip.calibrate()

	print "Enter to take Foreground Image!"
	sys.stdin.readline()
	ip.calibrate()
	
	print "Enter to find blobs!"
	sys.stdin.readline()
	res = ip.check()

	print "Finding Blobs:"
	objList = ip.find_objects(res)
	for a in objList:
		print "({0},{1}) W,H,A: {2},{3},{4}".format(a[0],a[1],a[2].minRectWidth(),a[2].minRectHeight(),a[2].area())
		#print "(" + str(a[0]) + "," + str(a[1]) + ")" + " W,H,A: "  + str(a[2].minRectWidth()) + "," + str(a[2].minRectHeight() + "," + str(a[2].area()
	
	print "Enter to Quit"
	sys.stdin.readline()
	ip = None

main()
