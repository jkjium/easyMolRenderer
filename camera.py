from collections import OrderedDict
#camera {
#  type pinhole
#  eye    0.0 0.0 0.0
#  target 0.0 0.0 -89.6766
#  up     0.0 1.0 0.0
#  fov    45.0
#  aspect 1.3333333735
#}
# determine focus distance
class Camera:
	def __init__(self):
		self.upIndex = 1
		self.attr = OrderedDict()
		self.attr['type']='pinhole'
		self.attr['eye'] = '0.0 0.0 0.0'
		self.attr['target'] = '0.0 0.0 -80.0'
		self.attr['up'] = '0.0 1.0 0.0'
		self.attr['fov'] = '30.0'
		self.attr['aspect'] = '1.3333333735'
			#self.shutter = '0 1' #for motion blur
		# t='thinlens':
			#self.fdist = 30.0 #focus distance
			#self.lensr = 1.0 # blurry value for out of focus objects
			#self.sides = 6
			#self.rotation 36.0
		#t=='spherical':
		#t=='fisheye':
		
	def SCString(self):
		attrStr='camera {'
		for key in self.attr:
			attrStr = ('%s\n\t%s %s') % (attrStr, key, self.attr[key])
		attrStr = ('%s\n}\n') % (attrStr)
		return attrStr