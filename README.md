# MSGC-Balloon-Trajectory-Prediction Code
This repository contains working versions of MSGC's Balloon Trajectory Prediction code. This code runs off of Weather Research and Forecasting model (WRF) output files (we recommend hourly increments). 

Instructions for WRF installation and how to generate WRF data can be found here: https://www2.mmm.ucar.edu/wrf/OnLineTutorial/index.php 

After WRF output files are generated for the desired launch time, state their location within the WRFDriver python file found here and run it within a pynio environment. 

This will require that WRFReader, WRFPrediction, and Calculations are also downloaded and stored within the same directory as WRFDriver. 

Running WRFDriver will output three files: prediction.csv, rates.txt, and times.txt within the same directory that it is run. Prediction.csv contains the predicted latitude, longitude, and geopotential of the balloon throughout launch and can be inputted into google earth to provide a comprehensive visualization of the prediction. Rates.txt and times.txt simply contain the rise rates of the balloon and the times at which data is released respectively during the prediction. All three files can be used in python plots such as the ones located in this repository to aid in the comparison between predicted and actual payload flights.


# Installation
This installation guide expects that you have Anaconda install and are running on a Unix system (Linux or Mac)

> conda create --name pyn_env --channel conda-forge pynio python=2.7 


> source activate pyn_env 



The conda create command will set up the create the python environment necessary for this prediction code
The source activate enable the use of this python environment. This command will need to be run every time you open a new terminal unless you set pyn_env as the default python environment.










