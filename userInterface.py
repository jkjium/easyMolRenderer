

class UserInterface:
	def __init__(self, img, mode):
		self.image = img

		# set init values
		self.bgGrayScale = 0
		self.floorShader = 'diff'
		self.globalShader = 'diff'
		self.floorShadow = 1

		# read parameters
		print 'mode: %d' % (mode)
		if mode == 0:
			self.parseCFG()

		# set scene 
		self.image.setBGGrayScale(self.bgGrayScale)
		self.image.setFloorShader(self.floorShader)
		self.image.setGlobalShader(self.globalShader)
		self.image.setFloorShadow(self.floorShadow)

	def parseCFG(self):
		print 'parsing config ...\n'
		cfgfile = 'scene.config'
		cfg = open(cfgfile, 'r')
		cfglines = cfg.readlines()

		for line in cfglines:
			line = line.strip()
			print '%d: %s' % (len(line), line)
			if len(line)==0 or '#' in line:
				continue	
			keyvalue = line.split(' ')

			if 'bgGrayScale' == keyvalue[0]:
				self.bgGrayScale = int(keyvalue[1])
				print 'set bgGrayScale: %s\n' % keyvalue[1]
			elif 'floorShader' == keyvalue[0]:
				self.floorShader = keyvalue[1]
				print 'set floorShader: %s\n' % keyvalue[1]
			elif 'globalShader' == keyvalue[0]:
				self.globalShader = keyvalue[1]
				print 'set floorShader: %s\n' % keyvalue[1]
			elif 'floorShadow' == keyvalue[0]:
				self.floorShadow = int(keyvalue[1])
				print 'set floorShadow: %s\n' % keyvalue[1]


		cfg.close()


