# This module contains all of the necessary functions for optimizing value-at-risk.
# Last Updated: 27/08
import monteCarloVaR
import  historicalVaR
import parametricVaR
import readData
import pandas as pd

def multiVaRMinimum(portfolios, weightsVector, varTechniqueVector, confidenceintervalVector, TVector, repVector):
    """This function calculates the minimum portfolio of a set of portfolios, each with their own VaR calculation
    technique. The lookback period is determined by the data itself. The index of each input corresponds to each
    portfolio. Historical Simulations do not require T (period of validity), therefore a 0 is put for their index in
    TVector. If the portfolio is not to be analysed using Monte Carlo repVector[portfolio] = 0 """
    vaRList = []
    for index in range(len(portfolios)):
        if varTechniqueVector[index] == "Parametric":
            VaR = parametricVaR.paraPortfolioVaR(portfolios[index], weightsVector[index],
                                                 confidenceintervalVector[index], TVector[index] )
        elif varTechniqueVector[index] == "Historical":
            VaR = historicalVaR.historicalPortfolioVaR(portfolios[index], confidenceintervalVector[index],
                                                       weightsVector[index])
        else: # varTechniqueVector[index] == "Monte Carlo"
            returnsList = monteCarloVaR.portfolioMonteCarlo2(portfolios[index], [0, TVector[index]], weightsVector[index],
                                                    repVector[index])
            VaR = historicalVaR.historicalSingleVaR(returnsList, confidenceintervalVector[index])

        vaRList.append(VaR)

    minIndex = vaRList.index(min(vaRList))
    print("Min portfolio is Portfolio: ")
    print(minIndex + 1)
    print("Min VaR value is: ")
    print(vaRList[minIndex])


def exchangeOptimize(portfolio, assetCodes, weightsVector, selectedAsset, varTechnique, T, reps):
    """For a specified derivative, this function searches the WikiFutures list to see if it is listed on another exchange
    which is already being traded on in the portfolio. If it is, then the CVaR of the original portfolio is calculated
    and added, and the CVaR of the new portfolio (where the asset is switched) is calculated and added.
    If the new CVaR is lower, the function returns the exchange with which the new asset is allocated to."""
    df = readData.readWikiFutures("wikifutures.csv")

    # Get a list of exchanges in portfolio. Construct a dictionary of assets and weights for each exchange
    exchangeList = []
    exchangeAssetDict = {}
    exchangeWeightDict = {}
    exchangeIndex = {}
    for index in range(len(assetCodes)):
        exchange = df.loc[df['Quandl Code'] == assetCodes[index], 'Exchange'].item()
        if exchange not in exchangeList:
            exchangeList.append(exchange)
            exchangeAssetDict[exchange] = [assetCodes[index]]
            exchangeWeightDict[exchange] = [weightsVector[index]]
            exchangeIndex[exchange] = [index]
        else:
            exchangeAssetDict[exchange].append(assetCodes[index])
            exchangeWeightDict[exchange].append(weightsVector[index])
            exchangeIndex[exchange].append(index)

    #Calculate the CVaR by summing the CVaR of each exchanges' portfolio
    cVaRList = []
    exchangesPortfoliosDict = {}
    for exchange in exchangeList:
        exchangePortfolio1 = portfolio.drop(portfolio.columns[exchangeIndex[exchange]],axis=1)
        exchangePortfolio2 = exchangePortfolio1.tail(df.loc[df['Quandl Code'] == exchangeAssetDict[exchange][0],
                                                            'Lookback'].item()) # Cut down to lookback
        exchangesPortfoliosDict[exchange] = exchangePortfolio2.copy(deep = True)

        exchangeWeights = exchangeWeightDict[exchange]
        exchangeConfidence = df.loc[df['Quandl Code'] == exchangeAssetDict[exchange][0], 'Confidence'].item()

        if varTechnique == "Parametric":
            CVaR = parametricVaR.paraPortfolioCVaR(exchangePortfolio2, exchangeWeights, exchangeConfidence, T)
        elif varTechnique == "Historical":
            CVaR = historicalVaR.historicalPortfolioVaR(exchangePortfolio2, exchangeConfidence, exchangeWeights)
        else: # varTechnique == "Monte Carlo"
            returnsList = monteCarloVaR.portfolioMonteCarlo2(exchangePortfolio2, reps, [0,T], exchangeWeights)
            CVaR = historicalVaR.historicalSingleVaR(returnsList, exchangeConfidence)

        cVaRList.append(CVaR)

    cVaRTotal = 0
    for CVaR in cVaRList:
        cVaRTotal += CVaR

    print("Current CVaR with asset " + selectedAsset + " is " + str(cVaRTotal) + ".")

    newCVaRTotal = cVaRTotal
    newCode = 0

    #Get name of asset and calculate the CVaR
    selectedName = df.loc[df['Quandl Code'] == selectedAsset, 'Name'].item()
    for index, row in df.iterrows():
        exchange = row["Exchange"]
        selectedAssetsExchange = df.loc[df['Quandl Code'] == selectedAsset, 'Exchange'].item()

        if row["Name"] == selectedName and row["Exchange"] in exchangeList and row["Exchange"] is not selectedAssetsExchange:
           subPortfolioCopy1 = (exchangesPortfoliosDict[exchange]).copy(deep=True)
           subWeightVectorCopy = list(exchangeWeightDict[exchange])
           rowCode = row["Quandl Code"]
           if rowCode not in assetCodes:
               singlePortfoliodirty = readData.readQuandl([str(rowCode) + ".1"], 1000, True)
               singlePortfolio2 = readData.cleanData(singlePortfoliodirty)
               singlePortfolio = singlePortfolio2.tail(df.loc[df['Quandl Code'] == exchangeAssetDict[exchange][0], 'Lookback'].item())

               # MAKE TEMP OF selectAsset's portfolio
               tempSelectedAssetPortfolio = exchangesPortfoliosDict[selectedAssetsExchange].copy(deep = True)
               tempSelectedAssetsWeightsList = list(exchangeWeightDict[selectedAssetsExchange])
               selectedAssetsIndex = 0
               newAssetsIndex = 0

               # Get the index of the selected assets exchange, to be used to remove the weight and portfolio values
               for index in range(len(exchangeAssetDict[selectedAssetsExchange])):
                   if exchangeAssetDict[selectedAssetsExchange][index] == selectedAsset:
                       selectedAssetsIndex = index

               # Get the index of the new assets exchange
               for index in range(len(exchangeAssetDict[exchange])):
                   if exchangeAssetDict[exchange][index] == rowCode:
                       newAssetsIndex = index

               tempSelectedAssetPortfolio.drop(tempSelectedAssetPortfolio.columns[selectedAssetsIndex], axis=1, inplace=True)
               tempWeight = tempSelectedAssetsWeightsList.pop(selectedAssetsIndex)

               # Add the new asset to the corresponding exchanges dataframe and the weight vector
               subWeightVectorCopy.append(tempWeight)
               subPortfolioCopy = (subPortfolioCopy1.join(singlePortfolio)).copy(deep = True)

               # recalculate the CVaR intermediateCVaRTotal
               cVaRRemainder = cVaRTotal - cVaRList[selectedAssetsIndex] - cVaRList[newAssetsIndex]

               newExchangeConfidence = df.loc[df['Quandl Code'] == exchangeAssetDict[exchange][0], 'Confidence'].item()
               oldexchangeConfidence = df.loc[df['Quandl Code'] == exchangeAssetDict[selectedAssetsExchange][0], 'Confidence'].item()

               # Get CVaR of selected Asset

               if varTechnique == "Parametric":
                   CVaRSelectedAsset = parametricVaR.paraPortfolioCVaR(tempSelectedAssetPortfolio, tempSelectedAssetsWeightsList, oldexchangeConfidence, T)
               elif varTechnique == "Historical":
                   CVaRSelectedAsset = historicalVaR.historicalPortfolioVaR(tempSelectedAssetPortfolio, oldexchangeConfidence, tempSelectedAssetsWeightsList)
               else:  # varTechnique == "Monte Carlo"
                   returnsList = monteCarloVaR.portfolioMonteCarlo2(tempSelectedAssetPortfolio, reps, [0, T], tempSelectedAssetsWeightsList)
                   CVaRSelectedAsset = historicalVaR.historicalSingleVaR(returnsList, oldexchangeConfidence)

               # Get CVaR of new asset
               if varTechnique == "Parametric":
                   CVaRNewAsset = parametricVaR.paraPortfolioCVaR(subPortfolioCopy,
                                                                  subWeightVectorCopy,
                                                                  newExchangeConfidence, T)
               elif varTechnique == "Historical":
                   CVaRNewAsset = historicalVaR.historicalPortfolioVaR(subPortfolioCopy,
                                                                       newExchangeConfidence,
                                                                       subWeightVectorCopy)
               else:  # varTechnique == "Monte Carlo"
                   returnsList = monteCarloVaR.portfolioMonteCarlo2(subPortfolioCopy, reps, [0, T],
                                                                    subWeightVectorCopy)
                   CVaRNewAsset = historicalVaR.historicalSingleVaR(returnsList, newExchangeConfidence)

               tempCVaRTotal = CVaRNewAsset + CVaRSelectedAsset + cVaRRemainder

               if tempCVaRTotal < cVaRTotal:
                   newCVaRTotal = tempCVaRTotal
                   newCode = row["Quandl Code"]

    if newCode == 0:
        print("No matching assets were found in other exchanges.")
    elif newCode == selectedAsset:
        print("CVaR cannot be minimized by switching this asset.")
    else:
        print("CVaR can be minimized by switching with asset " + newCode + ". New CVaR is " + str(newCVaRTotal) +".")


def optimizeSimilarAssets(portfolio, assetCodes, weightsVector, selectedAsset,
                          alternativeAssets, varTechnique, T, reps, confidence):
    """ Out of a list of alternative assets for a selected asset, this function is able to suggest an alternative asset for
    which the overall portfolio VaR is minimized. For maximum realism, the portfolio must be at a single exchange,
    as all VaR is calculated used the same method, lookback, and confidence."""

    # Calculate the current VaR

    if varTechnique == "Parametric":
        currentVaR = parametricVaR.paraPortfolioVaR(portfolio, weightsVector, confidence, T)
    elif varTechnique == "Historical":
        currentVaR = historicalVaR.historicalPortfolioVaR(portfolio, confidence, weightsVector)
    else:  # varTechniqueVector[index] == "Monte Carlo"
        returnsList = monteCarloVaR.portfolioMonteCarlo2(portfolio, [0, T], weightsVector, reps)
        currentVaR = historicalVaR.historicalSingleVaR(returnsList, confidence)

    # Identify index of selected asset in weightsVector

    selectedAssetIndex = 0
    for index in range(len(assetCodes)):
        if assetCodes[index] == selectedAsset:
            selectedAssetIndex = index

    # Pop the selected asset and weight. Append selected weight to the end of the weight vector

    selectedWeight = weightsVector.pop(selectedAssetIndex)
    weightsVector.append(selectedWeight)
    portfolio.drop(portfolio.columns[selectedAssetIndex], axis=1, inplace=True)

    # For each alternativeAsset, read the asset data and append selected asset portfolio and weight to the end.
    # Find the length of the original dataset

    lengthOriginal = len(portfolio)
    minVaR = currentVaR
    print("Original VaR is " + str(minVaR))
    minAsset = selectedAsset

    for alternativeAsset in alternativeAssets:
        singlePortfoliodirty = readData.readQuandl([alternativeAsset], lengthOriginal * 2, True)
        singlePortfolio2 = readData.cleanData(singlePortfoliodirty)
        singlePortfolio = (singlePortfolio2.tail(lengthOriginal)).copy(deep = True)

        subPortfolioDirtyCopy = (portfolio.join(singlePortfolio)).copy(deep=True)
        subPortfolioCopy = readData.cleanData(subPortfolioDirtyCopy).copy(deep = True)

        print(subPortfolioCopy)
        print(weightsVector)

        # Recalculate the VaR, if lower then replace the min VaR with new VaR and new asset

        if varTechnique == "Parametric":
            newVaR = parametricVaR.paraPortfolioVaR(subPortfolioCopy, weightsVector, confidence, T)
        elif varTechnique == "Historical":
            newVaR = historicalVaR.historicalPortfolioVaR(subPortfolioCopy, confidence, weightsVector)
        else:  # varTechniqueVector[index] == "Monte Carlo"
            returnsList = monteCarloVaR.portfolioMonteCarlo2(subPortfolioCopy, [0, T], weightsVector, reps)
            newVaR = historicalVaR.historicalSingleVaR(returnsList, confidence)

        if newVaR < minVaR:
            minVaR = newVaR
            minAsset = alternativeAsset

    # Print out results
    if minAsset == selectedAsset:
        print("VaR cannot be minimized by switching to an alternative asset.")
    else:
        print("VaR can be minimized by switching with asset " + minAsset + ". New VaR is " + str(minVaR) +".")


