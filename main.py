import readData
import parametricVar
import historicalVaR
import monteCarloVaR
import numpy as np

x = readData.alternativeHistReturns(["CHRIS/ICE_B17.1", "CHRIS/ICE_B1.1"], 200, 5)
#x = readData.alternativeHistReturns("CHRIS/ICE_B17.1", 200, 2)
weights = [0.7, 0.3]
mu = np.mean(x)
print(mu)
cov = parametricVar.varCovarMatrix(x)
print(cov)
test = monteCarloVaR.pythonNormRand(mu, cov, 1000)

list1 = []
list2 = []
for pair in test:
    list1.append(pair[0])
    list2.append(pair[1])
print("For list 1: ")
print(np.var(list1))
print(np.mean(list1))

print("For list 2: ")
print(np.var(list2))
print(np.mean(list2))

print(np.cov(list1, list2))