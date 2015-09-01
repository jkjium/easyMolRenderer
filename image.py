from collections import OrderedDict
#%bucket 64 hilbert #A larger bucket size means more RAM usage and less time rendering.
#image {
#	resolution 1280 959
#	aa 2 2
#	samples 4
#	filter gaussian
#}
#trace-depths {
#	diff 4
#	refl 3
#	refr 2
#}
#gi {
#	type ambocc
#	bright { "sRGB nonlinear" 1 1 1 } 
#	dark { "sRGB nonlinear" 0 0 0 }
#	samples 32
#	maxdist 200.0 
#}
#background {
#	color  { "sRGB nonlinear" 1.0 1.0 1.0 }
#}
#object {
#	shader floor
#	type plane
#	p 0.000000 -11.743686 0.000000
#	n 0 1 0
#}
class Image:
	def __init__(self):
		self.attr = OrderedDict()
		# attributes for image section
		self.attr['resolution']='1280 959' # to be decided by camera fov
		self.attr['aa'] = '1 2' # 0 1 for preview, 1 2 for final rendering
		self.attr['samples'] = '4' #When used they indirectly affect many aspects of the scene but directly affects DoF and camera/object motion blur.
		self.attr['filter'] = 'gaussian' # box and triangle for preview. gaussian, mitchell, blackman-harris for final
		
		# attributes for trace-depths section
		self.attr['diff']='1'
		self.attr['refl']='4'
		self.attr['refr']='4'
		
		# attributes for gi
		self.attr['type'] = 'ambocc'
		self.attr['bright'] = '{ "sRGB nonlinear" 1 1 1 }'
		self.attr['dark'] = '{ "sRGB nonlinear" 0 0 0 }'
		self.attr['gi:samples']='32'
		self.attr['maxdist']='200.0' # the higher the darker
		
		# background
		self.attr['bg_color'] = '{ "sRGB nonlinear" 1.0 1.0 1.0 }'
		self.attr['floor:color'] = '1.0 1.0 1.0'
		
		# floor
		self.floorHeight = float('inf')
		self.attr['floor:p'] = [0.0, 0.0, 0.0] # to be adjust according to the minimum point
		self.attr['floor:n'] = '0 1 0' # determined by camera.up attribute
		self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype diffuse\n\tdiff 1.0 1.0 1.0\n}\n'
		self.floorShadow = 1
		self.outputWidth = 1280

		# global shader
		self.attr['globalShader'] = 'diff'

	def setOutputWidth(self, width):
		self.outputWidth = width

	def setFloorShadow(self, flag):
		self.floorShadow = flag

	def setGlobalShader(self, shader):
		self.attr['globalShader'] = shader

	def setBGGrayScale(self, index):
		if index == 0:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 1.0 1.0 1.0 }'
			self.attr['floor:color'] = '1.0 1.0 1.0'
		elif index == 1:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 0.8 0.8 0.8 }'
			self.attr['floor:color'] = '0.605 0.605 0.605'
		elif index == 2:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 0.6 0.6 0.6 }'
			self.attr['floor:color'] = '0.32 0.32 0.32'
		elif index == 3:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 0.4 0.4 0.4 }'
			self.attr['floor:color'] = '0.133 0.133 0.133'
		elif index == 4:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 0.2 0.2 0.2 }'
			self.attr['floor:color'] = '0.033 0.033 0.033'
		elif index >= 5:
			self.attr['bg_color'] = '{ "sRGB nonlinear" 0 0 0 }'
			self.attr['floor:color'] = '0 0 0'


	def setFloorShader(self, shader):
		if shader == 'diff':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype diffuse\n\tdiff %s\n}\n' % (self.attr['floor:color'])
		elif shader == 'glass':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype glass\n\teta 1.33\n\tcolor  1 1 1\n\tabsorbtion.distance 5.0\n}\n' 
		elif shader == 'mirror':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype mirror\n\trefl 1 1 1\n}\n' 
		elif shader == 'shiny':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype shiny\n\tdiff { "sRGB nonlinear" %s }\n\trefl 0.5\n}\n' % (self.attr['floor:color'])
		elif shader == 'phong':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype phong\n\tdiff { "sRGB linear" %s }\n\tspec { "sRGB linear" %s } 50\n\tsamples 4\n}\n' % (self.attr['floor:color'], self.attr['floor:color'])


	def SCString(self):
		#image {
		#	resolution 1280 959
		#	aa 2 2
		#	samples 4
		#	filter gaussian
		#}	
		imageStr = 'image {\n\tresolution %s\n\taa %s\n\tsamples %s\n\tfilter %s\n}\n' % (self.attr['resolution'], self.attr['aa'], self.attr['samples'], self.attr['filter'])
		#trace-depths {
		#	diff 4
		#	refl 3
		#	refr 2
		#}
		traceDepthsStr = 'trace-depths {\n\tdiff %s\n\trefl %s\n\trefr %s\n}\n' % (self.attr['diff'], self.attr['refl'], self.attr['refr'])
		#gi {
		#	type ambocc
		#	bright { "sRGB nonlinear" 1 1 1 } 
		#	dark { "sRGB nonlinear" 0 0 0 }
		#	samples 32
		#	maxdist 200.0 
		#}		
		giStr = 'gi {\n\ttype %s\n\tbright %s\n\tdark %s\n\tsamples %s\n\tmaxdist %s\n}\n' % (self.attr['type'], self.attr['bright'], self.attr['dark'], self.attr['gi:samples'], self.attr['maxdist'])
		#background {
		#	color  { "sRGB nonlinear" 1.0 1.0 1.0 }
		#}		
		bgStr = 'background {\n\tcolor %s\n}' % (self.attr['bg_color'])
		return ('%s\n%s\n%s\n%s\n') % (imageStr, traceDepthsStr, giStr, bgStr)		
	
	def floorSCString(self):
		if self.floorShadow == 0:
			return ''
		else:
		#object {
		#	shader floor
		#	type plane
		#	p 0.000000 -11.743686 0.000000
		#	n 0 1 0
		#}	
			return self.attr['floor:shader'] + ('object {\n\tshader floor\n\ttype plane\n\tp %f %f %f\n\tn %s\n}\n') % (self.attr['floor:p'][0], self.attr['floor:p'][1], self.attr['floor:p'][2], self.attr['floor:n'])