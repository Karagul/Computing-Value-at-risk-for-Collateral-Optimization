import statistics as st
from scipy.stats import norm


# Calculates the most recent VaR value of a single asset.
def dailySingleParametricVar(retdata, confidence, windowsize):
    window = retdata['Returns'][-windowsize:]
    mean = st.mean(window)
    sd = st.pstdev(window)
    singleVaR = -norm.ppf(1-confidence/100, mean, sd) # Inv norm distribution of specified percentile, multiplied by -1
    return singleVaR

# Calculates multiple VaR values (ie for different dates) of a single asset.
def nondailySingleParametricVar(retdata, confidence, windowsize):
    VaRlist = []
    for index in range(windowsize-1, len(retdata)-1):
        window = retdata['Returns'][index:index+windowsize-1]
        mean = st.mean(window)
        sd = st.pstdev(window)
        singleVaR = -norm.ppf(1 - confidence / 100, mean, sd)
        VaRlist.append(singleVaR)

    retdata.drop(retdata.index[:windowsize], inplace=True)  # Drops the first row
    retdata['VaR'] = VaRlist
    return(retdata)

# Calculates the most recent VaR values of a multi asset.
def dailyMultiParametricVar(retdata, confidence, windowsize):
    VarList = []
    for asset in retdata:
        window = retdata[asset][-windowsize:]
        mean = st.mean(window)
        sd = st.pstdev(window)
        singleVaR = -norm.ppf(1-confidence/100, mean, sd) # Inv norm distribution of specified percentile, multiplied by -1
        VarList.append(singleVaR)
    return VarList




