import math
import time
from itertools import groupby

from camera import Camera
from image import Image
from shaderFactory import ShaderFactory



# povray output paring class
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

		self.routine = {'camer':self.parseCamera, '#defa':self.parseDefault, 
				'mesh2':self.parseMesh2, 'spher':self.parseSphere, 'cylin':self.parseCylinder}

		self.globalSCString={'camera':[], '#default':[], 'light_source':[], 
						'plane':[], 'mesh2':[], 'sphere':[], 'cylinder':[]}


	# convert pov into sc file
	def parsePov(self, pov_str, scfile):
		print '\nStart parsing PovRay primitives ...'
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
					if count%1000==0:
						print str(count)+' primitives parsed ...'
		t2 = time.time()
		print '\nTime elapsed: %s seconds.' % (str(t2-t1))
		print '\nWriting SC information ... '

		# after get minmax z, before writing camera
		if self.globalCamera.attr['type'] == 'thinlens':
			# -1.0 * (min - max) since z is always negative
			self.globalCamera.attr['fdist'] = -1.0 * (self.globalCamera.dofScale * (self.globalImage.minz - self.globalImage.maxz)/90.0 + self.globalImage.maxz)



		fout=open(scfile,'w')
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

	# pov line iterator
	# cannot catch 'plane' and 'light_source'
	def povline(self, povfile):
		#titles=['camera', '#default', 'light_source', 'plane', 'mesh2', 'sphere', 'cylinder']
		#titles=['camer', '#defa', 'light', 'plane', 'mesh2', 'spher', 'cylin']
		fp = open(povfile)
		poviter = (x[1] for x in groupby(fp, lambda line: line[:5] in self.routine))
		for entry in poviter:
			name = entry.next()
			content = ''.join(s.strip() for s in poviter.next())
			yield '%s %s' % (name.strip(), content)

	# convert pov into sc file
	def parsePovFile(self, povfile, scfile):
		print '\nStart parsing PovRay primitives ...'

		t1 = time.time()
		count = 0
		for line in self.povline(povfile):
			#line = line.strip()
			if len(line)<2: continue
			for key in self.dispatch:
				if key in line[:11]:
					count+=1
					self.globalSCString[key].append(self.dispatch[''.join(key)](line))
					if count%1000==0:
						print str(count)+' primitives parsed ...'
		t2 = time.time()
		print '\nTime elapsed: %s seconds.' % (str(t2-t1))
		print '\nWriting SC information ... '

		# after get minmax z, before writing camera
		if self.globalCamera.attr['type'] == 'thinlens':
			# -1.0 * (min - max) since z is always negative
			self.globalCamera.attr['fdist'] = -1.0 * (self.globalCamera.dofScale * (self.globalImage.minz - self.globalImage.maxz)/90.0 + self.globalImage.maxz)



		fout=open(scfile,'w')
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
				#sfVectors=sfVectors+'\t\t'+point+'\n'
				sfVectors='%s\t\t%s\n' % (sfVectors, point)
				# for finding the lowest point
				self.checkLowestPoint(point.split(' '))

		endPoint = j
		# parse normals
		#sfNormals = '\tnormals none\n'
		sfNormals = '\tnormals vertex\n'
		normalIdx = entry[endPoint:N].find('normal_vectors')+endPoint
		for i in xrange(normalIdx+15, N): #normal_vectors { 3, <-0.8562379479,0.3649974763,0.3655590415>, <-0.8029828072,0.3864040971,0.4537735879>, <-0.8294824362,0.4455040097,0.3368754089>} 
			if entry[i]=='}': # sign for vertex_vectors section end
				break
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>':j+=1
				point = entry[i+1:j].replace(',', ' ')
				#sfNormals=sfNormals+'\t\t'+point+'\n'
				sfNormals='%s\t\t%s\n' % (sfNormals, point)
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
				#sfTriangle=sfTriangle+'\t\t'+faces+'\n'
				sfTriangle='%s\t\t%s\n' % (sfTriangle, faces)
				
		
		return ('object {\n\tshader %s\n\ttype generic-mesh\n%s%s%s\tuvs none\n}\n') % (sfShader, sfVectors, sfTriangle, sfNormals)		

	# sphere generator 
	# http://eugene-eeo.github.io/blog/sphere-triangles.html
	def _normalize(self, p):
		s = sum(u*u for u in p) ** 0.5
		return (p[0]/s, p[1]/s, p[2]/s)

	def _midpoint(self, u, v):
		return ((u[0]+v[0])/2, (u[1]+v[1])/2, (u[2]+v[2])/2)

	def _subdivide_edge(self, tri, depth):
		if depth == 0:
			yield tri
			return
		#       p0
		#      /  \
		# m01 /....\ m02
		#    / \  / \
		#   /___\/___\
		# p1    m12   p2
		p0, p1, p2 = tri
		m01 = self._normalize(self._midpoint(p0, p1))
		m02 = self._normalize(self._midpoint(p0, p2))
		m12 = self._normalize(self._midpoint(p1, p2))

		triangles = [
			(p0,  m01, m02),
			(m01, p1,  m12),
			(m02, m12, p2),
			(m01, m02, m12),
		]
		for t in triangles:
			for tsub in self._subdivide_edge(t, depth-1):
				yield tsub

	def _subdivide(self, faces, depth):
		for tri in faces:
			for trisub in self._subdivide_edge(tri, depth):
				yield trisub

	def _spheretri(self, shader, transform, n):
		depth = n
		# octahedron
		p = 2**0.5 / 2

		faces = [
			# top half
			((0, 1, 0), (-p, 0, p), ( p, 0, p)),
			((0, 1, 0), ( p, 0, p), ( p, 0,-p)),
			((0, 1, 0), ( p, 0,-p), (-p, 0,-p)),
			((0, 1, 0), (-p, 0,-p), (-p, 0, p)),

			# bottom half
			((0,-1, 0), ( p, 0, p), (-p, 0, p)),
			((0,-1, 0), ( p, 0,-p), ( p, 0, p)),
			((0,-1, 0), (-p, 0,-p), ( p, 0,-p)),
			((0,-1, 0), (-p, 0, p), (-p, 0,-p))
		]       

		outstr = []
		for i, t in enumerate(self._subdivide(faces, n)):
			outstr.append('\nobject {\n\tshader %s\n%s\ttype generic-mesh\n\tpoints 3\n\t\t%.8f %.8f %.8f\n\t\t%.8f %.8f %.8f\n\t\t%.8f %.8f %.8f\n\ttriangles 1\n\t\t0 1 2\n\tnormals vertex\n\t\t%.8f %.8f %.8f\n\t\t%.8f %.8f %.8f\n\t\t%.8f %.8f %.8f\n\tuvs none\n}' % \
					(shader, transform, t[0][0],t[0][1],t[0][2], t[1][0],t[1][1],t[1][2], t[2][0],t[2][1],t[2][2], \
					t[0][0],t[0][1],t[0][2], t[1][0],t[1][1],t[1][2], t[2][0],t[2][1],t[2][2]))
		return '\n'.join(outstr)

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
				color = entry[i+1:j].replace(',', ' ')
				sfShader = self.globalShaderFactory.assignShaderName(color)
				break

		#return ('\nobject {\n\tshader %s\n\ttype sphere\n\tc %s\n\tr %s\n}') % (sfShader, center, radius)		
		transform = '\ttransform {\n\t\tscaleu %s\n\t\ttranslate %s\n\t}\n' % (radius, center)
		return self._spheretri(sfShader, transform, 4)

	def _cylindertri(self, shader, transform, n):
		ins = 6.283184/n # 2*pi/n
		#r = 1 # default radius
		# generation points on the fly
		vertices=[]
		for i in xrange(0, n):
			vertices.append('\t\t%.4f %.4f %.4f' % (math.cos(i*ins), math.sin(i*ins),1))
			vertices.append('\t\t%.4f %.4f %.4f' % (math.cos(i*ins), math.sin(i*ins),-1))
		points = '\n'.join(vertices)
		#normals = points

		order =['\t\t%d %d %d' % (k, k+1, k+2) for k in xrange(0,2*n-2)]
		order.append('\t\t%d %d %d' % (2*n-2, 2*n-1,0))
		order.append('\t\t%d %d %d' % (2*n-1, 0, 1))
		
		return '\nobject {\n\tshader %s\n%s\n\ttype generic-mesh\n\tpoints %d\n%s\n\ttriangles %d\n%s\n\tnormals vertex\n%s\n\tuvs none\n}\n' % \
				(shader, transform, 2*n, points, 2*n, '\n'.join(order), points)

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
		endPoint = j
		sfShader = ''
		pigmentIdx = entry[endPoint:N].find('pigment')+endPoint
		for i in xrange(pigmentIdx, N):
			if entry[i]=='<':
				j=i+1
				while entry[j]!='>': j+=1
				color = entry[i+1:j].replace(',', ' ')
				#print color
				sfShader = self.globalShaderFactory.assignShaderName(color)
				break	

		pArray = p2.split(' ')
		a = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
		pArray = p1.split(' ')
		b = ( [float(pArray[0]),float(pArray[1]),float(pArray[2])] )
		d = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
		r = math.sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2])
		
		scaleu = float(radius) # scale rate from 1
		scalez = r/(2*scaleu) # should be 0.25 # scale rate after scale radius from 0.5
		
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
		#return ('\nobject {\n\tshader %s\n\ttransform {\n\t\tscale 1 1 %f\n\t\tscaleu %f\n\t\trotatey %f\n\t\trotate %f %f %f %f\n\t\ttranslate %f %f %f\n\t}\n\ttype cylinder\n}') % (sfShader, scalez, scaleu, 180*th/3.1415926, nx, ny, nz, 180-180*phi/3.1415926, center[0], center[1], center[2])
		transform = '\ttransform {\n\t\tscale 1 1 %f\n\t\tscaleu %f\n\t\trotatey %f\n\t\trotate %f %f %f %f\n\t\ttranslate %f %f %f\n\t}\n' % (scalez, scaleu, 180*th/3.1415926, nx, ny, nz, 180-180*phi/3.1415926, center[0], center[1], center[2])
		return self._cylindertri(sfShader, transform, 16)

