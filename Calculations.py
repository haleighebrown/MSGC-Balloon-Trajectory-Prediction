import numpy as np
#from mpl_toolkits.basemap import Basemap
#import matplotlib.pyplot as plt

#CONSTANTS
g = 9.81 #m/s^2
EARTH_RADIUS = 6371.0 #km
DEGREES_TO_RADIANS = np.pi/180.0
RADIANS_TO_DEGREES = 180.0/np.pi
ALT_INCREMENT = 150.0 #m
PARACHUTE_DRAG = 0.5                         #UNITS?
SPHERE_DRAG = 0.48                           #UNITS?
DRY_AIR_GAS_CONSTANT = 287.058 #J/kgK
MASS_PER_MOLE_HELIUM = 4.0026 #g/mol
MASS_PER_MOLE_AIR = 28.96644 #g/mol
#WRF time index
time = 0

def destination(distance, bearing, lat, lon):
    #http://www.movable-type.co.uk/scripts/latlong.html
    #distance must be entered as km since EARTH_RADIUS is in km
    lat *= DEGREES_TO_RADIANS
    lon *= DEGREES_TO_RADIANS
    bearing *= DEGREES_TO_RADIANS

    end_lat = np.arcsin(np.sin(lat) * np.cos(distance/EARTH_RADIUS) + np.cos(lat) * np.sin(distance/EARTH_RADIUS) * np.cos(bearing))
    end_lon = lon + np.arctan2(np.sin(bearing) * np.sin(distance/EARTH_RADIUS) * np.cos(lat), np.cos(distance/EARTH_RADIUS) - np.sin(lat) * np.sin(end_lat))
    end_lon = (end_lon + np.pi) % (2. * np.pi) - np.pi #normalise to -180...+180
    
    end_lat *= RADIANS_TO_DEGREES
    end_lon *= RADIANS_TO_DEGREES
    return end_lat, end_lon

######################################################
#        CALCULATED ASCENT AND DESCENT RATES         #
######################################################
def getDecentRate(pressure, temperature, radius, mass_balloon, mass_payload):
    #area
    A = np.pi * radius**2
    #density
    density = pressure/(temperature * DRY_AIR_GAS_CONSTANT)
    #decent rate
    decent_rate = -np.sqrt(2.0 * g * (mass_payload + 0.7 * mass_balloon)/(A * PARACHUTE_DRAG * density))
    return decent_rate

def getAscentRate(surface_pressure, surface_temperature, pressure, temperature, radius_balloon, mass_balloon, mass_payload):
    #volume of balloon (surface)
    V_surface= 4.0/3.0 * np.pi * radius_balloon**3
    #density
    density = pressure/(temperature * DRY_AIR_GAS_CONSTANT)
    #surface density
    density_surface = surface_pressure/(surface_temperature * DRY_AIR_GAS_CONSTANT)
    #mass of heliums
    mass_helium = MASS_PER_MOLE_HELIUM * V_surface * density_surface / MASS_PER_MOLE_AIR
    #volume (changing with altitude)
    V = V_surface * density_surface / density
    #ascent rate calculation
    force_bouyant = (V * density * g) - ((mass_payload + mass_balloon + mass_helium) * g)
    cross_area = np.pi * (3.0 * V/(4.0 * np.pi))**(2.0/3.0)
    ascent_rate = np.sqrt((2.0 * force_bouyant)/(SPHERE_DRAG * cross_area * density))
    return ascent_rate

######################################################
#          SPECIFIC ASCENT AND DESCENT RATES         #
######################################################
def getRiseRate(alt, ascent):
    ascent_rates = [[2000,5.17],\
            [3000,6.8],\
            [4000,6.8],\
            [5000,6.8],\
            [6000,6.8],\
            [7000,6.8],\
            [8000,6.8],\
            [9000,6.8],\
            [10000,6.8],\
            [11000,6.8],\
            [12000,6.8],\
            [13000,6.8],\
            [14000,4.5],\
            [15000,4.49],\
            [16000,4.51],\
            [17000,4.51],\
            [18000,4.5],\
            [19000,4.51],\
            [20000,4.5],\
            [21000,4.5],\
            [22000,4.5],\
            [23000,4.5],\
            [24000,4.5],\
            [25000,4.5],\
            [26000,4.5],\
            [27000,4.5],\
            [28000,4.5]]
    descent_rates = [[30000,-36.0],\
            [28000,-31.0],\
            [26000,-27.0],\
            [24000,-23.0],\
            [22000,-20.0],\
            [20000,-18.0],\
            [18000,-15.0],\
            [16000,-13.0],\
            [14000,-10.0],\
            [12000,-9.0],\
            [10000,-8.0],\
            [8000,-7.0],\
            [6000,-6.0],\
            [4000,-4.50]]
    if ascent:
        rise_rates = ascent_rates
    else:
        rise_rates = descent_rates
    rise_rate = 0
    getRiseRate_error = 0
    getRiseRate_previous_error = 9999
    for i in range(len(rise_rates)):
        getRiseRate_error = abs(alt - rise_rates[i][0])
        if getRiseRate_error < getRiseRate_previous_error:
            rise_rate = rise_rates[i][1]
            getRiseRate_previous_error = getRiseRate_error
    return rise_rate

def getRiseRateSmall(alt, ascent):
    ascent_rates = [[2.00000000e3, 4.34163265],\
             [3.00000000e3, 6.77258065],\
             [4.00000000e3, 5.88378378],\
             [5.00000000e3, 4.51414141],\
             [6.00000000e3, 4.30990099],\
             [7.00000000e3, 4.02710280],\
             [8.00000000e3, 4.45700000],\
             [9.00000000e3, 3.88684211],\
             [1.00000000e4, 4.11047619],\
             [1.10000000e4, 4.24752475],\
             [1.20000000e4, 4.69791667],\
             [1.30000000e4, 4.42346939],\
             [1.40000000e4, 4.77362637],\
             [1.50000000e4, 4.76526316],\
             [1.60000000e4, 4.70686275],\
             [1.70000000e4, 5.08395062],\
             [1.80000000e4, 5.04333333],\
             [1.90000000e4, 4.99647059],\
             [2.00000000e4, 5.06250000],\
             [2.10000000e4, 5.10481928],\
             [2.20000000e4, 5.41025641],\
             [2.30000000e4, 5.29638554],\
             [2.40000000e4, 5.23278689]]
    descent_rates = [[2.00000000e3, -5.37333333],\
             [3.00000000e3, -6.56600000],\
             [4.00000000e3, -6.06031746],\
             [5.00000000e3, -6.37540984],\
             [6.00000000e3, -6.50169492],\
             [7.00000000e3, -6.49333333],\
             [8.00000000e3, -6.78771930],\
             [9.00000000e3, -7.23584906],\
             [1.00000000e4, -8.12978723],\
             [1.10000000e4, -8.79772727],\
             [1.20000000e4, -9.69750000],\
             [1.30000000e4, -1.05189189e1],\
             [1.40000000e4, -1.11424242e1],\
             [1.50000000e4, -1.22093750e1],\
             [1.60000000e4, -1.35629630e1],\
             [1.70000000e4, -1.47153846e1],\
             [1.80000000e4, -1.54153846e1],\
             [1.90000000e4, -1.68909091e1],\
             [2.00000000e4, -1.84500000e1],\
             [2.10000000e4, -2.01000000e1],\
             [2.20000000e4, -2.19764706e1],\
             [2.30000000e4, -2.22875000e1],\
             [2.40000000e4, -2.29400000e1]]
    if ascent:
        rise_rates = ascent_rates
    else:
        rise_rates = descent_rates
    rise_rate = 0
    getRiseRate_error = 0
    getRiseRate_previous_error = 9999
    for i in range(len(rise_rates)):
        getRiseRate_error = abs(alt - rise_rates[i][0])
        if getRiseRate_error < getRiseRate_previous_error:
            rise_rate = rise_rates[i][1]
            getRiseRate_previous_error = getRiseRate_error
    return rise_rate

def getRiseRateTest(alt, ascent):
    ascent_rates = [[2000,2.],\
            [3000,2.],\
            [4000,2.],\
            [5000,2.],\
            [6000,2.],\
            [7000,2.25],\
            [8000,2.5],\
            [9000,2.75],\
            [10000,2.75],\
            [11000,2.75],\
            [12000,2.75],\
            [13000,2.75],\
            [14000,2.5],\
            [15000,2.5],\
            [16000,2.75],\
            [17000,3.],\
            [18000,3.5],\
            [19000,3.75],\
            [20000,3.8],\
            [21000,4.89],\
            [22000,5.0],\
            [23000,5.],\
            [24000,5.],\
            [25000,5.],\
            [26000,5.37],\
            [27000,5.43],\
            [28000,5.53]]
    descent_rates = [[30000,-.1],\
            [28000,-.1],\
            [26000,-.125],\
            [24000,-.15],\
            [22000,-.2],\
            [20000,-.325],\
            [18000,-.3],\
            [16000,-.3],\
            [14000,-.3],\
            [12000,-.325],\
            [10000,-.35],\
            [8000,-.4],\
            [6000,-.4],\
            [4000,-.4]]
    if ascent:
        rise_rates = ascent_rates
    else:
        rise_rates = descent_rates
    rise_rate = 0
    getRiseRate_error = 0
    getRiseRate_previous_error = 9999
    for i in range(len(rise_rates)):
        getRiseRate_error = abs(alt - rise_rates[i][0])
        if getRiseRate_error < getRiseRate_previous_error:
            rise_rate = rise_rates[i][1]
            getRiseRate_previous_error = getRiseRate_error
    return rise_rate

def getRiseRateRadiosonde(alt, ascent, filename):
    values = np.genfromtxt(filename, dtype=float, usecols=(8,12), skip_header=1)
    ascent_rates = np.array([num for num in values if num[1] >= 0.5]) 
    descent_rates = np.array([num for num in values if num[1] < -0.5]) 
    if ascent:
        rise_rates = ascent_rates
    else:
        rise_rates = descent_rates
    rise_rate = 0
    getRiseRate_error = 0
    getRiseRate_previous_error = 9999
    for i in range(len(rise_rates)):
        getRiseRate_error = abs(alt - rise_rates[i][0])
        if getRiseRate_error < getRiseRate_previous_error:
            rise_rate = rise_rates[i][1]
            getRiseRate_previous_error = getRiseRate_error
    return rise_rate
######################################################

#def Plotting(points, sizex, sizey):
    points = np.array(points)
    x = points[:,1]
    y = points[:,0]
    z = points[:,2]
    m = Basemap(width=sizex, height=sizey, projection='lcc', lon_0=points[0][1], lat_0=points[0][0], resolution='i')
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.fillcontinents(color='#cc9966', lake_color='#99ffff')
    x,y = m(x,y)
    m.plot(x,y, 'r-')
    for i in range(len(z)-1):
        if z[i+1] < z[i]:
            m.plot(x[i], y[i], 'bo')
            break
    plt.text(x[len(x)-1], y[len(y)-1],
             str(points[len(y)-1,0]) + ', ' + str(points[len(x)-1,1]),
             horizontalalignment='center', verticalalignment='center')
    plt.show()
