'''
Main process for pymol kflow pov2sc
'''

import sys
import StringIO
import time
import math

from camera import Camera
from image import Image
from shaderFactory import ShaderFactory
from pov import pov
from config import config

def main():
	if len(sys.argv) < 4:
		print 'Usage: python pymolSC cfgfile povfile outSCfile'
		print 'java -jar kflow.jar [-ipr] -v 0 -o output.png outSCfilec'
		return
	cfgfile = sys.argv[1]
	povfile = sys.argv[2]
	outSCfile = sys.argv[3]
	print 'Reading povfile: %s' % povfile 
	# read pov file content as a big string
	with open (povfile, "r") as pf:
		povContent=pf.read()
	#print povContent

	# read config
	cfg = config(cfgfile)

	# init pov object
	p = pov()
	# set variables
	p.globalImage.setFloorColor(cfg.floorColor)
	p.globalImage.setFloorShader(cfg.floorShader)
	p.globalImage.setGlobalShader(cfg.globalShader)
	p.globalImage.setFloorShadow(cfg.floorShadow)
	p.globalImage.setOutputWidth(cfg.outputWidth)
	p.globalImage.setFloorAngle(cfg.floorAngle)		
	if cfg.dofDist != -1:
		p.globalCamera.attr['type'] = 'thinlens'
		# will be used in p.parsePov
		# change fdist before p.camera writing SCString
		p.globalCamera.dofScale = cfg.dofDist 

	p.parsePov(povContent, outSCfile)		
	print '%s saved.' % outSCfile

if __name__ == '__main__':
	main()