import matplotlib.pyplot as plt
import numpy as np



spread = np.random.rand(50) * 100
center = np.ones(25) * 50
flier_high = np.random.rand(10) * 100 + 100
flier_low = np.random.rand(10) * -100
data = np.concatenate((spread, center, flier_high, flier_low),0)

mpl_fig = plt.figure()
ax = mpl_fig.add_subplot(111)

ax.boxplot(data)

ax.set_xlabel('Data Points')
ax.set_ylabel('Variance')

plt.show()
