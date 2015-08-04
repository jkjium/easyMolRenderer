from pymol import cmd
 
def make_pov(file):
	(header,data) = cmd.get_povray()
	povfile=open(file,'w')
	povfile.write(header)
	povfile.write(data)
	povfile.close()
