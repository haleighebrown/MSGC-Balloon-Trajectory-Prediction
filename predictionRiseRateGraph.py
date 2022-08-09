"""
Haleigh Brown MSGC UM BOREALIS
haleighebrown@gmail.com
Tue July 19 2022

BALLOON TRAJECTORY RISE RATE COMPARISON VISUALIZATION TOOL:
"""

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
plt.style.use('seaborn-whitegrid')

#USER VARIABLES
radFile = "/home/wrf_user/Downloads/UM5_1710UTC_070622_GARY_Profile.txt" #location of radiosonde profile data
predFile = "/home/wrf_user/Desktop/Prediction.csv"                       #location of prediction data
predTimesFile = "/home/wrf_user/Desktop/times.txt"                       #location of prediction times

durationOL = 7052                                                        #duration of the observed launch (sec)
   
                                                 
predRiseRatesFile = "/home/wrf_user/Desktop/rates.txt"
#READING IN RADIOSONDE PROFILE DATA 
radDF = pd.read_csv(radFile, sep= "\t", skiprows = 18, encoding = 'unicode_escape')

#RENAMING RADIOSONDE DATA COLUMNS AND FILTERING OUT BLANK END ROWS
radDF.rename(columns={radDF.columns.values[15] : "Observed Rise Rates", radDF.columns.values[0] : "Time"}, inplace=True)

radDF = radDF.iloc[1:durationOL + 2, :]
pd.options.mode.chained_assignment = None  # default='warn'

#CONVERTING COLUMNS FROM STRING TO FLOAT FORMAT AND CLEANING DATA
radDF["Observed Rise Rates"] = (radDF["Observed Rise Rates"]).str.strip()


#radDF[radDF["Observed Rise Rates"] == "-"] = "0.0"

radDF = radDF.drop(radDF[radDF["Observed Rise Rates"].str.contains(r'-')].index)
radDF["Observed Rise Rates"] = (radDF["Observed Rise Rates"]).astype(float)
radDF["Time"] = (radDF["Time"]).str.strip().astype(float)


#READING IN PREDICTION DATA AND GRABING ASSOCIATED TIMES AND RISE RATES
with open(predRiseRatesFile,'r') as rates:
    for line in rates:
        predRates = line.split(",")
    predRates[0] = predRates[0][1:]
    predRates[-1] = predRates[-1][:-1]

with open(predTimesFile,'r') as times:
    for line in times:
        predTimes = line.split(",")
    predTimes[0] = predTimes[0][1:]
    predTimes[-1] = predTimes[-1][:-1]

predDF = pd.DataFrame()
predDF["Predicted Rise Rates"] = predRates
predDF["Predicted Rise Rates"] = (predDF["Predicted Rise Rates"]).str.strip().astype(float)
predDF["predTimes"] = predTimes
predDF["predTimes"] = (predDF["predTimes"]).str.strip().astype(float)


##############################PLOTING##############################
ax = radDF.plot(x = "Time", y = "Observed Rise Rates")
predDF.plot(ax = ax, x = "predTimes", y = "Predicted Rise Rates")

plt.axhline(0, color = "black")
plt.axvline(0, color = "black")

observedRatesMax = radDF.loc[radDF["Observed Rise Rates"].idxmax()]
predictedRatesMax = predDF.loc[predDF["Predicted Rise Rates"].idxmax()]
observedRatesMin = radDF.loc[radDF["Observed Rise Rates"].idxmin()]
predictedRatesMin = predDF.loc[predDF["Predicted Rise Rates"].idxmin()]

plt.xlim(0, max(observedRatesMax["Time"], predictedRatesMax["predTimes"]) + 100)
plt.ylim(0, max(observedRatesMax["Observed Rise Rates"], predictedRatesMax["Predicted Rise Rates"]) + .1)
#to view the descent rates, put the min as the lower limit using this line:
#min(observedRatesMin["Observed Rise Rates"], predictedRatesMin["Predicted Rise Rates"]) - .1

plt.title("Observed vs. Predicted Balloon Rise Rates")
plt.xlabel("Time [sec]")
plt.ylabel("Rise Rate [m/s]")
plt.show()


