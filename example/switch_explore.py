import janus.crop_functions.crop_decider as crpdec
import matplotlib.pyplot as plt
import numpy as np

s1 = crpdec.switching_prob_curve(4.5, 1.0, 1, 1.5, 100, 1000) #swtiching averse
s2 = crpdec.switching_prob_curve(0.5, 3.0, 1, 1.5, 100, 1000) #will switch
s3 = crpdec.switching_prob_curve(2, 2, 1, 1.5, 100, 1000) #switching nuetral
s5 = crpdec.switching_prob_curve(7, 1.5, 1, 1.5, 100, 1000) #aging nuetral
s4 = crpdec.switching_prob_curve(9.5, 0.5, 1, 1.5, 100, 1000) #aging averse

fig = plt.figure()
ax = plt.axes()

ax.plot(s1[0], s1[1], label='switching averse')
ax.plot(s3[0], s3[1], label='switching neutral')
ax.plot(s2[0], s2[1], label='switching tolerant')
ax.plot(s4[0], s4[1], label='aging averse')
ax.plot(s5[0], s5[1], label='aging neutral')

plt.legend()