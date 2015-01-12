import sys
import scipy.io as sio

def check_line(line, cuimat):

	results = []

	line_split = line.split(' ')
	a = line_split[0]
	cui_int_a = int(a[1:])

	for l in line_split[1:]:
		
		try:
			cui_int_b = int(l[1:])
			results.append(str(cuimat[cui_int_a, cui_int_b]))
		except:
			results.append(l)

	return '; '.join(results)

def check_file(infile, outfile, cuimat):

	with open(infile, 'r') as inf:
		with open(outfile, 'w') as outf:
			for line in inf:
				outf.write(check_line(line, cuimat))

def get_prob(cuimat):
	# print type(cuimat)
	m = cuimat['M']
	# print type(m)
	return m * m.transpose()

# def translate_dict(cuidict):

# 	cui_dict = {}

# 	with open(cuidict, 'r') as f:
# 		for line in f:
# 			# line = line.rstrip()
# 			l_split = line.split('\t')
# 			cui_dict[l_split[0]] = l_split[1]

# 	# print cui_dict['C0424578']
# 	return cui_dict

# ###################################

if __name__ == '__main__':


	if len(sys.argv) > 3:

		infile = sys.argv[1]
		outfile = sys.argv[2]
		cuimat = sys.argv[3]

	else:
		print 'usage ./check_prob.py infile outfile cuimat'
		sys.exit()

	print 'getting matrix'
	# cui_mat = get_mat(cuimat)
	cui_mat = get_prob(sio.loadmat(cuimat))
	check_file(infile, outfile, cui_mat)

	# print 'getting dictionary'
	# cui_dict = translate_dict(cuidict)
	# translate_file(infile, outfile, cui_dict)