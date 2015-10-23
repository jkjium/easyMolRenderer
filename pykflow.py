import warnings
import os 
import subprocess
import Tkinter
import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import Pmw
import tkColorChooser
from pymol import cmd


try:
	from pymol import *
	havePymol = True
except ImportError:
	havePymol = False
	warnings.warn("Failed to load module pymol, functions might be incomplete")


def __init__(self):
    
	self.menuBar.addmenuitem('Plugin','command','pykflow',label = 'pyKFlow', command = lambda s = self : pyKFlowPlugin(s))    


class pyKFlowPlugin:

	def __init__(self, app):

		self.dropShadow = Tkinter.BooleanVar()
		self.bgColor = [1,1,1]
		self.stageAngle = 10
		self.varImageWidth = Tkinter.StringVar()

		self.parent = app.root
		self.dialog = Pmw.Dialog(self.parent,
							buttons = ('Render IPR',
										'Render',
										'Reset',
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
		self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

		tab_main = self.notebook.add('Main')
		self.notebook.tab('Main').focus_set()
		labelFrame_scene = Tkinter.LabelFrame(tab_main, text='Scene')
		labelFrame_scene.pack(fill='both', expand = True, padx = 10, pady = 5)
		#labelFrame_scene.grid()

		self.label_img = Tkinter.Label(labelFrame_scene, text='Option description --------')
		self.label_img.grid(sticky='w', row=0, column=0, padx=5, pady=3)
		# image width
		entryField_imageWidth = Pmw.EntryField(labelFrame_scene, 
									label_text='Image Width:', 
									labelpos='w', value='2560', 
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
		self.optionMenu_shader = Pmw.OptionMenu(labelFrame_scene, labelpos='w', label_text='Molecule Shader:', items=('Diff','Phong','Shiny','Glass'), initialitem = 'Diff')
		self.optionMenu_shader.grid(sticky='we', row=4, column=1, columnspan=2, padx=5, pady=3)

		# optionMenu for ground shader
		self.optionMenu_bgShader = Pmw.OptionMenu(labelFrame_scene, labelpos='w', label_text='Background Shader:', items=('Diff','Phong','Shiny','Glass'), initialitem = 'Diff')
		self.optionMenu_bgShader.grid(sticky='we', row=5, column=1, columnspan=2, padx=5, pady=3)


 # main window event dispatcher
	def execute(self, event):
		if event == 'Exit':
			self.quit()
		elif event == 'Render':
			self.render()
		else:
			self.quit()

	# distroy main window
	def quit(self):
		self.dialog.destroy()


	# background color pickup event
	def setbgColor(self):
		try:
			colorTuple, color = tkColorChooser.askcolor()
			if colorTuple is not None and color is not None:
				self.bt_bgColor.config(bg=color)
				self.bgColor = color

		except Tkinter._tkinter.TclError:
			self.bgColor = [1,1,1]		

	def changeStageAngle(self, value):
		self.stageAngle = int(value)


	def render(self):
		#cmd.do('save t.pov')
		#if self.ImageWidth.get() == '' :

		print 'image width: %d' % (int(self.varImageWidth.get()))
		print 'drop shadow: %s' % self.dropShadow.get()
		print 'bg color: %s' % (str(self.bgColor))
		print 'stage angle: %d' % (self.stageAngle)
		print 'molecule shader: %s' % self.optionMenu_shader.getvalue()
		print 'background shader: %s' % self.optionMenu_bgShader.getvalue()

		(pov_header, pov_body) = cmd.get_povray()
		pov_str = ''.join([pov_header, pov_body]).replace('\n', ' ').replace('\r', '')

		print pov_str

		# cmd="java -jar kflow.jar -v 0 -o out.png output.sc" 
		path=os.path.dirname(__file__)+'/kflow.jar'
		path_java=path.replace(' ', '\" \"')
		path_java='\"'+path.replace('\\', '/')+'\"'

		print os.path.isfile(path)
		#path='kflow.jar'
		print os.path.isfile(path_java)

		cmd_args = '-v 3 -o output.png output.sc' 
		print 'start rendering ...'
		#path_java = '\"C:/Users/kjia/workspace/python/easyMolRenderer/sunflow/kflow.jar\"'
		#path_java = '\"C:/Users/kjia/kflow.jar\"'
		print path_java
		#path_jave = 'kflow.jar'
		'''p=subprocess.Popen('java -jar '+path_java+' '+cmd_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		#p=subprocess.Popen('java -jar '+path+' '+cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			out = p.stdout.read(1)
			if out == '' and p.poll() != None:
				break
			if out!='':
				sys.stdout.write(out)
				sys.stdout.flush()'''
