import sys


def translate_line(line, cuidict):

	results = []

	line_split = line.split(' ')
	for l in line_split:
		try:
			results.append(cuidict[l])
		except:
			results.append(l)

	return '; '.join(results)

def translate_file(infile, outfile, cuidict):
	
	contents = []

	with open(infile, 'r') as inf:
		with open(outfile, 'w') as outf:
			for line in inf:
				outf.write(translate_line(line, cuidict))

def translate_dict(cuidict):

	cui_dict = {}

	with open(cuidict, 'r') as f:
		for line in f:
			l_split = line.split()
			cui_dict[l_split[0]] = l_split[1]

	return cui_dict


# ###################################

if __name__ == '__main__':


	if len(sys.argv) > 3:

		infile = sys.argv[1]
		outfile = sys.argv[2]
		cuidict = sys.argv[3]

	else:
		print 'usage ./translate.py infile outfile cuidict'
		sys.exit()

	print 'getting dictionary'
	cui_dict = translate_dict(cuidict)
	translate_file(infile, outfile, cui_dict)

