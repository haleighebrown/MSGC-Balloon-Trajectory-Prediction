"""
Haleigh Brown MSGC UM BOREALIS
haleighebrown@gmail.com
Tue July 19 2022

BALLOON TRAJECTORY GEOPOTENTIAL COMPARISON VISUALIZATION TOOL:
"""

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
plt.style.use('seaborn-whitegrid')

#USER VARIABLES
radFile = "/home/wrf_user/Downloads/UM5_1710UTC_070622_GARY_Profile.txt" #location of radiosonde profile data
predFile = "/home/wrf_user/Desktop/Prediction.csv"                      #location of prediction data
predTimesFile = "/home/wrf_user/Desktop/times.txt"                      #location of prediction times

durationOL = 7052                                                       #duration of the observed launch (sec)
startingGP = 980                                                        #starting GP/Alt (m)


#READING IN RADIOSONDE PROFILE DATA 
radDF = pd.read_csv(radFile, sep= "\t", skiprows = 18, encoding = 'unicode_escape')

#RENAMING RADIOSONDE DATA COLUMNS AND FILTERING OUT BLANK END ROWS
radDF.rename(columns={radDF.columns.values[10] : "Observed Geopotential", radDF.columns.values[0] : "Time"}, inplace=True)
radDF = radDF.iloc[1:durationOL + 2, :]
pd.options.mode.chained_assignment = None  # default='warn'

#CONVERTING COLUMNS FROM STRING TO FLOAT FORMAT
radDF["Observed Geopotential"] = (radDF["Observed Geopotential"]).str.strip().astype(float)
radDF["Time"] = (radDF["Time"]).str.strip().astype(float)


#READING IN PREDICTION DATA AND GRABING ASSOCIATED TIMES
predDF = pd.read_csv(predFile, sep= ",", skiprows=lambda x: (x != 0) and not x % 2, encoding = 'unicode_escape')
predDF.rename(columns={"Altitude(m)" : "Predicted Geopotential"}, inplace=True)
with open(predTimesFile,'r') as times:
    for line in times:
        predTimes = line.split(",")
    predTimes[0] = predTimes[0][1:]
    predTimes[-1] = predTimes[-1][:-1]

predDF["pointTimes"] = predTimes
predDF["pointTimes"] = (predDF["pointTimes"]).str.strip().astype(float)


##############################PLOTING##############################
ax = radDF.plot(x = "Time", y = "Observed Geopotential")
predDF.plot(ax = ax, x = "pointTimes", y = "Predicted Geopotential")

plt.axhline(0, color = "black")
plt.axvline(0, color = "black")

observedBurst = radDF.loc[radDF["Observed Geopotential"].idxmax()]
predictedBurst = predDF.loc[predDF["Predicted Geopotential"].idxmax()]
#this code is for ploting the max alt for both predicted and observed alt
plt.plot(observedBurst["Time"], observedBurst["Observed Geopotential"],"o:k", ms = 5)
plt.text(observedBurst["Time"]+100, observedBurst["Observed Geopotential"]+150, str(round(observedBurst["Observed Geopotential"]/1000, 2)) + "km", {'ha': 'left'}, rotation = 0)
plt.plot(predictedBurst["pointTimes"], predictedBurst["Predicted Geopotential"], "o:k", ms = 5)
plt.text(predictedBurst["pointTimes"]+100, predictedBurst["Predicted Geopotential"], str(round(predictedBurst["Predicted Geopotential"]/1000, 2)) + "km", {'ha': 'left'}, rotation = 0)

plt.xlim(0, max(observedBurst["Time"], predictedBurst["pointTimes"]) + 1000)
plt.ylim(startingGP, max(observedBurst["Observed Geopotential"], predictedBurst["Predicted Geopotential"]) + 5000)

plt.rcParams.update({'font.family':'sans-serif'})
plt.legend(loc="upper right", fontsize=15)
plt.title("Observed vs. Predicted Balloon Geopotential", fontsize=20)
plt.xlabel("Time [sec]", fontsize=20, labelpad=10)
plt.ylabel("Geopotential [m]", fontsize=20, labelpad=10)
plt.show()






