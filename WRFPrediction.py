"""
Created on Tue Jun 23 09:34:11 2015

@author: Reed Hovenkotter
"""

import WRFReader
import Calculations
import numpy as np

#USER INITIAL VARIABLES
#Should probably put these as variables Predictions needs to run at some point
radius_parachute = 0.28 #m (0.28 m for GRAW red parachute)
#Balloon Info: http://kaymontballoons.com/Weather_Forecasting.html
radius_balloon = 0.662432 #m (200g balloon has radius of 1.95 ft = 0.59436 m)                            # IS THIS RADIUS OR DIAMETER? 
mass_balloon = 600 #g
mass_payload = 100 #g
# radiosonde = 'RadiosondeData/Fort_Missoula_07_29_2015.txt' # Is this needed? not for Chile

def Prediction(wrf_file, main_directory, start_lat, start_lon, start_alt, max_alt):
    #Floating balloon variables for testing
    floating_balloon = False
    duration = 3600
    time_in_float = 0
    floating = False
    TIME_INCREMENT = 30
    #NONUSER VARIABLES
    ascent = True
    done = False
    points = []
    #arbitraty initial rise rate
    rise_rate = 5.0
    hour_duration = 0
    current_lat = start_lat
    current_lon = start_lon
    current_alt = start_alt
    latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
    points.append(latLonAlt)

    #CONSTANTS
    ALT_INCREMENT = 150.0 #m
    #PREDICTION PROCESS
    wrf = WRFReader.openWRF(main_directory, wrf_file)
    print(wrf_file, wrf)
    x,y = WRFReader.findNetCDFLatLonIndex(wrf,current_lat,current_lon)
    z = WRFReader.findNetCDFAltIndex(wrf,x,y,current_alt)
    P_surface = WRFReader.getPressure(wrf, x, y, z)
    T_surface = WRFReader.getTemperature(wrf, x, y, z)

    while(not done):
        x,y = WRFReader.findNetCDFLatLonIndex(wrf,current_lat,current_lon)
        z = WRFReader.findNetCDFAltIndex(wrf,x,y,current_alt)

        w_spd, w_dir, w_vert = WRFReader.getWindSpeedAndDirection(wrf,x,y,z)
        terrain_height = WRFReader.getTerrainHeight(wrf,x,y)

        P = WRFReader.getPressure(wrf, x, y, z)
        T = WRFReader.getTemperature(wrf, x, y, z)

        if not floating:
            rise_time = 1/abs(rise_rate) * ALT_INCREMENT
            distance = rise_time * w_spd
        else:
            rise_time = TIME_INCREMENT
            distance = rise_time * w_spd

        hour_duration += rise_time
        if hour_duration >= 3600:                                       #SECONDS?
            wrf_time = int(wrf_file[22:24]) + 1
            wrf_file =  wrf_file[:22] + str(wrf_time) + wrf_file[24:]
            wrf = WRFReader.openWRF(main_directory, wrf_file)
            hour_duration = 0

        current_lat, current_lon = Calculations.destination(distance/1000, w_dir, current_lat, current_lon)
        print(current_lat, current_lon)
        if(ascent):
            current_alt += ALT_INCREMENT
##            rise_rate = Calculations.getRiseRate(current_alt, ascent)
            rise_rate = Calculations.getAscentRate(P_surface,T_surface,P,T,radius_balloon,float(mass_balloon)/1000.0,float(mass_payload)/1000.0)
##            rise_rate = Calculations.getRiseRateRadiosonde(current_alt, ascent, radiosonde)
##            rise_rate = Calculations.getRiseRateSmall(current_alt, ascent)
            rise_rate += w_vert
            if(current_alt >= max_alt):
                print('burst')
                ascent = False
        else:
            if(floating_balloon and time_in_float < duration):
                time_in_float+=TIME_INCREMENT
                floating = True
            else:
                floating = False
                current_alt -= ALT_INCREMENT
##                rise_rate = Calculations.getRiseRate(current_alt, ascent)
                rise_rate = Calculations.getDecentRate(P,T,float(radius_parachute),float(mass_balloon)/1000,float(mass_payload)/1000)
##                rise_rate = Calculations.getRiseRateRadiosonde(current_alt, ascent, radiosonde)
##                rise_rate = Calculations.getRiseRateSmall(current_alt, ascent)
                rise_rate += w_vert
                if(current_alt <= terrain_height):
                    done = True
                    current_alt = terrain_height
        latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
        points.append(latLonAlt)
    wrf.close()
    return points
