
import numpy as np
import Classes.aFarmer as farmer
import Classes.dCellClass as cell

# Declare number of rows and columns
nRows = 40
nCols = 40


# Load domain with stub cells


# Create a random array of either farmer or urban agents
ind = np.random.randint(3,size=(nRows,nCols))

AgentArray = np.empty((nRows,nCols),dtype='U10')

AgentArray[ind==0] = 'empty'
AgentArray[ind==1] = 'aFarmer'
AgentArray[ind==2] = 'aUrban'


for i in np.arange(nRows):
 	for j in np.arange(nCols):
		
 		if(AgentArray[i][j]=='aFarmer'):
 			NewAgent = farmer.aFarmer()
	 	elif(AgentArray[i][j]=='aUrban'):
	 		NewAgent = urban.aUrban()
	 		
 		dFASM[i][j].AddAgent(AgentArray[i][j],NewAgent)
