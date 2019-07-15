
import numpy as np
import matplotlib.pyplot as plt
import CropDecider as cd

Nyears  = 20
Nmonths = 12

a_ra = 4.5
b_ra = 1.0

a_ea = 0.5
b_ea = 3.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100
profit = 20000

x_ra,fx_ra = cd.SwitchingProbCurve(a_ra,b_ra,fmin,fmax,n,profit)
x_ea,fx_ea = cd.SwitchingProbCurve(a_ea,b_ea,fmin,fmax,n,profit)

plt.figure(figsize=(11,8.5))
plt.plot(x_ra-profit,fx_ra,'b-',label='Switching averse')
plt.plot(x_ea-profit,fx_ea,'r-',label='Switching tolerant')
plt.legend(loc='lower right')
plt.ylabel('Probability of Switching')
plt.xlabel('Expected Profit [$]')

ProfitMultipliers = np.array([0.05, 0.1, 0.15, 0.25, 0.35, 0.45])



for p_profit_mult in p_profit_mult:
    
    count_ra = 0.0
    count_ea = 0.0
    
    for i in np.arange(1000):
    
    count_ea += cd.Decide(a_ea,b_ea,fmin,fmax,n,profit,profit*(p_profit_mult+1))
    count_ra += cd.Decide(a_ra,b_ra,fmin,fmax,n,profit,profit*(p_profit_mult+1))
    
    
# Read in prices paid


# Read in prices received




#for i in np.arange(Nyears):

#	for j in np.arange(Nmonths):




