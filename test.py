from userInterface import UserInterface
from image import Image
img = Image()
ui = UserInterface(img, 0)

print img.attr['bg_color']
print img.attr['floor:color']
print img.attr['floor:shader']
print img.attr['globalShader']


#c=Camera()
#print c.SCString()
#img = Image()
#print img.SCString()
#print img.attr['floor:p'][1]