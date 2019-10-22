from image import Image
from pov import pov
img = Image()

print img.attr['bg_color']
print img.attr['floor:color']
print img.attr['floor:shader']
print img.attr['globalShader']

#c=Camera()
#print c.SCString()
#img = Image()
#print img.SCString()
#print img.attr['floor:p'][1]
dispatch = {'camera':1, '#default':1, 'light_source':1, 'plane':1, 'mesh2':1, 'sphere':1, 'cylinder':1}

with open ('t.pov', "r") as pf:
	pov_str=pf.read()

pov_str=pov_str.replace('\n',' ').replace('\r','')
for key in dispatch.keys():
	pov_str = pov_str.replace(key, '\n'+key)

with open('t.out','w') as fout:
    fout.write(pov_str)

#buf = StringIO.StringIO(pov_str)
#povlines = buf.readlines()