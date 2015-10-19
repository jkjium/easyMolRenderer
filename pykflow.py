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
		self.notebook.pack(fill='both', expand=1, padx=10, pady=8)

		tab_main = self.notebook.add('Main')
		tab_main_group = Pmw.Group(tab_main, tag_text='Scene')
		tab_main_group.pack(fill='both', expand=1, padx=10, pady=5)



	def execute(self, event):
		if event == 'Exit':
			self.quit()


	def quit(self):
		self.dialog.destroy()

