
import numpy as np
import matplotlib.pyplot as plt
import CropDecider as cd

a_ra = 4.5
b_ra = 1.0

a_ea = 0.5
b_ea = 3.0

fmin = 1.0
fmax = 1.5
f0 = 1.2
n = 100
profit = 20000


N_ens = 1000

x_ra,fx_ra = cd.SwitchingProbCurve(a_ra,b_ra,fmin,fmax,n,profit)
x_ea,fx_ea = cd.SwitchingProbCurve(a_ea,b_ea,fmin,fmax,n,profit)

plt.figure(figsize=(11,8.5))
plt.rcParams.update({'font.size': 16})
plt.plot(x_ra-profit,fx_ra,label='Switching averse')
plt.plot(x_ea-profit,fx_ea,label='Switching tolerant')
plt.legend(loc='lower right')
plt.ylabel('Probability of Switching')
plt.xlabel('Expected Increase in Profit [$]')
plt.savefig('ProbSwitch.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')

ProfitMultipliers = np.array([0.05, 0.1, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65])

PercentSwitch_ra = np.zeros(ProfitMultipliers.shape)
PercentSwitch_ea = np.zeros(ProfitMultipliers.shape)

count = 0

for p_profit_mult in ProfitMultipliers:
    
    count_ra = 0.0
    count_ea = 0.0
    
    for i in np.arange(N_ens):
    
        count_ra += cd.Decide(a_ra,b_ra,fmin,fmax,n,profit,profit*(p_profit_mult+1))
        count_ea += cd.Decide(a_ea,b_ea,fmin,fmax,n,profit,profit*(p_profit_mult+1))
    
    
    PercentSwitch_ra[count] = count_ra / N_ens * 100.0
    PercentSwitch_ea[count] = count_ea / N_ens * 100.0    

    count += 1

x = np.arange(ProfitMultipliers.size)  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots(figsize=(11.5,8))
ax.bar(x - width/2, PercentSwitch_ra, width, label='Switching Averse')
ax.bar(x + width/2, PercentSwitch_ea, width, label='Switching Tolerant')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percent Switching')
ax.set_xticks(x)
ax.set_xticklabels(list(((ProfitMultipliers*100.0).astype('int')).astype('str')))
ax.set_xlabel('Anticipated Increase in Profit [%]')
ax.legend()

plt.savefig('PerCentSwitchVsProfitIncrease.png',dpi=300,facecolor='w', edgecolor='w', 
             bbox_inches='tight')
