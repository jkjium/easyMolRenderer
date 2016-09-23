class ShaderFactory:
	seleSlot = {'diff': 0.01, 'mirror': 0.02, 'shiny': 0.03, 'ambocc': 0.04, 'glass': 0.05, 'phong': 0.06}
	shaderDict = {'111': 'diff', '222': 'phong', '333': 'glass', '444': 'mirror', '555':'shiny'}
	def __init__(self):
		self.ShaderNames={}
		self.SCSelector={'diff': self.diffSCString, 'mirror': self.mirrorSCString, 'shiny':self.shinySCString, 'ambocc':self.amboccSCString, 'glass':self.glassSCString, 'phong':self.phongSCString}
		
		self.shaderType = 'diff'
		self.colorSpace = 'sRGB nonlinear'
		# sRGB linear
		# sRGB nonlinear
		# XYZ

	# given color return shader name	
	def assignShaderName(self, color_id):
		if color_id in self.ShaderNames:
			return self.ShaderNames[color_id]
		else:
			self.ShaderNames[color_id]= 'sh.%d' % len(self.ShaderNames) #shader sh.%d
			return self.ShaderNames[color_id]		
			
	def SCString(self, defaultShader):
		outString=''
		for ckey in self.ShaderNames:
			shaderType = self.decodeShader(ckey, defaultShader)
			outString = '%s\n%s' % (outString, self.SCSelector[shaderType.lower()](ckey))
		return outString+'\n'

	# get shader from color info
	def decodeShader(self, color_id, defaultShader):
		rgb = color_id.split(' ')
		shaderID = '%s%s%s' % (rgb[0][5], rgb[1][5], rgb[2][5])
		if shaderID not in self.shaderDict:
			return defaultShader
		else:
			return self.shaderDict[shaderID]

	
	def diffSCString(self, color_id):
	#shader {
	#	name sh.0
	#	type diffuse
	#	diff 1.0000 0.6000 0.6000
	#}
		return 'shader {\n\tname %s\n\ttype diffuse\n\tdiff { "%s" %s }\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id)

	def mirrorSCString(self, color_id):
	#shader {
  	#	name sh.0
  	#	type mirror
  	#	refl 0.8 0.2 0.2
	#}
		return 'shader {\n\tname %s\n\ttype mirror\n\trefl { "%s" %s }\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id)

	def shinySCString(self, color_id):
	#shader {
  	#	name sh.0
  	#	type shiny
  	#	diff { "sRGB nonlinear" 0.80 0.250 0.250 }
  	#	refl 0.1
	#}
		return 'shader {\n\tname %s\n\ttype shiny\n\tdiff { "%s" %s }\n\trefl 0.8\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id)

	def amboccSCString(self, color_id):
	#shader {
  	#	name Sfamb.red
  	#	type amb-occ
  	#	bright { "sRGB nonlinear" 1 1 1 } 
  	#	dark { "sRGB nonlinear" 0.70 0.25 0.25 } 
  	#	samples 32
  	#	dist 9.0
	#}
		return 'shader {\n\tname %s\n\ttype amb-occ\n\tbright { "%s" 0.9 0.9 0.9 }\n\tdark { "%s" %s }\n\tsamples 32\n\tdist 9.0\n}\n' % (self.ShaderNames[color_id], self.colorSpace, self.colorSpace, color_id)

	def glassSCString(self, color_id):
	#shader {
	#	name sh.trans.00
	#	type glass
	#	eta 1.0
	#	color { "sRGB nonlinear" 0.800 0.800 0.800 }
	#	absorbtion.distance 5.0
	#	absorbtion.color { "sRGB nonlinear" 1.0 1.0 1.0 }
	#}
		return 'shader {\n\tname %s\n\ttype glass\n\teta 1.33\n\tcolor { "%s" %s }\n\tabsorbtion.distance 5.0\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id)

	def phongSCString(self, color_id):
	#shader sfpho.shader {
 	#	type phong
 	#	diffuse color "sRGB linear" 0.604 0.604 0.604
	#	specular color "sRGB linear" 1.0 1.0 1.0
 	#	power float 50.0
 	#	samples int 4
	#}
		return 'shader {\n\tname %s\n\ttype phong\n\tdiff { "%s" %s }\n\tspec { "%s" %s } 80\n\tsamples 4\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id, self.colorSpace, color_id)
