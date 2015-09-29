

class UserInterface:
	def __init__(self, img, mode):
		self.image = img

		# set init values
		self.floorShader = 'diff'
		self.globalShader = 'diff'
		self.floorShadow = 1
		self.outputWidth = 1280
		self.floorAngle = 0.0
		self.floorColor = '1 1 1'

		# read parameters
		print 'mode: %d' % (mode)
		if mode == 0:
			self.parseCFG()

		# set scene 
		self.image.setFloorColor(self.floorColor)
		self.image.setFloorShader(self.floorShader)
		self.image.setGlobalShader(self.globalShader)
		self.image.setFloorShadow(self.floorShadow)
		self.image.setOutputWidth(self.outputWidth)
		self.image.setFloorAngle(self.floorAngle)

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
			#keyvalue = line.split(' ')
			brk = line.find(' ')
			keyvalue =[]
			keyvalue.append(line[0:brk].strip())
			keyvalue.append(line[brk:].strip())

			if 'floorShader' == keyvalue[0]:
				self.floorShader = keyvalue[1]
				print 'set floorShader: %s\n' % keyvalue[1]
			elif 'globalShader' == keyvalue[0]:
				self.globalShader = keyvalue[1]
				print 'set floorShader: %s\n' % keyvalue[1]
			elif 'floorShadow' == keyvalue[0]:
				self.floorShadow = int(keyvalue[1])
				print 'set floorShadow: %s\n' % keyvalue[1]
			elif 'outputWidth' == keyvalue[0]:
				self.outputWidth = int(keyvalue[1])
				print 'set outputWidth: %s\n' % keyvalue[1]
			elif 'floorAngle' == keyvalue[0]:
				self.floorAngle = float(keyvalue[1])
				if self.floorAngle > 90.0:
					self.floorAngle = 90.0
				print 'set floorAngle: %s\n' % keyvalue[1]
			elif 'floorColor' == keyvalue[0]:
				self.floorColor = keyvalue[1]
				print 'set floorColor: %s\n' % keyvalue[1]

		cfg.close()

	# check for lowest point according to different floor:n
	# assume Y is the up axis
	# the rotation is about x axis
	def checkLowestPoint(self, pArray):
		cp = [0.0,0.0,0.0]
		cp[0] = float(pArray[0])
		cp[1] = float(pArray[1])
		cp[2] = float(pArray[2])

		self.image.checkLowestPoint(cp)








