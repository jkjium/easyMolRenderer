import warnings
import os 
import shutil
import subprocess
import Tkinter
import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import Pmw
import tkColorChooser
from pymol import cmd
from types import *
import time
import math
import StringIO
import re

try:
	from pymol import *
	havePymol = True
except ImportError:
	havePymol = False
	warnings.warn("Failed to load module pymol, functions might be incomplete")


def __init__(self):
    
	self.menuBar.addmenuitem('Plugin','command','pykflow',label = 'pyKFlow', command = lambda s = self : pyKFlowPlugin(s))    

# kflow start
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
		self.attr['lensr'] = 1.5

		
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



class ShaderFactory:

	# map for pymol selection specific shader assignment
	seleSlot = {'diff': 0.001, 'phong': 0.002, 'shiny': 0.003, 'mirror': 0.004, 'glass': 0.005, 'ambocc': 0.006}

	def __init__(self):
		self.ShaderNames={}
		self.SCSelector={'diff': self.diffSCString, 'mirror': self.mirrorSCString, 'shiny':self.shinySCString, 'ambocc':self.amboccSCString, 'glass':self.glassSCString, 'phong':self.phongSCString}
		
		self.shaderType = 'diff'
		self.seleShader = {}

		# shader settings
		self.colorSpace = 'sRGB nonlinear'
		self.shaderSamples = 4
		self.phongSpec = 50
		self.shinyRefl = 0.5
		self.glassETA = 1.33		

	# given color return shader name	
	# color_str: 0.0000,0.00000,0.00000
	def assignShaderName(self, color_str):
		rgb = color_str.split(',')
		color_id = '%s %s %s' % (rgb[0][0:5], rgb[1][0:5], rgb[2][0:5])
		if color_id in self.ShaderNames:
			return self.ShaderNames[color_id]
		else:
			self.ShaderNames[color_id]= 'sh.%d' % len(self.ShaderNames) #shader sh.%d
			#print 'add %s as name: %s' % (color_id, self.ShaderNames[color_id])
			return self.ShaderNames[color_id]		
			
	def SCString(self, shaderType):
		outString=''
		#print repr(self.seleShader)
		for ckey in self.ShaderNames:
			#print ckey
			if ckey in self.seleShader:
				outString = '%s\n%s' % (outString, self.SCSelector[self.seleShader[ckey][0]](ckey))
			else:
				outString = '%s\n%s' % (outString, self.SCSelector[shaderType.lower()](ckey))
		return outString+'\n'
	
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
		return 'shader {\n\tname %s\n\ttype shiny\n\tdiff { "%s" %s }\n\trefl %.1f\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id, self.shinyRefl)

	def amboccSCString(self, color_id):
	#shader {
  	#	name Sfamb.red
  	#	type amb-occ
  	#	bright { "sRGB nonlinear" 1 1 1 } 
  	#	dark { "sRGB nonlinear" 0.70 0.25 0.25 } 
  	#	samples 32
  	#	dist 9.0
	#}
		return 'shader {\n\tname %s\n\ttype amb-occ\n\tbright { "sRGB nonlinear" 0.9 0.9 0.9 }\n\tdark { "sRGB nonlinear" %s }\n\tsamples 32\n\tdist 9.0\n}\n' % (self.ShaderNames[color_id], color_id)

	def glassSCString(self, color_id):
	#shader {
	#	name sh.trans.00
	#	type glass
	#	eta 1.0
	#	color { "sRGB nonlinear" 0.800 0.800 0.800 }
	#	absorbtion.distance 5.0
	#	absorbtion.color { "sRGB nonlinear" 1.0 1.0 1.0 }
	#}
		return 'shader {\n\tname %s\n\ttype glass\n\teta %.2f\n\tcolor { "%s" %s }\n\tabsorbtion.distance 5.0\n}\n' % (self.ShaderNames[color_id], self.glassETA, self.colorSpace, color_id)

	def phongSCString(self, color_id):
	#shader sfpho.shader {
 	#	type phong
 	#	diffuse color "sRGB linear" 0.604 0.604 0.604
	#	specular color "sRGB linear" 1.0 1.0 1.0
 	#	power float 50.0
 	#	samples int 4
	#}
		return 'shader {\n\tname %s\n\ttype phong\n\tdiff { "%s" %s }\n\tspec { "%s" %s } %d\n\tsamples %d\n}\n' % (self.ShaderNames[color_id], self.colorSpace, color_id, self.colorSpace, color_id, self.phongSpec, self.shaderSamples)


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
		self.attr = {}
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
		#self.floorHeight = float('inf') # not support in pymol
		self.floorHeight = 1e3000
		self.attr['floor:p'] = [0.0, 0.0, 0.0] # to be adjust according to the minimum point
		self.attr['floor:n'] = [0.0, 1.0, 0.0] # determined by camera.up attribute
		self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype diffuse\n\tdiff 1.0 1.0 1.0\n}\n'


		# [DOF]
		# works with camera
		# camera.attr['type']='thinlens'
		# camera.fdist = 0 ~ self.maxz #focus distance
		# camera.lensr = 1.0 # blurry value for out of focus objects
		# adjusted in parseCamera()
		# setup values for dof
		# corresponding changes in camera.SCString()

		# dof switch
		self.dof = False
		# fdist for dof
		# updated in checkLowestPoint()
		#self.maxz = -1e3000
		self.maxz = -200
		self.minz = 200

		self.floorShadow = 1
		self.outputWidth = 1280
		self.floorAngle = 90.0

		self.minHeight = 1e3000 #float('inf')
		self.lowestPoint = [0.0, 0.0, 0.0]

		# global shader
		self.attr['globalShader'] = 'diff'


	def setFloorAngle(self, angle):
		self.floorAngle = angle

	def setOutputWidth(self, width):
		self.outputWidth = width

	def setFloorShadow(self, flag):
		self.floorShadow = flag

	def setGlobalShader(self, shader):
		self.attr['globalShader'] = shader

	def setFloorColor(self, color):
		self.attr['floor:color'] = color


	def setFloorShader(self, shader):
		shader=shader.lower()
		if shader == 'diff':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype diffuse\n\tdiff %s\n}\n' % (self.attr['floor:color'])
		elif shader == 'glass':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype glass\n\teta 1.33\n\tcolor  %s\n\tabsorbtion.distance 5.0\n}\n' % (self.attr['floor:color'])
		elif shader == 'mirror':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype mirror\n\trefl %s\n}\n' % (self.attr['floor:color'])
		elif shader == 'shiny':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype shiny\n\tdiff { "sRGB nonlinear" %s }\n\trefl 0.5\n}\n' % (self.attr['floor:color'])
		elif shader == 'phong':
			self.attr['floor:shader'] = 'shader {\n\tname floor\n\ttype phong\n\tdiff { "sRGB linear" %s }\n\tspec { "sRGB linear" %s } 50\n\tsamples 4\n}\n' % (self.attr['floor:color'], self.attr['floor:color'])

	# assume Y is the up axis
	# all the points rotate negative floorAngle to find the lowest height (Y) by applying rotx
	#   old point = [a, b, c]
	#	new point = [a, b*cos(x)+(-1)*c*sin(x), b*sin(x)+c*cos(x)]
	# point in original coordinate system will be recorded
	def checkLowestPoint(self, cp):
		np = [cp[0], cp[1]*math.cos(math.radians(-1*self.floorAngle)) + (-1)*cp[2]*math.sin(math.radians(-1*self.floorAngle)), cp[1]*math.sin(math.radians(-1*self.floorAngle)) + cp[2]*math.cos(math.radians(-1*self.floorAngle))]
		if np[1] < self.floorHeight:
			self.floorHeight = np[1]
			self.lowestPoint[0] = cp[0]
			self.lowestPoint[1] = cp[1]
			self.lowestPoint[2] = cp[2]
		if cp[2] > self.maxz:
			self.maxz = cp[2]
		if cp[2] < self.minz:
			self.minz = cp[2]



	# output SC strings
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
#		bgStr = 'background {\n\tcolor %s\n}' % (self.attr['bg_color'])
		bgStr = 'background {\n\tcolor %s\n}' % ('1.0 1.0 1.0')
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
			self.attr['floor:n'][1] = math.cos(math.radians(self.floorAngle))
			self.attr['floor:n'][2] = math.sin(math.radians(self.floorAngle))

			self.attr['floor:p'][0] = self.lowestPoint[0]
			self.attr['floor:p'][1] = self.lowestPoint[1] - 2
			self.attr['floor:p'][2] = self.lowestPoint[2]
			return self.attr['floor:shader'] + ('object {\n\tshader floor\n\ttype plane\n\tp %f %f %f\n\tn %f %f %f\n}\n') % (self.attr['floor:p'][0], self.attr['floor:p'][1], self.attr['floor:p'][2], self.attr['floor:n'][0], self.attr['floor:n'][1], self.attr['floor:n'][2])

# povray output paring class
class pov:
	def __init__(self):
		self.globalCameraUpIndex = 0
		#self.globalFloorMin = float('inf')

		self.globalCamera = Camera()
		self.globalImage = Image()
		self.globalShaderFactory = ShaderFactory()

		self.dispatch = {'camera':self.parseCamera, '#default':self.parseDefault, 
				'light_source':self.parseLightSource, 'plane':self.parsePlane, 
				'mesh2':self.parseMesh2, 'sphere':self.parseSphere, 'cylinder':self.parseCylinder}

		self.globalSCString={'camera':[], '#default':[], 'light_source':[], 
						'plane':[], 'mesh2':[], 'sphere':[], 'cylinder':[]}


	# convert pov into sc file
	def parsePov(self, pov_str):
		pov_str=pov_str.replace('\n',' ').replace('\r','')
		for key in self.dispatch.keys():
			pov_str = pov_str.replace(key, '\n'+key)

		buf = StringIO.StringIO(pov_str)
		povlines = buf.readlines()
		#povlines = pov_str.split('\n')

		t1 = time.time()
		count = 0
		for line in povlines:
			line = line.strip()
			if len(line)<2: continue
			for key in self.dispatch.keys():
				if key in line[0:15]:
					count+=1
					self.globalSCString[key].append(self.dispatch[''.join(key)](line))
					#if count%1000==0:
					#	print str(count)+' primitives parsed ...'
		t2 = time.time()
		print 'Writing SC information ...\nTime elapsed: %s seconds.' % (str(t2-t1))

		# after get minmax z, before writing camera
		if self.globalCamera.attr['type'] == 'thinlens':
			# -1.0 * (min - max) since z is always negative
			self.globalCamera.attr['fdist'] = -1.0 * (self.globalCamera.dofScale * (self.globalImage.minz - self.globalImage.maxz)/90.0 + self.globalImage.maxz)



		fout=open('kflow.sc','w')
		# globalSCString['camera'] stores Image informat not camera
		# after adding dof, camera SC need to generate after all the geometry parsed.
		fout.write(''.join(self.globalSCString['camera']))
		fout.write(self.globalCamera.SCString())
	#	out.write(''.join(globalSCString['light_source']))
		fout.write(self.globalShaderFactory.SCString(self.globalImage.attr['globalShader']))
		fout.write(self.globalImage.floorSCString())
		fout.write(''.join(self.globalSCString['mesh2']))
		fout.write(''.join(self.globalSCString['sphere']))
		fout.write(''.join(self.globalSCString['cylinder']))		

		fout.close()


	def checkLowestPoint(self, pArray):
		cp = [0.0,0.0,0.0]
		cp[0] = float(pArray[0])
		cp[1] = float(pArray[1])
		cp[2] = float(pArray[2])

		self.globalImage.checkLowestPoint(cp)		


	# parse camera information
	def parseCamera(self, entry):
		N=len(entry)
		locationIdx = entry.find('location')
		for i in xrange(locationIdx+8,N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				location = entry[i+1:j].replace(',',' ')
				#print location
				break
		endPoint = j
		rightIdx = entry[endPoint:N].find('right')+endPoint
		for i in xrange(rightIdx, N):
			if entry[i].isdigit() == True:
				j=i+1
				while entry[j]!='*': j+=1
				aspect = entry[i:j]
				#print aspect
				break
		endPoint = j
		upIdx = entry[endPoint:N].find('up')+endPoint
		for i in xrange(upIdx, N):
			if (entry[i].isalpha() == True) and (entry[i] in 'xyz'):
				if entry[i]=='x':
					up = '1.0 0.0 0.0'
					self.globalCamera.upIndex = 0
					self.globalImage.attr['floor:n'] = [1.0, 0.0, 0.0]
				elif entry[i] == 'y':
					up = '0.0 1.0 0.0'
					self.globalCamera.upIndex = 1
					self.globalImage.attr['floor:n'] = [0.0, 1.0, 0.0]
				else:
					up = '0.0 0.0 1.0'
					self.globalCamera.upIndex = 2
					self.globalImage.attr['floor:n'] = [0.0, 0.0, 1.0]
				#print 'globalCameraUpIndex: %d\n' % self.globalCamera.upIndex 
				break
		target = '\ttarget 0.0 0.0 -57.8435' # change later
		width = self.globalImage.outputWidth
		height = width/float(aspect)
		self.globalImage.attr['resolution'] = '%d %d' % (width, height)
		
		self.globalCamera.attr['eye']=location
		self.globalCamera.attr['up'] = up
		self.globalCamera.attr['target']='0.0 0.0 -57.8435'
		self.globalCamera.attr['fov']='25.0'
		self.globalCamera.attr['aspect']=aspect
		
		#return self.globalImage.SCString()+self.globalCamera.SCString()		
		return self.globalImage.SCString()	

	# do nothing
	def parseDefault(self, entry):
		return ''

	def parsePlane(self, entry):
		return ''

	# parse light information
	def parseLightSource(self, entry):
		N=len(entry)

		for i in xrange(0, N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>':j+=1
				point = entry[i+1:j].replace(',', ' ') # find light location
				break
		endPoint = j
		for i in xrange(endPoint,N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>':j+=1
				color = entry[i+1:j].replace(',', ' ') # find color
				break

		return 'light {\n\ttype point\n\tcolor { "sRGB nonlinear" %s }\n\tpower 100.0\n\tp %s\n}\n' % (color, point)		


	# parse Mesh 2 
	def parseMesh2(self, entry):
		N=len(entry)
		sfVectors = '\tpoints 3\n'
		
		transIdx = entry.find('transmit') #hard coded the space. 
		if transIdx!=-1:
			i=transIdx+len('transmit')
			while entry[i].isdigit()!=True: i+=1
			j=i
			while (entry[j].isdigit() or entry[j]=='.'): j+=1
			transmit = float(entry[i:j])*10.0
		
		vertexIdx = entry.find('vertex_vectors')
		# parse vertex
		for i in xrange(vertexIdx+15, N): #mesh2 { vertex_vectors { 3, <-5.3871469498,-5.4616031647,-69.2255630493>, <-5.5629453659,-6.2845845222,-68.7088241577>, <-5.7161660194,-5.9352922440,-69.4062881470>}  
			if entry[i]=='}': # sign for vertex_vectors section end
				break
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>':j+=1
				point = entry[i+1:j].replace(',', ' ')
				sfVectors=sfVectors+'\t\t'+point+'\n'
				# for finding the lowest point
				self.checkLowestPoint(point.split(' '))

		endPoint = j
		# parse normals
		sfNormals = '\tnormals vertex\n'
		normalIdx = entry[endPoint:N].find('normal_vectors')+endPoint
		for i in xrange(normalIdx+15, N): #normal_vectors { 3, <-0.8562379479,0.3649974763,0.3655590415>, <-0.8029828072,0.3864040971,0.4537735879>, <-0.8294824362,0.4455040097,0.3368754089>} 
			if entry[i]=='}': # sign for vertex_vectors section end
				break
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>':j+=1
				point = entry[i+1:j].replace(',', ' ')
				sfNormals=sfNormals+'\t\t'+point+'\n'
		# parse texture
		endPoint = j
		sfShader = ''
		pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
		for i in xrange(pigmentIdx+7,N): #texture_list { 3, texture { pigment{color rgb<0.00201,0.0000,1.0000> }} ,texture { pigment{color rgb<0.00201,0.0000,1.0000> }} ,texture { pigment{color rgb<0.00201,0.0000,1.0000> }} } 
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				#color = entry[i+1:j].replace(',', ' ')
				color = entry[i+1:j]
				#print color
				sfShader = self.globalShaderFactory.assignShaderName(color)
				break # only one color for one mesh
		endPoint = j
		
		# parse face order
		sfTriangle = '\ttriangles 1\n'
		faceIdx = entry[endPoint:N].find('face_indices')+endPoint
		for i in xrange(faceIdx,N):  #face_indices { 1, <0,1,2>, 0, 1, 2 } } 
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				faces = entry[i+1:j].replace(',', ' ')
				#print faces
				sfTriangle=sfTriangle+'\t\t'+faces+'\n'
		
		return ('object {\n\tshader %s\n\ttype generic-mesh\n%s%s%s\tuvs none\n}\n') % (sfShader, sfVectors, sfTriangle, sfNormals)		


	# parse sphere information
	def parseSphere(self, entry):
		N=len(entry)
		transIdx = entry.find('transmit') #hard coded the space. 
		if transIdx!=-1:
			i=transIdx+len('transmit')
			while entry[i].isdigit()!=True: i+=1
			j=i
			while (entry[j].isdigit() or entry[j]=='.'): j+=1
			transmit = float(entry[i:j])*10.0
		
		# read center vector
		centerIdx = entry.find('<')
		for i in xrange(centerIdx,N):
			if entry[i]=='>':
				center = entry[centerIdx+1:i].replace(',',' ')
				# for finding the lowest point
				self.checkLowestPoint(center.split(' '))
				break
		endPoint = i
		# read radius
		for i in xrange(endPoint, N):
			if entry[i].isdigit() == True:
				j=i+1
				while entry[j].isdigit() or entry[j]=='.': j+=1
				radius = entry[i:j]
				#print radius
				break
		endPoint = j
		sfShader = ''
		pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
		for i in xrange(pigmentIdx, N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				color = entry[i+1:j]
				sfShader = self.globalShaderFactory.assignShaderName(color)
				break

		return ('\nobject {\n\tshader %s\n\ttype sphere\n\tc %s\n\tr %s\n}') % (sfShader, center, radius)		


	# parse cylinder information
	def parseCylinder(self, entry):
		N=len(entry)
		vertexIdx = entry.find('vertex_vectors')
		# parse vertex
		p1Idx = entry.find('<')
		for i in xrange(p1Idx,N):
			if entry[i]=='>':
				p1 = entry[p1Idx+1:i].replace(',',' ')
				break
		endPoint = i	
		for i in xrange(endPoint, N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				p2 = entry[i+1:j].replace(',',' ')
				break
		endPoint = j
		for i in xrange(endPoint, N):
			if entry[i].isdigit()==True:
				j=i+1
				while entry[j].isdigit() or entry[j]=='.': j+=1
				radius = entry[i:j]
				break
		endPoiint = j
		sfShader = ''
		pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
		for i in xrange(pigmentIdx, N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				color = entry[i+1:j]
				#print color
				sfShader = self.globalShaderFactory.assignShaderName(color)
				break	

		pArray = p2.split(' ')
		a = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
		pArray = p1.split(' ')
		b = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
		d = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
		r = math.sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2])
		
		scaleu = float(radius)
		scalez = r/(2*scaleu) # should be 0.25	
		
		center = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)
		x=d[2]
		y=d[0]
		z=d[1]

		phi = math.atan2(z, math.sqrt(x*x+y*y))
		th = math.atan2(y,x)
		
		# thCoor: the norm against which the cylinder should rotates after rotatey
		thCoor = th + 1.5708 # pi/2
		nz = math.cos(thCoor)
		nx = math.sin(thCoor)
		ny =0
		
	#	object {
	#	   shader sh.0
	#	   transform {
	#		  scale 1 1 1.2228
	#		  scaleu 0.25
	#		  rotatey 48.4996
	#		  rotate 0.6626 0 -0.7490 117.3103
	#		  translate -0.8666 0.8980 -21.9849
	#	   }  
	#	   type cylinder
	#	}	
		return ('\nobject {\n\tshader %s\n\ttransform {\n\t\tscale 1 1 %f\n\t\tscaleu %f\n\t\trotatey %f\n\t\trotate %f %f %f %f\n\t\ttranslate %f %f %f\n\t}\n\ttype cylinder\n}') % (sfShader, scalez, scaleu, 180*th/3.1415926, nx, ny, nz, 180-180*phi/3.1415926, center[0], center[1], center[2])


# kflow end

class pyKFlowPlugin:

	def __init__(self, app):

		self.dropShadow = Tkinter.BooleanVar()
		self.bgColor = '1 1 1'
		self.stageAngle = 10
		self.dofDist = -1
		self.varImageWidth = Tkinter.StringVar()

		# shader setting
		self.colorSpace = 'sRGB nonlinear'
		self.shaderSamples = 4
		self.phongSpec = 50
		self.shinyRefl = 0.5
		self.glassETA = 1.33

		# for selection speicific shader
		self.seleShaderDict = {}
		self.spColorShaderDict = {}

		self.parent = app.root
		self.dialog = Pmw.Dialog(self.parent,
							buttons = ('Render IPR',
										'Render Full',
										'Save SC',
										'Reset Default',
										'Exit'),
							title = 'pyKFlow -- Sunflow Plugin for Pymol',
							defaultbutton = 'Render IPR',
							command = self.execute)
		Pmw.setbusycursorattributes(self.dialog.component('hull'))
		
		w = Tkinter.Label(self.dialog.interior(),
                          text='PyMOL KFlow \nKejue Jia, 2015 - www.morphojourney.com',
                          #background='black',
                          background='#04092d',
                          foreground='#dbd1a1',
                          #pady = 20,
                          )
		w.pack(fill = 'both', expand=True, padx = 10, pady = 2)
		
		self.notebook = Pmw.NoteBook(self.dialog.interior())
		self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

######################################
######## main tab ####################
######################################

		tab_main = self.notebook.add(' Main ')
		self.notebook.tab(' Main ').focus_set()


		labelFrame_scene = Tkinter.LabelFrame(tab_main, text='Scene')
		labelFrame_scene.pack(fill='both', expand = True, padx = 10, pady = 5)
		#labelFrame_scene.grid()

		self.console = Tkinter.StringVar()
		self.console.set('%28s' % ('pykflow initialized'))
		self.label_img = Tkinter.Label(labelFrame_scene, textvariable=self.console, foreground='#08194d')
		#self.label_img = Tkinter.Label(labelFrame_scene, text='Option description --------')
		self.label_img.grid(sticky='w', row=0, column=0, padx=5, pady=3)
		# image width
		entryField_imageWidth = Pmw.EntryField(labelFrame_scene, 
									label_text='Image Width:', 
									labelpos='w', value='800', 
									entry_textvariable=self.varImageWidth)
		entryField_imageWidth.grid(sticky='w', row=0, column = 1, columnspan=2, padx =5 , pady=3)

		# floor switch / drop shadow checkbox 
		checkbox_dropShadow = Tkinter.Checkbutton(labelFrame_scene, text = 'Drop Shadow', variable = self.dropShadow)
		checkbox_dropShadow.select()
		checkbox_dropShadow.grid(sticky='w', row =2, column =1, columnspan=2, padx=5, pady=3)

		# background color selector
		label_bgColor = Tkinter.Label(labelFrame_scene, text='Background Color:')
		label_bgColor.grid(sticky='w', row=1, column=1, padx=5, pady=3)
		self.bt_bgColor = Tkinter.Button(labelFrame_scene, bg='white', command = self.setbgColor, width=12)
		self.bt_bgColor.grid(sticky='we',row=1, column=2, padx=5, pady=3)

		# scene angle (if drop shadow is set to true)
		label_stageAngle = Tkinter.Label(labelFrame_scene, text='Stage Angle:')
		label_stageAngle.grid(sticky='w', row=3, column=1, padx=5, pady=3)
		self.scale_stageAngle = Tkinter.Scale(labelFrame_scene, length= 80, 
							from_=10.0, to=90.0, resolution=1.0, orient = Tkinter.HORIZONTAL, 
							command = self.changeStageAngle)
		self.scale_stageAngle.set(10.0)
		self.scale_stageAngle.grid(sticky='we', row=3, column=2, padx=5, pady=3)

		# optionMenu for shader
		self.globalShader = Tkinter.StringVar()
		self.globalShader.set('diff')
#		self.optionMenu_shader = Pmw.OptionMenu(labelFrame_scene, labelpos='w', label_text='Molecule Shader:', menubutton_textvariable=self.globalShader, items=('Diff','Phong','Shiny','Glass','Mirror'), initialitem = 'Diff')
		self.optionMenu_shader = Pmw.OptionMenu(labelFrame_scene, labelpos='w', label_text='Molecule Shader:', menubutton_textvariable=self.globalShader, items=('diff','phong','shiny','glass','mirror'))
		self.optionMenu_shader.grid(sticky='we', row=4, column=1, columnspan=2, padx=5, pady=3)

		# optionMenu for ground shader
		self.bgShader = Tkinter.StringVar()
		self.bgShader.set('diff')
		self.optionMenu_bgShader = Pmw.OptionMenu(labelFrame_scene, labelpos='w', label_text='Background Shader:', menubutton_textvariable=self.bgShader, items=('diff','phong','shiny','glass', 'mirror'))
		self.optionMenu_bgShader.grid(sticky='we', row=5, column=1, columnspan=2, padx=5, pady=3)

		# scene angle (if drop shadow is set to true)
		label_dof = Tkinter.Label(labelFrame_scene, text='Depth of field:')
		label_dof.grid(sticky='w', row=6, column=1, padx=5, pady=3)
		self.scale_dof = Tkinter.Scale(labelFrame_scene, length= 80, 
							from_=-1.0, to=100.0, resolution=1.0, orient = Tkinter.HORIZONTAL, 
							command = self.changeDofDist)
		self.scale_dof.set(-1.0)
		self.scale_dof.grid(sticky='we', row=6, column=2, padx=5, pady=3)


######################################
######## shader tab ##################
######################################

		tab_shader = self.notebook.add(' Shaders Setting ')
		labelFrame_shader = Tkinter.LabelFrame(tab_shader, text='Setting')
		labelFrame_shader.pack(fill='both', expand = True, padx = 10, pady = 5)	

		self.shaderConsole = Tkinter.StringVar()
		self.shaderConsole.set('%24s' % ('Settings for general shaders\nAffect all the shaders in the scene'))
		self.label_shaderConsole = Tkinter.Label(labelFrame_shader, textvariable=self.shaderConsole, foreground='#08194d')
		self.label_shaderConsole.grid(sticky='w', row=0, column=0, padx=5, pady=3)


		# optionMenu for color space
		self.colorSpace = Tkinter.StringVar()
		self.colorSpace.set('sRGB linear')
		self.optionMenu_colorSpace = Pmw.OptionMenu(labelFrame_shader, labelpos='w', label_text='Color Space:', menubutton_textvariable=self.colorSpace, items=('sRGB linear','sRGB nonlinear','XYZ'))
		self.optionMenu_colorSpace.grid(sticky='we', row=0, column=1, columnspan=2, padx=5, pady=3)

		label_shaderSamples = Tkinter.Label(labelFrame_shader, text='Shader Samples:')
		label_shaderSamples.grid(sticky='w', row=1, column=1, padx=5, pady=3)
		self.scale_shaderSamples = Tkinter.Scale(labelFrame_shader, length= 80, 
							from_=4, to=64, resolution=4, orient = Tkinter.HORIZONTAL, 
							command = self.changeShaderSamples)
		self.scale_shaderSamples.set(4)
		self.scale_shaderSamples.grid(sticky='we', row=1, column=2, padx=5, pady=3)


		label_phongSpec = Tkinter.Label(labelFrame_shader, text='Phong Spec:')
		label_phongSpec.grid(sticky='w', row=2, column=1, padx=5, pady=3)
		self.scale_phongSpec = Tkinter.Scale(labelFrame_shader, length= 80, 
							from_=0, to=500, resolution=10, orient = Tkinter.HORIZONTAL, 
							command = self.changePhongSpec)
		self.scale_phongSpec.set(50)
		self.scale_phongSpec.grid(sticky='we', row=2, column=2, padx=5, pady=3)



		label_shinyRefl = Tkinter.Label(labelFrame_shader, text='Shiny Refl:')
		label_shinyRefl.grid(sticky='w', row=3, column=1, padx=5, pady=3)
		self.scale_shinyRefl = Tkinter.Scale(labelFrame_shader, length= 80, 
							from_=0.0, to=2.0, resolution=0.1, orient = Tkinter.HORIZONTAL, 
							command = self.changeShinyRefl)
		self.scale_shinyRefl.set(0.5)
		self.scale_shinyRefl.grid(sticky='we', row=3, column=2, padx=5, pady=3)


		label_glassETA = Tkinter.Label(labelFrame_shader, text='Glass eta:')
		label_glassETA.grid(sticky='w', row=4, column=1, padx=5, pady=3)
		self.scale_glassETA = Tkinter.Scale(labelFrame_shader, length= 80, 
							from_=0.0, to=3.0, resolution=0.1, orient = Tkinter.HORIZONTAL, 
							command = self.changeGlassETA)
		self.scale_glassETA.set(1.33)
		self.scale_glassETA.grid(sticky='we', row=4, column=2, padx=5, pady=3)


######################################
######## selection tab ###############
######################################

		tab_selection = self.notebook.add(' Selection Shaders ')
		labelFrame_selection = Tkinter.LabelFrame(tab_selection, text='Selection')
		labelFrame_selection.pack(fill='both', expand = True, padx = 10, pady = 5)		

		# output console textfield
		self.selectionConsole = Tkinter.StringVar()
		#self.selectionConsole.set('%28s' % ('Specify shader to PYMOL Selections'))
		self.selectionConsole.set('Specify shader to PYMOL Selections')
		self.label_selectionConsole = Tkinter.Label(labelFrame_selection, textvariable=self.selectionConsole, foreground='#08194d')
		self.label_selectionConsole.grid(sticky='w', row=0, column=0, padx=5, pady=30)

		# 
		self.varSelectionName = Tkinter.StringVar()
		entryField_selectionName = Pmw.EntryField(labelFrame_selection, 
									label_text='Sele Name:', 
									labelpos='w', value='', 
									entry_textvariable=self.varSelectionName)
		entryField_selectionName.grid(sticky='w', row=1, column = 0, padx =5 , pady=3)

		# dropdown for selection shader
		self.selectionShader = Tkinter.StringVar()
		self.selectionShader.set('diff')
		self.optionMenu_selectionShader = Pmw.OptionMenu(labelFrame_selection, labelpos='w', label_text='Available Shaders:', menubutton_textvariable=self.selectionShader, items=('diff','phong','shiny','glass', 'mirror'))
		self.optionMenu_selectionShader.grid(sticky='w', row=2, column=0, padx=5, pady=3)		

		label_separater = Tkinter.Label(labelFrame_selection, text='_______________________________', foreground='#909090')
		label_separater.grid(sticky='w', row=3, column=0, padx=5, pady=3)

		# apply button for shader selection
		button_selection = Tkinter.Button(labelFrame_selection, text = '  Apply  ', command = self.applyShader)
		button_selection.grid(sticky='w', row=4, column=0, padx=40, pady=15)		

		# apply button for shader selection
		button_unset = Tkinter.Button(labelFrame_selection, text = '  Unset all  ', command = self.unsetShader)
		button_unset.grid(sticky='e', row=4, column=0, padx=100, pady=15)		





		# important!
		self.notebook.setnaturalsize()

 # main window event dispatcher
	def execute(self, event):
		if event == 'Exit':
			self.quit()
		elif event == 'Render Full':
			self.render('')
		elif event == 'Render IPR':
			self.render('-ipr')
		elif event == 'Save SC':
			self.saveSC()
		elif event == 'Reset Default':
			self.resetScene()
			self.unsetShader()
		else:
			self.quit()

	# distroy main window
	def quit(self):
		self.dialog.destroy()

	# clean all the shader settings in (selection shader tab)
	def unsetShader(self):
 		self.selectionConsole.set('Unset all selection shaders')
 		self.seleShaderDict = {}
		self.spColorShaderDict = {}

	# selection shader tab
	# put sele: shader pair into seleShaderDict
	# action is taken when (save SC / render
	def applyShader(self):
		sele = self.varSelectionName.get()
		shader = self.optionMenu_selectionShader.getvalue()
		sess = cmd.get_session()['names']
		match_flag = False
		for i in sess:
			if type(i) is ListType:
				match = re.search(sele, i[0])
				#print 'sele: %s, i[0]: %s, match: %s' % (sele, i[0], repr(match))

				# exact word match
				# pattern s1, string: 1t3r
				# match == None
				if match is None:
					continue
				# when using regular expression like 's*'
				# match is always not None
				# match.group(0) == '' if not matching
				if match is not None: 
					#print repr(match.group(0))
					if match.group(0) == '':
						continue

				match_flag = True
				#if match.group(0):
				#if sele == i[0]:
				# user clicked apply for a selection more than once
				if i[0] in self.seleShaderDict:
					for key in self.spColorShaderDict:
						sele_in_dict = self.spColorShaderDict[key][1]
						if i[0] == sele_in_dict:
							self.selectionConsole.set('Shader for [%s] is not empty. \n Click [Unset all] if scene has been changed.' % i[0])
							return
								#self.spColorShaderDict.pop(key, 0)

				self.seleShaderDict[i[0]] = shader
	 			self.selectionConsole.set('Set [%s] with [%s] shader' % (sele, self.seleShaderDict[i[0]]))
	 			# add into dictionary
	 			self.sele2Color()

	 	if match_flag == False:
 			self.selectionConsole.set('Error: Selection [%s] does not exist.' % sele)


 	# transfer sele in seleShaderDict to color id
 	# sele -> color id
 	# return a dictionary with ['color': ('shader', 'sele')] information
 	def sele2Color(self):
 		globalShader = self.optionMenu_shader.getvalue()

 		# (color:shader) dictionary
 		# be used in shaderFactory.SCString()
 		#self.spColorShaderDict = {}
 		# get all the selection name
		sess = cmd.get_session()['names']
		for i in sess:
			if type(i) is ListType:
				# for each selection in the scene
				# also should exist in seleShaderDict
				if i[0] in self.seleShaderDict:
					newShader =  self.seleShaderDict[i[0]]
					if newShader != globalShader: # should be different from global shader, otherwise do nothing
						newColorInc = ShaderFactory.seleSlot[newShader]
						# pymol api routine
						# get the color for all the atoms in current selection
						stored.idcolor_list = []
						cmd.iterate(i[0], 'stored.idcolor_list.append((ID, int(color)))')

						# for a set of atoms have the same new color
						# apply color all at once for better performance
						# cmd.color is slow
						# example result: (color_index: [atom ids])
						# {25: [2, 3, 6], 6: [1], 9: [4, 5]}
						colorSetDict = {}
						for (atom_id, color) in stored.idcolor_list:
							colorSetDict.setdefault(color, []).append(str(atom_id))
						#print repr(colorSetDict)

						# for each color
						#for (atom_id, color) in stored.idcolor_list:
						for color in colorSetDict:
							atom_set = colorSetDict[color]
							rgb_color = cmd.get_color_tuple(color)
							#newColorInc = 0.001
							if rgb_color[2] >= 0.990:
								color_id = '%s %s %s' % (str(rgb_color[0])[0:5].ljust(5, '0'), str(rgb_color[1])[0:5].ljust(5, '0'), str(rgb_color[2]-newColorInc)[0:5])
							else:
								color_id = '%s %s %s' % (str(rgb_color[0])[0:5].ljust(5, '0'), str(rgb_color[1])[0:5].ljust(5, '0'), str(rgb_color[2]+newColorInc)[0:5])
							#print atom_id, color, color_id, repr(rgb_color)

							# color_id from all the sele:shader dictionary
							# determine color_id:shader pair
							if color_id not in self.spColorShaderDict:
								self.spColorShaderDict[color_id] = [newShader, i[0]]

							# apply new color to atom set
							newRGB = color_id.split(' ')
							newColor = [float(newRGB[0]), float(newRGB[1]), float(newRGB[2])]
							cmd.set_color(color_id, newColor)
							cmd.color(color_id, ('ID %s' % '+'.join(atom_set)))
						print 'apply shader [%s] to selection [%s].' % (newShader, i[0])


	# background color pickup event
	def setbgColor(self):
		try:
			colorTuple, color = tkColorChooser.askcolor()
			if colorTuple is not None and color is not None:
				self.bt_bgColor.config(bg=color)
				self.bgColor = '%f %f %f' % (colorTuple[0]/256.0, colorTuple[1]/256.0, colorTuple[2]/256.0)

		except Tkinter._tkinter.TclError:
			self.bgColor = '1.0 1.0 1.0'

	# slide phong spec
	def changePhongSpec(self, value):
		self.phongSpec = int(value)

	# slide phong samples
	def changeShaderSamples(self, value):
		self.shaderSamples = int(value)

	# slide shiny refl
	def changeShinyRefl(self, value):
		self.shinyRefl = float(value) 

	# slide glass eta
	def changeGlassETA(self, value):
		self.glassETA = float(value)

	# slide angle
	def changeStageAngle(self, value):
		self.stageAngle = int(value)


	def changeDofDist(self, value):
		self.dofDist = int(value)


	def getSunflow(self, destPath):
		'''
		get the path to kflow.jar and bring it to 
		'''
		filePath = tkFileDialog.askopenfilename(title = 'Please locate kflow.jar',
												initialdir = '',
												filetypes = [('all', '*')],
												parent = self.parent)
		if filePath:
			print 'copy kflow.jar into your HOME directory ...'
			shutil.copy(filePath, destPath)
		return

	def resetScene(self):
		self.varImageWidth.set('800')
		self.dropShadow.set(True)
		self.scale_stageAngle.set(10.0)
		self.changeStageAngle(10.0)
		self.globalShader.set('Diff')
		self.bgShader.set('Diff')
		self.console.set('%28s' % ('Scene reset.'))


	def saveSC(self):
		(pov_header, pov_body) = cmd.get_povray()
		self.p = pov()
		self.p.globalShaderFactory.seleShader = self.spColorShaderDict
		self.p.globalImage.setFloorColor(self.bgColor)
		self.p.globalImage.setFloorShader(self.optionMenu_bgShader.getvalue())
		self.p.globalImage.setGlobalShader(self.optionMenu_shader.getvalue())
		self.p.globalImage.setFloorShadow(self.dropShadow.get())
		self.p.globalImage.setOutputWidth(int(self.varImageWidth.get()))
		self.p.globalImage.setFloorAngle(self.stageAngle)		


		# shader settings
		self.p.globalShaderFactory.colorSpace = self.optionMenu_colorSpace.getvalue()
		self.p.globalShaderFactory.shaderSamples = self.shaderSamples
		self.p.globalShaderFactory.phongSpec = self.phongSpec
		self.p.globalShaderFactory.shinyRefl = self.shinyRefl
		self.p.globalShaderFactory.glassETA = self.glassETA


		if self.dofDist != -1:
			self.p.globalCamera.attr['type'] = 'thinlens'
			# will be used in p.parsePov
			# change fdist before p.camera writing SCString
			self.p.globalCamera.dofScale = self.dofDist 

		self.p.parsePov(''.join([pov_header, pov_body]))		
		self.console.set('%28s' % ('kflow.sc saved.'))



	def render(self, renderType):
		#cmd.do('save t.pov')
		#print 'image width: %d' % (int(self.varImageWidth.get()))
		#print 'drop shadow: %s' % self.dropShadow.get()
		#print 'bg color: %s' % (self.bgColor)
		#print 'stage angle: %d' % (self.stageAngle)
		#print 'molecule shader: %s' % self.optionMenu_shader.getvalue()
		#print 'background shader: %s' % self.optionMenu_bgShader.getvalue()
		try:
			os.unlink('kflow.sc')
			os.unlink('output.png')
		except:
			#traceback.print_exc()
			pass

		(pov_header, pov_body) = cmd.get_povray()
		self.p = pov()
		self.p.globalShaderFactory.seleShader = self.spColorShaderDict
		self.p.globalImage.setFloorColor(self.bgColor)
		self.p.globalImage.setFloorShader(self.optionMenu_bgShader.getvalue())
		self.p.globalImage.setGlobalShader(self.optionMenu_shader.getvalue())
		self.p.globalImage.setFloorShadow(self.dropShadow.get())


		# shader settings
		self.p.globalShaderFactory.colorSpace = self.optionMenu_colorSpace.getvalue()
		self.p.globalShaderFactory.shaderSamples = self.shaderSamples
		self.p.globalShaderFactory.phongSpec = self.phongSpec
		self.p.globalShaderFactory.shinyRefl = self.shinyRefl
		self.p.globalShaderFactory.glassETA = self.glassETA


		if renderType == '':	
			self.console.set('%28s' % ('Full Render'))
			self.p.globalImage.setOutputWidth(int(self.varImageWidth.get()))
		else:
			self.console.set('%28s' % ('Render IPR'))
			self.p.globalImage.setOutputWidth(800)
		self.p.globalImage.setFloorAngle(self.stageAngle)		
		if self.dofDist != -1:
			self.p.globalCamera.attr['type'] = 'thinlens'
			# will be used in p.parsePov
			# change fdist before p.camera writing SCString
			self.p.globalCamera.dofScale = self.dofDist 
		self.p.parsePov(''.join([pov_header, pov_body]))

		sunflowpath = os.path.expanduser('~')+'/kflow.jar'
		#print sunflowpath
		if os.path.isfile(sunflowpath) != True:
			self.getSunflow(sunflowpath)

		path_java='\"'+sunflowpath.replace('\\', '/')+'\"'

		cmd_args = '%s -v 0 -o output.png kflow.sc' % (renderType)
		print 'Start rendering ...'
		p=subprocess.Popen('java -jar '+path_java+' '+cmd_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			out = p.stdout.read(1)
			if out == '' and p.poll() != None:
				break
			if out!='':
				sys.stdout.write(out)
				sys.stdout.flush()
		

