"""
Haleigh Brown MSGC UM BOREALIS
haleighebrown@gmail.com
Tue July 19 2022

BALLOON TRAJECTORY OVERALL COMPARISON VISUALIZATION TOOL:
"""

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
plt.style.use('seaborn-whitegrid')

#USER VARIABLES
radFile = "/home/wrf_user/Downloads/UM5_1710UTC_070622_GARY_Profile.txt"#location of radiosonde profile data
predFile = "/home/wrf_user/Desktop/Prediction.csv"                      #location of prediction data
predTimesFile = "/home/wrf_user/Desktop/times.txt"                      #location of prediction times

durationOL = 7052                                                       #duration of the observed launch (sec)


#READING IN RADIOSONDE PROFILE DATA 
radDF = pd.read_csv(radFile, sep= "\t", skiprows = 18, encoding = 'unicode_escape')

#RENAMING RADIOSONDE DATA COLUMNS AND FILTERING OUT BLANK END ROWS
radDF.rename(columns={radDF.columns.values[10] : "Observed Geopotential", radDF.columns.values[0] : "Time", radDF.columns.values[7] : "Observed Longitude", radDF.columns.values[8] : "Observed Latitude"}, inplace=True)
radDF = radDF.iloc[1:durationOL + 2, :]
pd.options.mode.chained_assignment = None  # default='warn'

#CONVERTING COLUMNS FROM STRING TO FLOAT FORMAT
radDF["Observed Geopotential"] = (radDF["Observed Geopotential"]).str.strip().astype(float)
radDF["Time"] = (radDF["Time"]).str.strip().astype(float)
radDF["Observed Longitude"] = (radDF["Observed Longitude"]).str.strip().astype(float)
radDF["Observed Latitude"] = (radDF["Observed Latitude"]).str.strip().astype(float)

#READING IN PREDICTION DATA AND GRABING ASSOCIATED TIMES
predDF = pd.read_csv(predFile, sep= ",", skiprows=lambda x: (x != 0) and not x % 2, encoding = 'unicode_escape')
predDF.rename(columns={"Longitude" : "Predicted Longitude"}, inplace=True)
predDF.rename(columns={"Latitude" : "Predicted Latitude"}, inplace=True)
predDF.rename(columns={"Altitude(m)" : "Predicted Geopotential"}, inplace=True)
with open(predTimesFile,'r') as times:
    for line in times:
        predTimes = line.split(",")
    predTimes[0] = predTimes[0][1:]
    predTimes[-1] = predTimes[-1][:-1]

predDF["pointTimes"] = predTimes
predDF["pointTimes"] = (predDF["pointTimes"]).str.strip().astype(float)



##############################PLOTING##############################
threeD = plt.figure().gca(projection='3d')
threeD.plot(radDF["Observed Longitude"], radDF["Observed Latitude"], radDF["Observed Geopotential"], label="Observed")
threeD.plot(predDF["Predicted Longitude"], predDF["Predicted Latitude"], predDF["Predicted Geopotential"], label="Predicted")

plt.rcParams.update({'font.family':'sans-serif'})
plt.legend(loc="upper right", fontsize=20)
threeD.set_xlabel("Longitude", fontsize=20, labelpad=10)
threeD.set_ylabel("Latitude", fontsize=20, labelpad=10)
threeD.set_zlabel("Geopotential", fontsize=20, labelpad=10)
plt.title("Observed vs. Predicted Balloon Trajectory", fontsize=20)
plt.show()














