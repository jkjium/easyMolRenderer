from camera import Camera
from image import Image
from shaderFactory import ShaderFactory
sf = ShaderFactory()
color = '0.2 0.2 0.8'
sn = sf.assignShaderName(color)
print sn
color = '0.5 0.5 0.8'
sn = sf.assignShaderName(color)
print sn
print sf.SCString()
#c=Camera()
#print c.SCString()
#img = Image()
#print img.SCString()
#print img.attr['floor:p'][1]