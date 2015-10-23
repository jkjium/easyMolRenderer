import math
import StringIO
from camera import Camera
from image import Image
from shaderFactory import ShaderFactory

# povray output paring class
class pov:
	def __init__(self):
		self.globalCamera = Camera()
		self.globalImage = Image()
		self.globalShaderFactory = ShaderFactory()

		self.dispatch = {'camera':self.parseCamera, '#default':self.parseDefault, 'light_source':self.parseLightSource, 'plane':self.parsePlane, 'mesh2':self.parseMesh2, 'sphere':self.parseSphere, 'cylinder':self.parseCylinder}

	def parsePov(self, pov_str):
		print 'in parsePov'
		for key in self.dispatch.keys():
			pov_str = pov_str.replace(key, '\n'+key)

		print pov_str


	def parseCamera(self):
		print 'parsing camera'

	def parseDefault(self):
		print 'parsing Default'

	def parseLightSource(self):
		print 'parsing light'

	def parseMesh2(self):
		print 'parsing mesh'

	def parseCylinder(self):
		print 'parsing cylinder'

	def parsePlane(self):
		print 'parsing plane'

	def parseSphere(self):
		print 'parsing sphere'
