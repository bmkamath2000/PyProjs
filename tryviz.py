import matplotlib.pyplot as plt
import numpy as np
xvalues = np.array([0,100])
yvalues = np.array([0,200])
yvalues = np.sin(xvalues)
plt.plot(xvalues,yvalues)
plt.show()
ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, marker = 'o')
plt.show()