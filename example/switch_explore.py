import janus.crop_functions.crop_decider as crpdec
import matplotlib.pyplot as plt
import numpy as np

s1 = crpdec.switching_prob_curve(4.5, 1.0, 1, 1.5, 100, 1000) #swtiching averse
s2 = crpdec.switching_prob_curve(0.5, 3.0, 1, 1.5, 100, 1000) #will switch
s3 = crpdec.switching_prob_curve(2, 2, 1, 1.5, 100, 1000) #switching nuetral

fig = plt.figure()
ax = plt.axes()

ax.plot(s1[0], s1[1], label='switching averse')
ax.plot(s3[0], s3[1], label='switching neutral')
ax.plot(s2[0], s2[1], label='switching tolerant')

plt.legend()