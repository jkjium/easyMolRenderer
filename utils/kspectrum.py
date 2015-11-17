# output pymol scripts for spectrum a set of selections
class kspectrum:
	def __init__(self):
		self.input = ''
		self.colorSpace = 'HSL'
		self.HSLdict = {}
		self.HSLspan = 300.0 # from red to purple
		self.HSLlum = 0.7
		self.HSLsat = 1.0

		self.initHSL()

	# Given H,S,L in range of 0-360, 0-1, 0-1  Returns a Color
	def HSL2RGB(self, hue, sat, lum):
		# default to gray
		red = lum
		green = lum
		blue = lum
		if lum <= 0.5:
			v = lum * (1.0 + sat)
		else:
			v = lum + sat - lum * sat
		m = lum + lum - v
		sv = (v - m) / v
		hue = hue / 60.0
		sextant = int(hue)
		fract = hue - sextant
		vsf = v * sv * fract
		mid1 = m + vsf
		mid2 = v - vsf

		if v > 0:
			if sextant == 0:
				red = v
				green = mid1
				blue = m
			elif sextant == 1:
				red = mid2
				green = v
				blue = m
			elif sextant == 2:
				red = m
				green = v
				blue = mid1
			elif sextant == 3:
				red = m
				green = mid2
				blue = v
			elif sextant == 4:
				red = mid1
				green = m
				blue = v
			elif sextant == 5:
				red = v
				green = m
				blue = mid2

		return (red, green, blue)


	# initialize HSL color dictionary (2 - HSLspan)
	def initHSL(self):
		step = (self.HSLspan -1) / self.HSLspan 
		for i in xrange(2, int(self.HSLspan)+1):
			self.HSLdict[i] = self.HSL2RGB((i-1)*step, self.HSLsat, self.HSLlum)



	# read hcg file and output as pymol scripts
	# hcg format: 1oai_A.domain,HKLE,605 609 606 611
	def spectrumHCG(self, hcgfile):
		fin = open(hcgfile, 'r')
		lines = fin.readlines()
		fin.close()
		N = len(lines) # number of clusters / selections
		# make selections
		sel = ''
		for i in xrange(0,N):
			strArr = lines[i].strip().split(',')
			sel = '%sselect hcg%d, resi %s\n' % (sel, i, strArr[2].replace(' ', '+'))

		# set color	
		set_color = ''
		interval = int(self.HSLspan / N)
		hcgindex = 0
		for i in xrange(2, int(self.HSLspan)+1, interval):
			set_color = '%sset_color k%d=[%f,%f,%f]\ncolor k%d, hcg%d\n' % (set_color, i, self.HSLdict[i][0], self.HSLdict[i][1], self.HSLdict[i][2], i, hcgindex)
			hcgindex+=1

		if hcgindex < N:
			print 'HCG truncated at index: %d. N: %d' % (hcgindex, N)

		return '\n'.join([sel, set_color])

	# write pml file
	def writeSpectrumHCG(self, hcgfile):
		fo = open(hcgfile+'.pml', 'w')
		fo.write(self.spectrumHCG(hcgfile))
		fo.close()

