import numpy as np
import matplotlib.pyplot as plt

filename = "../result8/result_out.20.R"
R = np.loadtxt(filename)

R_flat = R.flatten()
R_sort = sorted(R_flat)
print np.argsort(R_flat)
plt.plot(R_sort)
plt.show()
#print sorted(R, key=lambda row: row[1])
