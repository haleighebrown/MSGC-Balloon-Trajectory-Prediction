import math
import WRFReader
import Calculations
import numpy as np
import wrf


#USER INITIAL VARIABLES
radius_parachute = 0.28 #m (0.28 m for GRAW red parachute)
#Balloon Info: http://kaymontballoons.com/Weather_Forecasting.html
                            
mass_balloon = 600 #g
mass_payload = 100 #g

#This is the main prediction function that relies on WRFReader.py and Calculations.py. 
def Prediction(wrf_file, main_directory, start_lat, start_lon, start_alt, burstDi, start_time, timeSpanOfWrfFile):
    #Floating balloon variables for testing
    floating_balloon = False 
    duration = timeSpanOfWrfFile 
    time_in_float = 0 
    floating = False 
    TIME_INCREMENT = 30
 
    #NONUSER VARIABLES
    ascent = True 
    done = False 
    points = [] 
    times = [] 
    riseRates = []
    rise_rate = 5.0
    last_Rate = None 
    duration = 0 
    count = 1
    time = 0
    rate = 0
    index = 0
    secInterval = 3600
    times.append(time)
    riseRates.append(rate)
    current_lat = start_lat 
    current_lon = start_lon 
    current_alt = start_alt 
    latLonAlt = [current_lat, current_lon, current_alt, rise_rate] 
    points.append(latLonAlt) 
    
    #CONSTANTS
    ALT_INCREMENT = 100.0     
    
    #PREDICTION PROCESS: start with opening the first WRF file. 
    wrfFile = WRFReader.openWRF(main_directory, wrf_file)
    
    #find starting point: (this is only applicable when using non-hourly wrf input files, which can be necessary if actual launch occurs off the hour)
    numFrames = len(wrf.g_times.get_xtimes(wrfFile, timeidx=wrf.ALL_TIMES))
    if numFrames != 1: 
    	secInterval = timeSpanOfWrfFile/numFrames 
    	start = int(start_time[3:5])*60 + int(start_time[6:])
    	index = round(start/secInterval) 
    
    #initializing values with surface data 
    x,y = WRFReader.findNetCDFLatLonIndex(wrfFile, current_lat, current_lon, index) 
    z = WRFReader.findNetCDFAltIndex(wrfFile, x, y, current_alt, index) 
    P_surface = WRFReader.getPressure(wrfFile, x, y, z, index) 
    T_surface = WRFReader.getTemperature(wrfFile, x, y, z, index) 
    
    #retrieving initial fill, volume, and radius values
    predicted_Fill, volume_AtLaunch, radius_AtLaunch = Calculations.predictedFill(P_surface, T_surface, mass_balloon/1000, mass_payload/1000)
    print("This is the predicted fill value: ", predicted_Fill)


    #This loop runs from launch to the end of decent in increments of 100m  
    while(not done):
        #set necessary variables and increment duration of flight
        x,y = WRFReader.findNetCDFLatLonIndex(wrfFile, current_lat, current_lon, index) 
        z = WRFReader.findNetCDFAltIndex(wrfFile, x, y, current_alt, index) 
        w_spd, w_dir, w_vert = WRFReader.getWindSpeedAndDirection(wrfFile, x, y, z, index) 
        terrain_height = WRFReader.getTerrainHeight(wrfFile, x, y, index) 
        P = WRFReader.getPressure(wrfFile, x, y, z, index) 
        T = WRFReader.getTemperature(wrfFile, x, y, z, index) 
        if not floating: 
            rise_time = 1/abs(rise_rate) * ALT_INCREMENT 
            distance = rise_time * w_spd
        else: 
            rise_time = TIME_INCREMENT
            distance = rise_time * w_spd
        duration += rise_time 
        time += rise_time
        
        #replace curent file (this is able to hand wrf output files of any increment)
        if duration >= secInterval*count: 
            index += 1
            count += 1
            if index == numFrames:              
                if timeSpanOfWrfFile >= 3600:
                    wrf_file =  wrf_file[:22] + str(int(wrf_file[22:24]) + 1).zfill(2) + wrf_file[24:]
                else:
            	    if int(wrf_file[25:27]) == 60 - timeSpanOfWrfFile/60:
                	    wrf_file =  wrf_file[:22] + str(int(wrf_file[22:24]) + 1).zfill(2) + ":00" + wrf_file[27:]
            	    else:
                	    wrf_file =  wrf_file[:25] + str(int(wrf_file[25:27]) + int(timeSpanOfWrfFile/60)) + wrf_file[27:]
                wrfFile = WRFReader.openWRF(main_directory, wrf_file) 
                numFrames = len(wrf.g_times.get_xtimes(wrfFile, timeidx=wrf.ALL_TIMES))
                secInterval = timeSpanOfWrfFile/numFrames
                count = 1
                duration = 0 
                index = 0
        
        #retrive and print new lat and lon
        current_lat, current_lon = Calculations.destination(distance/1000, w_dir, current_lat, current_lon) 
        print(current_lat, current_lon)

        #while still ascending retrive new rise_rate/volume and increase by one ALT_INCREMENT
        if(ascent): 
            current_alt += ALT_INCREMENT 
            rise_rate, volume, last_Rate = Calculations.getAscentRate(P_surface,T_surface,P,T,float(mass_balloon)/1000.0,float(mass_payload)/1000.0, volume_AtLaunch, radius_AtLaunch, last_Rate) 
            rise_rate += w_vert 
         
            #this statments checks if the balloon should still be acsending or if decent should start based on the new volume of the balloon
            if volume >= 4.0/3.0*math.pi*(float(burstDi)/200)**3+35:
            #if current_alt >= 32000: 
                print('burst') 
                ascent = False 

        #if the balloon is now in decent phase retrive fall rate and verify the payload has not reached ground yet 
        else: 
            if(floating_balloon and time_in_float < duration):
                time_in_float+=TIME_INCREMENT
                floating = True
            else: 
                floating = False 
                current_alt -= ALT_INCREMENT 
                rise_rate = Calculations.getDecentRate(P,T,float(radius_parachute),float(mass_balloon)/1000,float(mass_payload)/1000) 
                rise_rate += w_vert 

                #if the balloon payload has reached the terrain_height of its predicted location then it is assumed to be done falling
                if(current_alt <= terrain_height): 
                    done = True 
                    current_alt = terrain_height 
        
        #calculated infromation is added to the three lists returned to WRFDriver.py (points, times, and riseRates)
        latLonAlt = [current_lat, current_lon, current_alt, rise_rate] 
        points.append(latLonAlt) 
        times.append(time)
        riseRates.append(rise_rate)

    wrfFile.close() 
    return points, times, riseRates 

