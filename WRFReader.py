import Nio
import numpy as np

#CONSTANTS
g = 9.81 #m/s**2
EARTH_RADIUS = 6371.0 #km
DEGREES_TO_RADIANS = np.pi/180.0
RADIANS_TO_DEGREES = 180.0/np.pi
#WRF time index
time = 0

#NOTE: in the WRF Users Guide pages 212 and 213 should have all
#   WRF perturbation correction equations. (section 5 page 112/113)

def openWRF(main_directory, file_name):
    try:
        wrf = Nio.open_file(main_directory + file_name, format='nc')
        return wrf
    except:
        print ('Failure when opening WRF file')
    quit()

def findNetCDFLatLonIndex(wrf, lat, lon):
    lats = wrf.variables['XLAT'][time,:,:]
    lons = wrf.variables['XLONG'][time,:,:]
    error_lat = 0
    error_lon = 0
    previous_error_lat = 9999
    previous_error_lon = 9999
    index_i=0
    index_j=0
    for j in range(len(lats)):
        for i in range(len(lats[j])):
            error_lat = abs(lat - lats[j][i])
            error_lon = abs(lon - lons[j][i])
            if ((error_lat + error_lon) < (previous_error_lat + previous_error_lon)):
                index_i = i
                index_j = j
                previous_error_lat = error_lat
                previous_error_lon = error_lon
    return index_i, index_j
def findNetCDFAltIndex(wrf, index_i, index_j, alt):
    PH = wrf.variables["PH"][time,:,index_j,index_i]
    PHB = wrf.variables["PHB"][time,:,index_j,index_i]
    ALT = [(0.5*(PHB[i] + PH[i] + PH[i+1] + PHB[i+1])/g) for i in range(len(PH)-1)]
    error = 0
    previous_error = 9999
    index_k = 0
    for k in range(len(ALT)):
        error = abs(alt - ALT[k])
        if  error < previous_error:
            index_k = k
            previous_error = error
    return index_k

def getWindSpeedAndDirection(wrf, index_i, index_j, index_k):
    #Website for unstaggering
    #http://www.openwfm.org/wiki/How_to_interpret_WRF_variables
    U = (wrf.variables["U"][time, index_k, index_j, index_i] + wrf.variables["U"][time, index_k, index_j, index_i + 1]) * 0.5
    V = (wrf.variables["V"][time, index_k, index_j, index_i] + wrf.variables["V"][time, index_k, index_j + 1, index_i]) * 0.5
    W = (wrf.variables["W"][time, index_k, index_j, index_i] + wrf.variables["W"][time, index_k + 1, index_j, index_i]) * 0.5
    COSALPHA = wrf.variables["COSALPHA"][time, index_j, index_i]
    SINALPHA = wrf.variables["SINALPHA"][time, index_j, index_i]
    U = U*COSALPHA - V*SINALPHA
    V = V*COSALPHA + U*SINALPHA
    windDir = RADIANS_TO_DEGREES * np.arctan2(U, V)
    windSpd = np.sqrt(U**2 + V**2)
    windVertical = W
    return windSpd, windDir, windVertical

def getTerrainHeight(wrf, index_i, index_j):
    HGT = wrf.variables["HGT"][time, index_j, index_i]
    return HGT

def getHydPressure(wrf, index_i, index_j, index_k):
    P_HYD = wrf.variables["P_HYD"][time, index_k, index_j, index_i] #Pa
    pressure = P_HYD #Pa
    return pressure

def getPressure(wrf, index_i, index_j, index_k):
    P = wrf.variables["P"][time,index_k,index_j,index_i] #perturbation pressure
    PB = wrf.variables["PB"][time,index_k,index_j,index_i]
    pressure = P + PB #Pa
    return pressure

def getTemperature(wrf, index_i, index_j, index_k):
    #Convert from perturbation potential temperature to temperature
    #http://mailman.ucar.edu/pipermail/wrf-users/2010/001896.html
    #Step 1: convert to potential temperature by adding 300
    #Step 2: convert potential temperatuer to temperature
    #   https://en.wikipedia.org/wiki/Potential_temperature
    #   Note: p_0 = 1000. hPa and R/c_p = 0.286 for dry air
    T = wrf.variables["T"][time, index_k, index_j, index_i]
    potential_temp = T + 300 #K
    pressure = getPressure(wrf, index_i, index_j, index_k) #Pa
    temperature = potential_temp * (pressure/100000.)**(0.286) #K
    return temperature

