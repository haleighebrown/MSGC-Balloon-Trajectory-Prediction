from sympy.solvers import solve
from sympy import Symbol
from math import *
import numpy as np

#CONSTANTS
g = 9.81 #m/s^2
EARTH_RADIUS = 6371.0 #km
DEGREES_TO_RADIANS = np.pi/180.0 #simple conversion
RADIANS_TO_DEGREES = 180.0/np.pi #simple conversion
#ALT_INCREMENT = 150.0 #m NOT USED?
PARACHUTE_DRAG = 0.5                         
DRY_AIR_GAS_CONSTANT = 287.058 #J/kgK
MASS_PER_MOLE_HELIUM = 4.0026 #g/mol
MASS_PER_MOLE_AIR = 28.96644 #g/mol
#WRF time index
time = 0
last_Rate = None

#This function returns the new lat and lon of the balloon based on previous location, distance traveled, and bearing data
def destination(distance, bearing, lat, lon):
    #http://www.movable-type.co.uk/scripts/latlong.html
    #distance must be entered as km since EARTH_RADIUS is in km
    lat *= DEGREES_TO_RADIANS #multiplies lat and DEGREES_TO_RAD together and assigns lat to the result
    lon *= DEGREES_TO_RADIANS #same but for lon
    bearing *= DEGREES_TO_RADIANS #same but for the dir we are "facing"

    end_lat = np.arcsin(np.sin(lat)*np.cos(distance/EARTH_RADIUS) + np.cos(lat)*np.sin(distance/EARTH_RADIUS)*np.cos(bearing))
    end_lon = lon + np.arctan2(np.sin(bearing) * np.sin(distance/EARTH_RADIUS) * np.cos(lat), np.cos(distance/EARTH_RADIUS) - np.sin(lat) * np.sin(end_lat))
    end_lon = (end_lon + np.pi) % (2. * np.pi) - np.pi #normalise to -180...+180
    
    end_lat *= RADIANS_TO_DEGREES
    end_lon *= RADIANS_TO_DEGREES
    return end_lat, end_lon


######################################################
#        CALCULATED ASCENT AND DESCENT RATES         #
######################################################


#This function calculates the decent rate of the balloon.
def getDecentRate(pressure, temperature, radius, mass_balloon, mass_payload):
    #area
    A = np.pi * radius**2
    #density
    density = pressure/(temperature * DRY_AIR_GAS_CONSTANT)
    #decent rate
    decent_rate = -np.sqrt(2.0 * g * (mass_payload + 0.7 * mass_balloon)/(A * PARACHUTE_DRAG * density))
    return decent_rate


#This function calculates the ascent rate of the balloon.
def getAscentRate(surface_pressure, surface_temperature, pressure, temperature, mass_balloon, mass_payload, volume_AtLaunch, radius_AtLaunch, last_Rate): 
    #the intial volume comes from the predictedFill function
    V_surface =  float(volume_AtLaunch)
    #V_surface = 4.0/3.0 * np.pi * 0.662432 **3 #<--- this is the previous method for calc starting volume

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

    #this if statement gets an initial rise rate based on the coefficient of drag (cD) for a prefect sphere
    if pressure >= surface_pressure:
        ascent_rate = np.sqrt((2.0 * force_bouyant)/(.48 * cross_area * density))
        last_Rate = ascent_rate

    #this statement invloves the actual calculation of reynolds number and cD
    else:    
        #http://hyperphysics.phy-astr.gsu.edu/hbase/Kinetic/visgas.html
        a = 0.555*(524.07) + 120
        b = 0.555*(temperature*1.8) + 120
        mue_Naught = 0.01827
        air_Viscosity = mue_Naught*a/b*((temperature*1.8)/524.07)**(3/2)
        
        r = ((3*V)/(4*np.pi))**(1/3)

        #conversion factor 1000 (Re has no units so they all need to cancel)

        Re = float(((density*last_Rate*r)/air_Viscosity)*1000)
        cD = 0.04808*(np.log(Re))**2 - 1.406*(np.log(Re)) + 10.49 + .109 #this is our adjustment factor for coefficient of drag as of right now
        
        ascent_rate = np.sqrt((2.0 * force_bouyant)/(cD * cross_area * density))
        last_Rate = ascent_rate

    return ascent_rate, V, last_Rate
    

#This function returns the predicted fill for the balloon based on surface data along with volume and radius at lunach. 
def predictedFill(surface_pressure, surface_temperature, mass_balloon, mass_payload):
    m = Symbol('m')
    he_MolarMass = 0.004  
    air_MolarMass = 0.02896 
    B = 8.314 #GAS CONSTANT
    g = 9.8 #ACCELERATION DUE TO GRAVITY

    #density calculations for air and helium
    he_Density = (surface_pressure * he_MolarMass)/(B * surface_temperature) 
    air_Density = (surface_pressure * air_MolarMass)/(B * surface_temperature) 
  
    #intial v and cD (assuming a desired 5.0 m/s rise rate for the balloon)
    velocity_AtLaunch = 5.68
    Cd = 0.23 

    #rad, area and volume at launch calculations
    radius_AtLaunch = ((3 * m * B * surface_temperature)/(4.0 * pi * he_MolarMass * surface_pressure))**(1.0/3.0) 
    crossArea_AtLaunch = pi * (m * (3 * B * surface_temperature)/(4.0 * pi * he_MolarMass * surface_pressure))**(2.0/3.0) 
    volume_AtLaunch = (m * B * surface_temperature)/(he_MolarMass * surface_pressure) 

    #solving established equations for the mass of helium needed
    Mass = solve(((volume_AtLaunch * g)*(air_Density - he_Density)) - (0.5 * air_Density * (velocity_AtLaunch**2) * Cd * crossArea_AtLaunch) - ((mass_balloon + mass_payload + m) * g), m)[0]
    
    #using new known mass to re calc volume and radius at launch (necessary for ascent rates)
    volume_AtLaunch = (Mass * B * surface_temperature)/(he_MolarMass * surface_pressure)
    radius_AtLaunch = ((3 * Mass * B * surface_temperature)/(4.0 * pi * he_MolarMass * surface_pressure))**(1.0/3.0)
    
    #calculating volume of gas needed
    volGas_AtLaunchM = (Mass * B * surface_temperature)/(he_MolarMass * surface_pressure) 
    volGas_AtLaunchFT = volGas_AtLaunchM/0.0283168 

    #calulating upper and lower fill limits and returning the average value along with volume and radius at luanch 
    fill_PSI = 10.13825 * volGas_AtLaunchFT 
    pf2 = fill_PSI-60 
    liftneeded = 1.5 * mass_payload + (mass_balloon + mass_payload)/28
    mimpostiveLift = 450
    maxpostiveLift = 750
    postiveLift = (mimpostiveLift- liftneeded) + mimpostiveLift 
    cf = (mass_payload * 1000 + mass_balloon * 1000 + 1.5 * mass_payload) / 27.82 
    PSI =  cf * 14.5038
    lowFill = pf2-((pf2-PSI)/16)
    avg_Fill = (lowFill+pf2)/2

    return avg_Fill, volume_AtLaunch, radius_AtLaunch













