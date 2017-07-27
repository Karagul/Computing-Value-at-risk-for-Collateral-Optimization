import readData
import parametricVar
import historicalVaR
import monteCarloVaR
import numpy as np

x = readData.alternativeHistReturns(["CHRIS/ICE_B17.1", "CHRIS/ICE_B1.1"], 200, 5)
#x = readData.alternativeHistReturns("CHRIS/ICE_B17.1", 200, 2)
weights = [0.7, 0.3]

print("Cor matrix is: ")
cov = parametricVar.varCovarMatrix(x)
print(cov)

chel = monteCarloVaR.choleskyMatrix(cov)
print("Chel matrix is: ")
print(chel)
chelt = np.transpose(chel)
print("Chelt matrix is: ")
print(chelt)

result = np.dot(chel,chelt)
print("result matrix is: ")
print(result)

print("Cov matrix is: ")
cov = parametricVar.varCovarMatrix(x)
print(cov)

