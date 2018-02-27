# Last Updated: 05/07. This module contains functions whjch allow the use to enter a portfolio and to preprocess
# time series data.

import quandl
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day

# Allows more than 50 data requests per day from Quandl
quandl.ApiConfig.api_key = ""

def readQuandl(derivativelist, lookback, returns):
    """Reads time series and obtains daily returns if desired for specified derivatives on Quandl """
    today = pd.datetime.today()
    start = today - BDay(lookback)
    if returns == True:
        mydata = quandl.get(derivativelist, start_date = start, end_date = today,
                            transformation = 'rdiff', rows = lookback)
    else: mydata = quandl.get(derivativelist, start_date = start, end_date = today, rows = lookback)
    return mydata


def cleanData(mydata):
    """# Zero's are assumed to be missing values, and are replaced with NaN. Missing data is filled in using linear
    interpolation for all columns. NaN at the start and end of a column are replaced with ~ 0 """
    mydata2 = mydata.replace(0, np.NaN)
    if mydata2.isnull().values.any():
        print("Dataset Contains NA or 0 values")
        mydata3 = mydata2.interpolate()
        mydata3 = mydata3.fillna(0.000000001)
        return mydata3
    else:
        return mydata2

def cleanOpen(mydata):
    """Missing data is filled in using linear interpolation 'Open' only. """
    if mydata['Open'].isnull().values.any():
        print("Open Contains NA values")
        mydata['Open'] = mydata['Open'].interpolate()
    return mydata

def tick2ret(series):
    """Converts series of prices to one of returns. CURRENTLY NOT REQUIRED AS get.quandl DOES THIS FOR US """
    retdata = pd.DataFrame(series['Open'])
    prices = series['Open']
    retlist = []

    index = 1
    while index < len(prices):
        ret = (prices[index]-prices[index-1])/prices[index-1]
        retlist.append(ret)
        index += 1

    retdata.drop(retdata.index[:1], inplace=True) # Drops the first row
    retdata['Returns'] = retlist
    return retdata

def portfolioWeights():
    """Obtains portfolio weights as an input from the user. """
    weights = [float(x) for x in input("Enter a list of weights which sum to 1, separated by spaces: ").split()]
    return weights

def alternativeHistReturns(derivativelist, lookback, T):
    """Obtains returns for specified T day intervals (not T=1), since Quandl only calculates returns for T=1. Useful
    for historical simulations. """
    rawdata = readQuandl(derivativelist, lookback+T, False)
    cleanrawdata = cleanData(rawdata)
    for derivative in cleanrawdata:
        index = len(cleanrawdata)-1
        while index >= T and index > 0:
            indexedreturn = cleanrawdata[derivative][index]/cleanrawdata[derivative][index-T] - 1
            cleanrawdata[derivative][index] = indexedreturn
            index = index - 1
    cleanrawdata.drop(cleanrawdata.index[:T], inplace=True)  # Drops the first T rows
    return cleanrawdata


def commodityData(csvfilename):
    """This function obtains all clean commodity returns data for commodities which contain fewer than "thresh"
    instances of 1e-9 and saves it in a CSV file which is specified in the argument. """
    commlist = ["CHRIS/CME_0D","CHRIS/CME_0F","CHRIS/SGX_1MF","CHRIS/CME_1N","CHRIS/CME_1NB","CHRIS/CME_1R",
                "CHRIS/CME_1U","CHRIS/SGX_3MF","CHRIS/CME_46","CHRIS/CME_47","CHRIS/CME_4L","CHRIS/CME_4M",
                "CHRIS/CME_4N","CHRIS/CME_4P","CHRIS/CME_58","CHRIS/CME_5C","CHRIS/CME_5Z","CHRIS/CME_6T",
                "CHRIS/CME_6Z","CHRIS/CME_71","CHRIS/CME_7H","CHRIS/CME_7K","CHRIS/CME_7Q","CHRIS/CME_7Y",
                "CHRIS/CME_8I","CHRIS/CME_8Z","CHRIS/CME_9F","CHRIS/CME_A3","CHRIS/CME_A5","CHRIS/CME_A6",
                "CHRIS/ODE_AB","CHRIS/CME_ABY","CHRIS/CME_AD","CHRIS/CME_AFF","CHRIS/ICE_B","CHRIS/ICE_C",
                "CHRIS/MCX_AG","CHRIS/SHFE_AG","CHRIS/CME_AGA","CHRIS/MCX_AGM","CHRIS/SHFE_AL","CHRIS/MCX_AL",
                "CHRIS/MCX_ALM","CHRIS/ASX_AP","CHRIS/SGX_AP","CHRIS/ICE_C","CHRIS/CME_ARW","CHRIS/ICE_G",
                "CHRIS/ICE_M","CHRIS/SHFE_AU","CHRIS/CME_AW","CHRIS/LIFFE_AXF","CHRIS/MCX_B","CHRIS/ICE_DW",
                "CHRIS/CME_B0","CHRIS/CME_B3","CHRIS/CME_B4","CHRIS/CME_B6","CHRIS/MX_BAX","CHRIS/CME_BB",
                "CHRIS/ASX_BB","CHRIS/CME_BK","CHRIS/CME_BO","CHRIS/CME_BOB","CHRIS/CME_BP","CHRIS/ICE_DW",
                "CHRIS/CME_BR","CHRIS/ICE_WA","CHRIS/ICE_WA","CHRIS/LIFFE_BXF","CHRIS/CME_BY","CHRIS/CME_BZ",
                "CHRIS/LIFFE_C","CHRIS/CME_C","CHRIS/ICE_OJ","CHRIS/ICE_T","CHRIS/CME_C0","CHRIS/ODE_C75",
                "CHRIS/CME_CB","CHRIS/ICE_AFR","CHRIS/CME_CD","CHRIS/ICE_AFR","CHRIS/ICE_CC","CHRIS/SGX_CFF",
                "CHRIS/MX_CGB","CHRIS/MX_CGF","CHRIS/MX_CGZ","CHRIS/CME_CI","CHRIS/SGX_CIF","CHRIS/MCX_CL",
                "CHRIS/CME_CL","CHRIS/SGX_CN","CHRIS/CME_CNH","CHRIS/EUREX_CONF","CHRIS/CME_CPO","CHRIS/MCX_CRDM",
                "CHRIS/CME_CS","CHRIS/CME_CSC","CHRIS/MCX_CT","CHRIS/ICE_CT","CHRIS/CME_CU","CHRIS/MCX_CU",
                "CHRIS/SHFE_CU","CHRIS/MCX_CUM","CHRIS/CME_CY","CHRIS/CME_CZ","CHRIS/CME_D0","CHRIS/CME_D2",
                "CHRIS/CME_D3","CHRIS/CME_D4","CHRIS/CME_D6","CHRIS/CME_D7","CHRIS/CME_D8","CHRIS/CME_D9",
                "CHRIS/CME_DA","CHRIS/CME_DB","CHRIS/CME_DC","CHRIS/CME_DJ","CHRIS/OSE_DJIA","CHRIS/CME_DK",
                "CHRIS/ICE_KC","CHRIS/ICE_N","CHRIS/ICE_SB","CHRIS/ICE_ATW","CHRIS/ICE_ATW","CHRIS/CME_DY",
                "CHRIS/CME_E3","CHRIS/CME_E4","CHRIS/CME_E5","CHRIS/CME_E7","CHRIS/CME_E8","CHRIS/LIFFE_EBM",
                "CHRIS/CME_EC","CHRIS/LIFFE_ECO","CHRIS/SGX_ED","CHRIS/CME_ED","CHRIS/CME_EH","CHRIS/CME_EJ",
                "CHRIS/SGX_EL","CHRIS/CME_EM","CHRIS/LIFFE_EMA","CHRIS/CME_EN","CHRIS/LIFFE_EO3","CHRIS/LIFFE_EOB",
                "CHRIS/LIFFE_EON","CHRIS/LIFFE_EPE","CHRIS/LIFFE_EPL","CHRIS/LIFFE_EPR","CHRIS/ICE_CER","CHRIS/CME_ES",
                "CHRIS/CME_EW","CHRIS/SGX_EY","CHRIS/CME_EY","CHRIS/CME_F2","CHRIS/EUREX_F2CR","CHRIS/EUREX_F2MX",
                "CHRIS/CME_F5","CHRIS/SGX_FB","CHRIS/EUREX_FBTP","CHRIS/EUREX_FBTS","CHRIS/EUREX_FBUT","CHRIS/CME_FC",
                "CHRIS/EUREX_FCAG","CHRIS/EUREX_FCCO","CHRIS/LIFFE_FCE","CHRIS/EUREX_FCEN","CHRIS/EUREX_FCGR",
                "CHRIS/EUREX_FCIN","CHRIS/EUREX_FCLI","CHRIS/EUREX_FCPE","CHRIS/EUREX_FCPR","CHRIS/EUREX_FCSO",
                "CHRIS/EUREX_FCXE","CHRIS/EUREX_FDAX","CHRIS/EUREX_FDIV","CHRIS/CME_FDM","CHRIS/EUREX_FEAA",
                "CHRIS/EUREX_FEDV","CHRIS/LIFFE_FEF","CHRIS/SGX_FEF","CHRIS/LIFFE_FEO","CHRIS/EUREX_FEO1",
                "CHRIS/EUREX_FEPP","CHRIS/EUREX_FERU","CHRIS/EUREX_FESX","CHRIS/EUREX_FEU3","CHRIS/EUREX_FEXD",
                "CHRIS/EUREX_FEXF","CHRIS/CME_FF","CHRIS/EUREX_FFOX","CHRIS/EUREX_FGBL","CHRIS/EUREX_FGBM",
                "CHRIS/EUREX_FGBS","CHRIS/EUREX_FGBX","CHRIS/CME_FH","CHRIS/EUREX_FHOG","CHRIS/CME_FI",
                "CHRIS/EUREX_FMAS","CHRIS/EUREX_FMCL","CHRIS/EUREX_FMCN","CHRIS/EUREX_FMCO","CHRIS/EUREX_FMCZ",
                "CHRIS/EUREX_FMEA","CHRIS/EUREX_FMEE","CHRIS/EUREX_FMEL","CHRIS/EUREX_FMEM","CHRIS/EUREX_FMEU",
                "CHRIS/EUREX_FMEY","CHRIS/EUREX_FMFM","CHRIS/EUREX_FMHU","CHRIS/EUREX_FMIN","CHRIS/EUREX_FMJP",
                "CHRIS/EUREX_FMMA","CHRIS/EUREX_FMMX","CHRIS/EUREX_FMMY","CHRIS/EUREX_FMPE","CHRIS/EUREX_FMPH",
                "CHRIS/EUREX_FMPL","CHRIS/EUREX_FMRS","CHRIS/EUREX_FMRU","CHRIS/EUREX_FMTH","CHRIS/EUREX_FMWO",
                "CHRIS/LIFFE_FMX","CHRIS/EUREX_FMZA","CHRIS/CME_FO","CHRIS/EUREX_FOAM","CHRIS/EUREX_FOAT",
                "CHRIS/CME_FP","CHRIS/EUREX_FPIG","CHRIS/EUREX_FRDX","CHRIS/CME_FS","CHRIS/ODE_FS","CHRIS/EUREX_FSLI",
                "CHRIS/EUREX_FSMI","CHRIS/EUREX_FSMM","CHRIS/EUREX_FSMP","CHRIS/EUREX_FSTX","CHRIS/EUREX_FTDX",
                "CHRIS/LIFFE_FTI","CHRIS/CME_FTM","CHRIS/SHFE_FU","CHRIS/CME_FV","CHRIS/EUREX_FVS","CHRIS/EUREX_FWHY",
                "CHRIS/CME_FY","CHRIS/ICE_O","CHRIS/LIFFE_G","CHRIS/CME_GA","CHRIS/CME_GA","CHRIS/CME_GC",
                "CHRIS/MCX_GC","CHRIS/CME_GCI","CHRIS/CME_GCU","CHRIS/MCX_GD","CHRIS/CME_GE","CHRIS/ICE_RS",
                "CHRIS/MCX_GG","CHRIS/CME_GI","CHRIS/CME_GL","CHRIS/MCX_GM","CHRIS/ICE_RS","CHRIS/SGX_GOF",
                "CHRIS/MCX_GP","CHRIS/MCX_GRM","CHRIS/MCX_GRS","CHRIS/CBOE_GV","CHRIS/ASX_GW","CHRIS/CME_GY",
                "CHRIS/CME_GZ","CHRIS/LIFFE_H","CHRIS/CME_H2","CHRIS/CME_H3","CHRIS/CME_H4","CHRIS/CME_H5",
                "CHRIS/CME_HA","CHRIS/CME_HB","CHRIS/CME_HG","CHRIS/CME_HH","CHRIS/SGX_HK","CHRIS/CME_HK",
                "CHRIS/CME_HMO","CHRIS/CME_HMW","CHRIS/CME_HO","CHRIS/CME_HOB","CHRIS/CME_HP","CHRIS/CME_HR",
                "CHRIS/LIFFE_I","CHRIS/CME_I3","CHRIS/CME_I5","CHRIS/CME_I6","CHRIS/ASX_IB","CHRIS/ICE_SF",
                "CHRIS/CME_IBV","CHRIS/MGEX_IC","CHRIS/ICE_SF","CHRIS/SGX_ID","CHRIS/MGEX_IH","CHRIS/CME_IN",
                "CHRIS/SGX_IN","CHRIS/MGEX_IP","CHRIS/ASX_IR","CHRIS/SGX_IR","CHRIS/ICE_TIB","CHRIS/MGEX_IS",
                "CHRIS/ICE_AR","CHRIS/MGEX_IW","CHRIS/ICE_BPB","CHRIS/LIFFE_J","CHRIS/CME_J2","CHRIS/CME_J4",
                "CHRIS/CME_J7","CHRIS/SGX_JB","CHRIS/TFX_JBA","CHRIS/SGX_JG","CHRIS/LIFFE_JGB","CHRIS/CME_JM",
                "CHRIS/CME_JP","CHRIS/CME_JR","CHRIS/CME_JS","CHRIS/CME_JY","CHRIS/CME_K2","CHRIS/CME_K3",
                "CHRIS/CME_K4","CHRIS/CME_KA","CHRIS/CME_KB","CHRIS/ICE_BW","CHRIS/CME_KG","CHRIS/CME_KH",
                "CHRIS/CME_KI","CHRIS/CME_KJ","CHRIS/CME_KK","CHRIS/MCX_KP","CHRIS/MCX_KPK","CHRIS/SGX_KRF",
                "CHRIS/ICE_BW","CHRIS/CME_KS","CHRIS/CME_KW","CHRIS/LIFFE_L","CHRIS/CME_L1","CHRIS/CME_L3",
                "CHRIS/CME_L4","CHRIS/CME_L5","CHRIS/CME_L6","CHRIS/CME_L9","CHRIS/CME_LB","CHRIS/CME_LC",
                "CHRIS/MX_LGB","CHRIS/MX_LGB","CHRIS/CME_LN","CHRIS/CME_LT","CHRIS/CME_LY","CHRIS/ICE_CEU",
                "CHRIS/CME_M6B","CHRIS/CME_M6E","CHRIS/CME_MBE","CHRIS/CME_MBN","CHRIS/CME_MCC","CHRIS/CME_MD",
                "CHRIS/CME_ME","CHRIS/CME_MEL","CHRIS/CME_MEO","CHRIS/CME_MF","CHRIS/LIFFE_MFA","CHRIS/LIFFE_MFC",
                "CHRIS/CME_MFF","CHRIS/CME_MG","CHRIS/CME_MGC","CHRIS/CME_MJN","CHRIS/CME_MM","CHRIS/CME_MNB",
                "CHRIS/CME_MNC","CHRIS/MCX_MO","CHRIS/CME_MOD","CHRIS/ICE_DPA","CHRIS/CME_MP","CHRIS/LIFFE_MPE",
                "CHRIS/CME_MPX","CHRIS/SGX_MR","CHRIS/CME_MTF","CHRIS/CME_MTS","CHRIS/MGEX_MW","CHRIS/ICE_DPB",
                "CHRIS/CME_N1","CHRIS/CME_N1U","CHRIS/CME_N1Y","CHRIS/CME_N3","CHRIS/CME_N9","CHRIS/ICE_DX",
                "CHRIS/SGX_ND","CHRIS/CME_ND","CHRIS/CME_NE","CHRIS/CME_NEN","CHRIS/CME_NF","CHRIS/CME_NFN",
                "CHRIS/CME_NG","CHRIS/MCX_NG","CHRIS/CME_NH","CHRIS/CME_NI","CHRIS/MCX_NI","CHRIS/MCX_NIM",
                "CHRIS/CME_NJ","CHRIS/ICE_ERU","CHRIS/SGX_NJF","CHRIS/CME_NK","CHRIS/SGX_NK","CHRIS/OSE_NK225",
                "CHRIS/OSE_NK225M","CHRIS/OSE_NK300","CHRIS/CME_NKN","CHRIS/OSE_NKVI","CHRIS/CME_NL","CHRIS/CME_NN",
                "CHRIS/CME_NP","CHRIS/CME_NQ","CHRIS/CME_NR","CHRIS/CME_NS","CHRIS/ICE_GER","CHRIS/SGX_NU",
                "CHRIS/CME_NW","CHRIS/CME_NX","CHRIS/CME_NYF","CHRIS/CME_NZ","CHRIS/CME_O","CHRIS/ICE_GNM",
                "CHRIS/CME_O1","CHRIS/CME_OFM","CHRIS/ASX_OI","CHRIS/MX_OIS","CHRIS/ICE_IBO","CHRIS/MX_ONX",
                "CHRIS/CME_OPM","CHRIS/ODE_OR","CHRIS/CBOE_OV","CHRIS/ICE_ICN","CHRIS/ICE_IS","CHRIS/CME_P5",
                "CHRIS/CME_P7","CHRIS/CME_P8","CHRIS/CME_PA","CHRIS/SHFE_PB","CHRIS/MCX_PB","CHRIS/MCX_PBM",
                "CHRIS/CME_PC","CHRIS/CME_PD","CHRIS/CME_PDM","CHRIS/CME_PF","CHRIS/CME_PG","CHRIS/CME_PH",
                "CHRIS/CME_PL","CHRIS/MCX_POT","CHRIS/LIFFE_PSI","CHRIS/CME_PTM","CHRIS/CME_PZ","CHRIS/LIFFE_Q",
                "CHRIS/CME_Q5","CHRIS/CME_QG","CHRIS/CME_QL","CHRIS/CME_QM","CHRIS/CME_QP","CHRIS/CME_QX",
                "CHRIS/LIFFE_R","CHRIS/CME_R3","CHRIS/CME_R6","CHRIS/CME_R7","CHRIS/CME_RA","CHRIS/SHFE_RB",
                "CHRIS/CME_RB","CHRIS/CME_RBB","CHRIS/LIFFE_RC","CHRIS/CME_RF","CHRIS/ICE_ISM","CHRIS/ICE_IW",
                "CHRIS/SGX_RGF","CHRIS/CME_RK","CHRIS/CME_RL","CHRIS/CME_RM","CHRIS/CME_RP","CHRIS/CME_RR",
                "CHRIS/ICE_KRU","CHRIS/ICE_MP","CHRIS/ODE_RS","CHRIS/SGX_RT","CHRIS/CME_RU","CHRIS/SHFE_RU",
                "CHRIS/ICE_NCF","CHRIS/CME_RV","CHRIS/CME_RY","CHRIS/CME_S","CHRIS/LIFFE_S","CHRIS/CME_S4",
                "CHRIS/CME_SA","CHRIS/ODE_SB","CHRIS/ICE_NJ","CHRIS/MX_SCF","CHRIS/CME_SD","CHRIS/CME_SE",
                "CHRIS/ICE_NT","CHRIS/ICE_P","CHRIS/CME_SF","CHRIS/CME_SG","CHRIS/SGX_SG","CHRIS/CME_SI",
                "CHRIS/MCX_SI","CHRIS/MCX_SIM","CHRIS/CME_SM","CHRIS/CME_SP","CHRIS/ICE_P","CHRIS/CME_SSI",
                "CHRIS/SGX_ST","CHRIS/MCX_STLRPR","CHRIS/MX_SXA","CHRIS/MX_SXB","CHRIS/MX_SXF","CHRIS/MX_SXH",
                "CHRIS/MX_SXM","CHRIS/MX_SXY","CHRIS/ICE_RF","CHRIS/CME_SZ","CHRIS/LIFFE_T","CHRIS/ICE_RG",
                "CHRIS/CME_T3","CHRIS/CME_TC","CHRIS/ICE_RV","CHRIS/SGX_TF","CHRIS/ICE_SS","CHRIS/ICE_SY",
                "CHRIS/CME_TIO","CHRIS/ASX_TN","CHRIS/LIFFE_TPI","CHRIS/CME_TR","CHRIS/SGX_TR","CHRIS/ODE_TR",
                "CHRIS/CME_TRY","CHRIS/CME_TU","CHRIS/SGX_TW","CHRIS/ASX_TY","CHRIS/CME_TY","CHRIS/CME_TZ6",
                "CHRIS/CME_U3","CHRIS/CME_U4","CHRIS/CME_U5","CHRIS/CME_U6","CHRIS/CME_UA","CHRIS/ASX_UB",
                "CHRIS/CME_UB","CHRIS/CME_UL","CHRIS/ICE_TF","CHRIS/ICE_TFM","CHRIS/CME_UM","CHRIS/CME_UN",
                "CHRIS/CME_UO","CHRIS/CME_US","CHRIS/ASX_US","CHRIS/CME_UV","CHRIS/CME_UX","CHRIS/CME_V3",
                "CHRIS/ASX_VC","CHRIS/SGX_VCF","CHRIS/CME_VM","CHRIS/CBOE_VN","CHRIS/CME_VP","CHRIS/CME_VR",
                "CHRIS/ASX_VW","CHRIS/CBOE_VX","CHRIS/CBOE_VXEW","CHRIS/LIFFE_W","CHRIS/CME_W","CHRIS/CME_W4",
                "CHRIS/CME_W6","CHRIS/ICE_ULS","CHRIS/ICE_ULS","CHRIS/CME_WCC","CHRIS/CME_WJ","CHRIS/ASX_WK",
                "CHRIS/CME_WQ","CHRIS/SHFE_WR","CHRIS/CME_WS","CHRIS/CME_X1","CHRIS/CME_XAF","CHRIS/CME_XAK",
                "CHRIS/CME_XAP","CHRIS/CME_XAU","CHRIS/CME_XAY","CHRIS/LIFFE_XFC","CHRIS/CME_XN","CHRIS/ASX_XS",
                "CHRIS/LIFFE_XZ","CHRIS/LIFFE_Y","CHRIS/ICE_Y","CHRIS/ICE_Y","CHRIS/CME_Y1","CHRIS/CME_Y7",
                "CHRIS/CME_YC","CHRIS/ODE_YC","CHRIS/CME_YH","CHRIS/CME_YK","CHRIS/CME_YM","CHRIS/ASX_YS",
                "CHRIS/ASX_YT","CHRIS/CME_YW","CHRIS/CME_YX","CHRIS/LIFFE_YZ","CHRIS/CME_Z","CHRIS/LIFFE_Z",
                "CHRIS/CME_Z1","CHRIS/CME_Z9","CHRIS/ICE_ZJ","CHRIS/MCX_ZN","CHRIS/SHFE_ZN","CHRIS/MCX_ZNM",
                "CHRIS/ICE_ZR"]
    x = readQuandl(commlist, 6000, True)
    y = x.dropna(axis=1, thresh=5500)
    nan2zero = cleanData(y)
    z = np.asarray(nan2zero)
    np.savetxt(csvfilename, z, delimiter=",")
  #  return z # Temp

def readWikiFutures(wikifuturescsv):
    """this function reads the Wiki Continuous Futures data for the commodities together with the category of the
    commodity (Metals, Softs, Livestock, Energy), and also the exchanges which trade the particular product. """
    df = pd.read_csv(wikifuturescsv)
    df.as_matrix()
    return df
