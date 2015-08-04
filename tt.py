import sys
import StringIO
import time
import math
import subprocess

from camera import Camera
from image import Image
from shaderFactory import ShaderFactory
#camera {
#  type pinhole
#  eye    0.0 0.0 0.0
#  target 0.0 0.0 -89.6766
#  up     0.0 1.0 0.0
#  fov    45.0
#  aspect 1.3333333735
#}
# extract: eye, target, up, aspect
def parseCamera(entry): #camera {direction<0.0,0.0,  -2.835>  location <0.0 , 0.0 , 0.0>  right 1.3333333735*x up y   } 
	global globalCamera
	global globalImage

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
				globalCamera.upIndex = 0
				globalImage.attr['floor:n'] = '1 0 0'
			elif entry[i] == 'y':
				up = '0.0 1.0 0.0'
				globalCamera.upIndex = 1
				globalImage.attr['floor:n'] = '0 1 0'				
			else:
				up = '0.0 0.0 1.0'
				globalCamera.upIndex = 2
				globalImage.attr['floor:n'] = '0 0 1'				
			print 'globalCameraUpIndex: %d\n' % globalCamera.upIndex 
			break
	target = '\ttarget 0.0 0.0 -57.8435' # change later
	width = 1280
	height = width/float(aspect)
	globalImage.attr['resolution'] = '%d %d' % (width, height)
	
	globalCamera.attr['eye']=location
	globalCamera.attr['up'] = up
	globalCamera.attr['target']='0.0 0.0 -57.8435'
	globalCamera.attr['fov']='25.0'
	globalCamera.attr['aspect']=aspect
	
	#print globalImage.SCString()
	#print globalCamera.SCString()
	
	return globalImage.SCString()+globalCamera.SCString()

def parseDefault(entry):
	return ''
	
# light_source{<4000.0001,4000.0001,9786.1221>  rgb<1.0,1.0,1.0>}	
#light {
#	type point
#	color { "sRGB nonlinear" 1.000 1.000 1.000 }
#	power 100.0
#	p 1.0 3.0 6.0
#}
def parseLightSource(entry):
	#print 'parsing Light ...'
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

	
def parsePlane(entry):
	return ''

def parseMesh2(entry):
	global globalFloorMin
	global globalImage
	global globalShaderFactory

	N=len(entry)
	sfVectors = '\tpoints 3\n'
	
	transIdx = entry.find('transmit') #hard coded the space. 
	if transIdx!=-1:
		i=transIdx+len('transmit')
		while entry[i].isdigit()!=True: i+=1
		j=i
		while (entry[j].isdigit() or entry[j]=='.'): j+=1
		transmit = float(entry[i:j])*10.0
		#print 'transmit: %s' % entry[i:j]
	
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
			pArray = point.split(' ')
			height = float(pArray[globalCamera.upIndex])
			if height < globalFloorMin:
				globalFloorMin = height

			#print point
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
			#print point	
	# parse texture
	endPoint = j
	sfShader = ''
	pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
	for i in xrange(pigmentIdx+7,N): #texture_list { 3, texture { pigment{color rgb<0.00201,0.0000,1.0000> }} ,texture { pigment{color rgb<0.00201,0.0000,1.0000> }} ,texture { pigment{color rgb<0.00201,0.0000,1.0000> }} } 
		if entry[i]=='<':
			j=i+1
			while entry[j]!='>': j+=1
			color = entry[i+1:j].replace(',', ' ')
			#print color
			if transIdx!=-1:
				glassShader = ('glass%s' % color)
				#if glassShader in globalShaders:
				#	sfShader = globalShaderNames[glassShader]
				#else:
				#	shaderIdx = len(globalShaders)
					#shader {
					#	name sh.trans.00
					#	type glass
					#	eta 1.0
					#	color { "sRGB nonlinear" 0.800 0.800 0.800 }
					#	absorbtion.distance 5.0
					#	absorbtion.color { "sRGB nonlinear" 1.0 1.0 1.0 }
					#}
					#shader {
					#  name Glass.blue
					#  type glass
					#  eta 1.6
					#  color 1 1 5
					#}
					#globalShaders[glassShader]='shader {\n\tname sh.trans.%d\n\ttype glass\n\teta 1.5\n\tcolor  %s\n\tabsorbtion.distance %f\n}\n' % (shaderIdx, color,transmit)
					#globalShaderNames[glassShader]='shader sh.trans.%d\n' % shaderIdx
					#sfShader = globalShaderNames[glassShader]
			else:
				sfShader = globalShaderFactory.assignShaderName(color)
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
	
	#return 'object {\n\t'+sfShader+'\ttype generic-mesh\n'+sfVectors+sfTriangle+sfNormals+'\tuvs none\n}\n'
	return ('object {\n\tshader %s\n\ttype generic-mesh\n%s%s%s\tuvs none\n}\n') % (sfShader, sfVectors, sfTriangle, sfNormals)

#object {
#  shader Glass
#  type sphere
#  c 45 -30 21
#  r 20
#}
def parseSphere(entry): #sphere{<-2.9441969395,3.6968467236,-80.1707839966>, 1.2000000477 pigment{color rgb<1.0000,0.2824,0.0000>}}
	global globalFloorMin
	global globalShaderFactory
	N=len(entry)

	transIdx = entry.find('transmit') #hard coded the space. 
	if transIdx!=-1:
		i=transIdx+len('transmit')
		while entry[i].isdigit()!=True: i+=1
		j=i
		while (entry[j].isdigit() or entry[j]=='.'): j+=1
		transmit = float(entry[i:j])*10.0
		#print 'transmit: %s' % entry[i:j]
	
	# read center vector
	centerIdx = entry.find('<')
	for i in xrange(centerIdx,N):
		if entry[i]=='>':
			center = entry[centerIdx+1:i].replace(',',' ')
			# for finding the lowest point
			pArray = center.split(' ')
			height = float(pArray[globalCamera.upIndex])
			if height < globalFloorMin:
				globalFloorMin = height	
			
			#print center
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
			color = entry[i+1:j].replace(',', ' ')
			if transIdx!=-1:
				glassShader = ('glass%s' % color)
				#if glassShader in globalShaders:
				#	sfShader = globalShaderNames[glassShader]
				#else:
				#	shaderIdx = len(globalShaders)
					#shader {
					#	name sh.trans.00
					#	type glass
					#	eta 1.0
					#	color { "sRGB nonlinear" 0.800 0.800 0.800 }
					#	absorbtion.distance 5.0
					#	absorbtion.color { "sRGB nonlinear" 1.0 1.0 1.0 }
					#}
					#shader {
					#  name Glass.blue
					#  type glass
					#  eta 1.6
					#  color 1 1 5
					#}
					#globalShaders[glassShader]='shader {\n\tname sh.trans.%d\n\ttype glass\n\teta 3.3\n\tcolor  %s\n\tabsorbtion.distance %f\n}\n' % (shaderIdx, color,transmit)
					#globalShaderNames[glassShader]='shader sh.trans.%d\n' % shaderIdx
					#sfShader = globalShaderNames[glassShader]
			else:
				sfShader = globalShaderFactory.assignShaderName(color)
			break
	#return '\nobject {\n\t'+sfShader+'\n\ttype sphere\n\tc '+center+'\n\tr '+radius+'\n}'
	return ('\nobject {\n\tshader %s\n\ttype sphere\n\tc %s\n\tr %s\n}') % (sfShader, center, radius)

def parseCylinder(entry): #cylinder{<0.0390287824,-1.5336283445,-27.3909511566>, <0.0660662426,-1.1014350308,-27.9811739975>, 0.2500000000 open pigment{color rgb<0.20001,0.2000,1.0000>}}
	global globalShaderFactory
	N=len(entry)
	vertexIdx = entry.find('vertex_vectors')
	# parse vertex
	p1Idx = entry.find('<')
	for i in xrange(p1Idx,N):
		if entry[i]=='>':
			p1 = entry[p1Idx+1:i].replace(',',' ')
	#		print p1
			break
	endPoint = i	
	for i in xrange(endPoint, N):
		if entry[i]=='<':
			j=i+1
			while entry[j]!='>': j+=1
			p2 = entry[i+1:j].replace(',',' ')
	#		print p2
			break
	endPoint = j
	for i in xrange(endPoint, N):
		if entry[i].isdigit()==True:
			j=i+1
			while entry[j].isdigit() or entry[j]=='.': j+=1
			radius = entry[i:j]
	#		print radius
			break
	endPoiint = j
	sfShader = ''
	pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
	for i in xrange(pigmentIdx, N):
		if entry[i]=='<':
			j=i+1
			while entry[j]!='>': j+=1
			color = entry[i+1:j].replace(',', ' ')
			#print color
			sfShader = globalShaderFactory.assignShaderName(color)
			#if color in globalShaders:
			#	sfShader = globalShaderNames[color]
			#else:
			#	shaderIdx = len(globalShaders)
			#	globalShaders[color]='shader {\n\tname sh.%d\n\ttype diffuse\n\tdiff %s\n}\n' % (shaderIdx, color)
			#	globalShaderNames[color]= 'shader sh.%d\n' % shaderIdx
			#	sfShader = globalShaderNames[color]	
			break	
			
			#sfShader = globalShaderFactory.assignShaderName(color)
	#print sfShader

	# calculate rotations	
	#pArray = p2.split(' ')
	#a = np.array( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
	#pArray = p1.split(' ')
	#b = np.array( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )

	#d = a - b	# cylinder vector
	#r = np.linalg.norm(d)
	#print r
	pArray = p2.split(' ')
	a = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
	pArray = p1.split(' ')
	b = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
	d = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
	r = math.sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2])
	
	scaleu = float(radius)
	scalez = r/(2*scaleu) # should be 0.25	
	
	#center = (a+b)/2 # cylinder origin
	center = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)
	x=d[2]
	y=d[0]
	z=d[1]
	#print x, y, z

	phi = math.atan2(z, math.sqrt(x*x+y*y))
	th = math.atan2(y,x)
	#print th, phi
	
	# thCoor: the norm against which the cylinder should rotates after rotatey
	thCoor = th + 1.5708 # pi/2
	nz = math.cos(thCoor)
	nx = math.sin(thCoor)
	ny =0
	#print 180*th/3.1415926, nx, ny, nz, (180-180*phi/3.1415926)
	
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

	
globalSCString={'camera':[], '#default':[], 'light_source':[], 'plane':[], 'mesh2':[], 'sphere':[], 'cylinder':[]}

# need global keyword
globalCameraUpIndex = 0
globalFloorMin = float('inf')
#object {
#	shader sh.3
#	type plane
#	p 0 -11.475104 0
#	n 0 1 0
#}
globalFloorP = ''#'object {\n\tshader floor\n\ttype plane\n\t'

globalCamera = Camera()
globalImage = Image()
globalShaderFactory = ShaderFactory()

def main():
	global globalCamera
	global globalImage
	global globalShaderFactory
	
	if len(sys.argv)<3:
		print 'Usage: tt.py povFile bucket/ipr\n'
		return
	
	povFile = sys.argv[1]
	renderType = sys.argv[2]
	print povFile
	dispatch = {'camera':parseCamera, '#default':parseDefault, 'light_source':parseLightSource, 'plane':parsePlane, 'mesh2':parseMesh2, 'sphere':parseSphere, 'cylinder':parseCylinder}
	with open (povFile, "r") as povfile:
		pov=povfile.read().replace('\n', ' ').replace('\r', '')
	#print pov
	for key in dispatch.keys():
		pov=pov.replace(key,'\n'+key)

	buf = StringIO.StringIO(pov)
	povlines = buf.readlines()
	
	t1 = time.time()
	count = 0
	for line in povlines:
		line = line.strip()
		if len(line)<2: continue
		for key in dispatch.keys():
			if key in line[0:15]:
				count+=1
				globalSCString[key].append(dispatch[''.join(key)](line))
				if count%1000==0:
					print str(count)+' primitives parsed ...'
	t2 = time.time()
	print 'Done.'
	print 'Time used : '+ str(t2-t1) + ' seconds.\n'
	print 'Writing SC information ...'

	
	shaderFloor = 'shader {\n\tname floor\n\ttype diffuse\n\tdiff 1.0 1.0 1.0\n}\n'
	fout=open('output.sc','w')

	fout.write(''.join(globalSCString['camera']))
#	fout.write(''.join(globalSCString['light_source']))
	fout.write(globalShaderFactory.SCString('diff'))

	print 'Lowest point: [%f]' % (globalFloorMin)
	globalImage.attr['floor:p'][globalCamera.upIndex] = globalFloorMin-2
	print 'Adjusted lowest point: [%f]\n' % (globalFloorMin-2)
	fout.write(shaderFloor)
	fout.write(globalImage.floorSCString())
	
	fout.write(''.join(globalSCString['mesh2']))
	fout.write(''.join(globalSCString['sphere']))
	fout.write(''.join(globalSCString['cylinder']))
	fout.close()
	t3 = time.time()
	print 'Done.'
	print 'Time used : ' + str(t3-t2) + ' seconds.'
	
	print 'start rendering ...\n'
	#p = subprocess.Popen('java -jar renderer.jar '+renderType, shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#retval = p.wait()
	t4 = time.time()
	print 'Time used : ' + str(t4-t3) + ' seconds.'

if __name__=='__main__':
	main()
