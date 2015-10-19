import warnings
import os 
import Tkinter
import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import Pmw
import tkColorChooser
from pymol.cgo import *


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
		w.pack(expand = 1, fill = 'both', padx = 10, pady = 2)

		self.notebook = Pmw.NoteBook(self.dialog.interior())
		self.notebook.pack(fill='both', expand=1, padx=10, pady=5)

		tab_main = self.notebook.add('Main')
		self.notebook.tab('Main').focus_set()
		labelFrame_scene = Tkinter.LabelFrame(tab_main, text='Scene')
		labelFrame_scene.pack(fill='both', expand = True, padx = 10, pady = 5)

		# image width
		entryField_imageWidth = Pmw.EntryField(labelFrame_scene, 
									label_text='Image Width:', 
									labelpos='ws', value='2560', 
									entry_textvariable=self.varImageWidth)
		entryField_imageWidth.grid(sticky='w', row=0, column = 1, columnspan=2, padx =5 , pady=5)

		# floor switch / drop shadow checkbox 
		checkbox_dropShadow = Tkinter.Checkbutton(labelFrame_scene, text = 'Drop Shadow', variable = self.dropShadow)
		checkbox_dropShadow.select()
		checkbox_dropShadow.grid(sticky = 'e', row =1, column =1, padx=3, pady=5)

		# background color selector
		label_bgColor = Tkinter.Label(labelFrame_scene, text='Background Color:')
		label_bgColor.grid(sticky='e', row=2, column=1)
		self.bt_bgColor = Tkinter.Button(labelFrame_scene, bg='white', command = self.setbgColor, width=12)
		self.bt_bgColor.grid(sticky='w', row=2, column=2, padx=0, pady=0)

		# scene angle (if drop shadow is set to true)
		label_stageAngle = Tkinter.Label(labelFrame_scene, text='Stage Angle:')
		label_stageAngle.grid(sticky='e', row=3, column=1, padx=5, pady=3)
		self.scale_stageAngle = Tkinter.Scale(labelFrame_scene, from_=10.0, to=90.0, resolution=1.0, orient = Tkinter.HORIZONTAL, command = self.changeStageAngle)
		self.scale_stageAngle.set(10.0)
		self.scale_stageAngle.grid(sticky='e', row=3, column=2, padx=5, pady=3)

		print self.varImageWidth.get()


	# main window event dispatcher
	def execute(self, event):
		if event == 'Exit':
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

		except Tkinter._tkinter.TclError:
			self.bgColor = [1,1,1]		

	def changeStageAngle(self, value):
		self.stageAngle = int(value)


