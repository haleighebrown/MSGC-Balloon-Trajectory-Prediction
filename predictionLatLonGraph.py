"""
Haleigh Brown MSGC UM BOREALIS
haleighebrown@gmail.com
Tue July 19 2022

BALLOON TRAJECTORY LAT/LON COMPARISON VISUALIZATION TOOL:
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
startingLat = 46.859                                                     #starting lattitude (°)
startingLon = -113.985                                                   #starting longitude (°)


#READING IN RADIOSONDE PROFILE DATA 
radDF = pd.read_csv(radFile, sep= "\t", skiprows = 18, encoding = 'unicode_escape')

#RENAMING RADIOSONDE DATA COLUMNS AND FILTERING OUT BLANK END ROWS
radDF.rename(columns={radDF.columns.values[7] : "Observed Longitude", radDF.columns.values[8] : "Observed Latitude"}, inplace=True)
radDF = radDF.iloc[1:durationOL + 2, :]
pd.options.mode.chained_assignment = None  # default='warn'

#CONVERTING COLUMNS FROM STRING TO FLOAT FORMAT
radDF["Observed Longitude"] = (radDF["Observed Longitude"]).str.strip().astype(float)
radDF["Observed Latitude"] = (radDF["Observed Latitude"]).str.strip().astype(float)


#READING IN PREDICTION DATA AND RENAMING COLUMNS
predDF = pd.read_csv(predFile, sep= ",", skiprows=lambda x: (x != 0) and not x % 2, encoding = 'unicode_escape')
predDF.rename(columns={"Longitude" : "Predicted Longitude"}, inplace=True)
predDF.rename(columns={"Latitude" : "Predicted Latitude"}, inplace=True)


##############################PLOTING##############################
ax = radDF.plot(x = "Observed Longitude", y = "Observed Latitude")
predDF.plot(ax = ax, x = "Predicted Longitude", y = "Predicted Latitude")

plt.axhline(0, color = "black")
plt.axvline(0, color = "black")

observedLon = radDF.loc[radDF["Observed Longitude"].idxmax()]
predictedLon = predDF.loc[predDF["Predicted Longitude"].idxmax()]

observedLat = radDF.loc[radDF["Observed Latitude"].idxmax()]
predictedLat = predDF.loc[predDF["Predicted Latitude"].idxmax()]

plt.xlim(startingLon, max(observedLon["Observed Longitude"], predictedLon["Predicted Longitude"]) + .1)
plt.ylim(startingLat, max(observedLat["Observed Latitude"], predictedLat["Predicted Latitude"]) + .1)

plt.title("Observed vs. Predicted Balloon Lat Lon Location")
plt.xlabel("Lon")
plt.ylabel("Lat")
plt.show()




