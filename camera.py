'''
camera {
	type pinhole/thinlens
	eye 0.0   0.0   0.0
	target 0.0 0.0 -57.8435
	up 0.0 1.0 0.0
	fov 25.0
	aspect 1.3333334303
	fdist 111.7
	lensr 1.30
}

In pov.parseCamera() the value of aspect will be determined.
Dof needs the range of z axis, therefore attr['fdist'] is set after all the geometries have been parsed 
but before camera.SCString() be called in Pov.parsePov().

'''
class Camera:
	def __init__(self):
		self.upIndex = 1
		self.dofScale = 1.0 # recording dof slide value from gui
		self.attr = {}
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
		self.attr['fdist'] = 10.0
		self.attr['lensr'] = 2.3

		
	def SCString(self):
		attrStr='camera {'
		attrStr = ('%s\n\ttype %s') % (attrStr, self.attr['type'])
		attrStr = ('%s\n\teye %s') % (attrStr, self.attr['eye'])
		attrStr = ('%s\n\ttarget %s') % (attrStr, self.attr['target'])
		attrStr = ('%s\n\tup %s') % (attrStr, self.attr['up'])
		attrStr = ('%s\n\tfov %s') % (attrStr, self.attr['fov'])
		attrStr = ('%s\n\taspect %s') % (attrStr, self.attr['aspect'])
		if self.attr['type'] == 'thinlens':
			attrStr = ('%s\n\tfdist %.1f') % (attrStr, self.attr['fdist'])
			attrStr = ('%s\n\tlensr %.2f') % (attrStr, self.attr['lensr'])

		attrStr = ('%s\n}\n') % (attrStr)
		return attrStr