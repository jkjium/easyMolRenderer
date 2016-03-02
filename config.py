'''
reading cfgfile for configurations
'''

class config:
	def __init__(self, cfgfile):

		# set init values
		self.floorShader = 'diff'
		self.globalShader = 'diff'
		self.floorShadow = 1
		self.outputWidth = 2560
		self.floorAngle = 10.0
		self.floorColor = '1 1 1'
		self.dofDist = -1

		# read parameters
		self.parseCFG(cfgfile)

	def parseCFG(self, cfgfile):
		print 'parsing config ...\n'
		cfg = open(cfgfile, 'r')
		cfglines = cfg.readlines()
		cfg.close()

		for line in cfglines:
			line = line.strip()
			#print '%d: %s' % (len(line), line)
			if len(line)==0 or '#' in line:
				continue	
			#keyvalue = line.split(' ')
			brk = line.find(' ')
			keyvalue =[]
			keyvalue.append(line[0:brk].strip())
			keyvalue.append(line[brk:].strip())

			if 'floorShader' == keyvalue[0]:
				self.floorShader = keyvalue[1]
				print 'set floorShader: %s' % keyvalue[1]
			elif 'globalShader' == keyvalue[0]:
				self.globalShader = keyvalue[1]
				print 'set floorShader: %s' % keyvalue[1]
			elif 'floorShadow' == keyvalue[0]:
				self.floorShadow = int(keyvalue[1])
				print 'set floorShadow: %s' % keyvalue[1]
			elif 'outputWidth' == keyvalue[0]:
				self.outputWidth = int(keyvalue[1])
				print 'set outputWidth: %s' % keyvalue[1]
			elif 'floorAngle' == keyvalue[0]:
				self.floorAngle = float(keyvalue[1])
				if self.floorAngle > 90.0:
					self.floorAngle = 90.0
				print 'set floorAngle: %s' % keyvalue[1]
			elif 'floorColor' == keyvalue[0]:
				self.floorColor = keyvalue[1]
				print 'set floorColor: %s' % keyvalue[1]
			elif 'dofDist' == keyvalue[0]:
				self.dofDist = int(keyvalue[1])
				print 'set dofDist: %d' % self.dofDist


