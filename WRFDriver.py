import WRFPrediction
import numpy as np
import csv

start_lat = 46.8601 #decimal degrees (46.8601 for UM Oval)
start_lon = -113.9852 #decimal degrees (-113.9852 for UM Oval)
start_alt = 980.84 #m


start_time = "17:00:00" #UTC
burstDi = "602" #cm

#WRF FILE AND DIRECTORY
wrf_file = "wrfout_d02_2022-07-13_17:00:00" #UTC hour required
timeSpanOfWrfFile = 3600 #sec


#/home/wrf_user/Desktop/070622Complete/em_real/
#/home/wrf_user/WRF/WRF/test/em_real/
main_directory = "/home/wrf_user/WRF/WRF/test/em_real/" #Change to directory where WRF outputs are

#PREDICTIONS
points, times, rates = WRFPrediction.Prediction(wrf_file, main_directory, start_lat, start_lon, start_alt, burstDi, start_time, timeSpanOfWrfFile)

with open("times.txt", "w") as output:
    output.write(str(times))

with open("rates.txt", "w") as output:
    output.write(str(rates))

#WRITING TO CSV 
file_name = 'Prediction.csv' #name of CSV file
with open(file_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Latitude', 'Longitude', 'Altitude(m)', 'Rise Rate(m/s)']) #creating the header

    for i in points:
        writer.writerows([i]) #writing the data in csv format 
        writer.writerows([i]) #writing the data in csv format 


