"""
File: SIMLA4OBS.py
Description:
This program generates SIMLA input files for on-bottom stability analysis,
runs them and reads and reports the results from the executed analyses.
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2025-06-02"
__maintainer__ = "Egil Giertsen"
__email__ = "giertsen@sintef.no"

import sys
import streamlit as st
import multiprocessing as mp
import os
from rafina import pyraf as pr
import pandas as pd
from PIL import Image
from S4O_Model import *
from S4O_Product import *
from S4O_Seabed import *
from S4O_Environment import *
from S4O_Execution import *
from S4O_Results import *

#
#	SIMLA4OBS main dashboard
#

def main():

	#	Assign SIMLA4OBS version number
	if 'S4O_versionID' not in st.session_state:
		st.session_state.S4O_versionID = 'SIMLA4OBS version 1.0 / 2025'

	#	Set initial model path, directory and name
	if 'modelMainTitle' not in st.session_state:
		st.session_state.modelMainTitle = 'SIMLA4OBS Test Case 01'
	if 'modelFilePath' not in st.session_state:
		st.session_state.modelFilePath = ''
	if 'modelFileDir' not in st.session_state:
		st.session_state.modelFileDir = '.\\'
	if 'modelFileName' not in st.session_state:
		st.session_state.modelFileName = ''

	#	Initialize global function parameters
	if 'Model_OK' not in st.session_state:
		st.session_state.Model_OK = False
	if 'Product_OK' not in st.session_state:
		st.session_state.Product_OK = False
	if 'Seabed_OK' not in st.session_state:
		st.session_state.Seabed_OK = False
	if 'Environment_OK' not in st.session_state:
		st.session_state.Environment_OK = False
	if 'Execution_OK' not in st.session_state:
		st.session_state.Execution_OK = False
	if 'Results_OK' not in st.session_state:
		st.session_state.Results_OK = False

	#	Initialize SIMLA4OBS and SIMLA global parameters
	if 'SIMLA4OBS_PATH' not in st.session_state:
		st.session_state.SIMLA4OBS_PATH = 'P:/Ocean/SIMLA4OBS'
		sys.path.append(st.session_state.SIMLA4OBS_PATH)
	if 'SIMLA_HOME' not in st.session_state:
		#	Set the SIMLA_HOME and HLALIB_PATH environment variables
		st.session_state.SIMLA_HOME = 'C:/SINTEFOcean/SIMLA/SIMLA-3.25.0-win64'
		st.session_state.HLALIB_PATH = st.session_state.SIMLA_HOME + '/bin/HLALib.jar'
		os.environ['SIMLA_HOME'] = st.session_state.SIMLA_HOME
		os.environ['HLALIB_PATH'] = st.session_state.HLALIB_PATH
		#	Add new directories to the PATH variable
		curpath = os.environ.get('PATH')
		newdir = st.session_state.SIMLA_HOME + '/bin'
		os.environ['PATH'] = newdir + os.pathsep + curpath
		curpath = os.environ.get('PATH')
		newdir = st.session_state.SIMLA_HOME + '/jre/jre/bin'
		os.environ['PATH'] = newdir + os.pathsep + curpath
		curpath = os.environ.get('PATH')
		newdir = st.session_state.SIMLA_HOME + '/jre/jre/bin/server'
		os.environ['PATH'] = newdir + os.pathsep + curpath
		#	Assign paths to simla.exe and dynpost.exe
		st.session_state.SIMLA_EXE = st.session_state.SIMLA_HOME + '/bin/simla.exe'		
		st.session_state.DYNPOST_EXE = st.session_state.SIMLA_HOME + '/bin/dynpost.exe'

	#	Assign nstep_dynres as global parameter
	if 'SIMLA_nstep_dynres' not in st.session_state:
		st.session_state.SIMLA_nstep_dynres = int(0)

	#	Initialize additional global application parameters
	if 'CPU_count' not in st.session_state:
		st.session_state.CPU_count = mp.cpu_count()
	if 'maxRunsPB' not in st.session_state:
		st.session_state.maxRunsPB = int(st.session_state.CPU_count/2)
	if 'noBlocksToRun' not in st.session_state:
		st.session_state.noBlocksToRun = 0
	if 'currentRunCount' not in st.session_state:
		st.session_state.currentRunCount = 0
	if 'noRunsPostprocessed' not in st.session_state:
		st.session_state.noRunsPostprocessed = 0
	if 'stdtolRunNumber' not in st.session_state:
		st.session_state.stdtolRunNumber = 0
	if 'listOfSeedNumbers' not in st.session_state:
		st.session_state.listOfSeedNumbers = []
	if 'simlaProgressBar' not in st.session_state:
		st.session_state.simlaProgressBar = ''
	if 'simlaProgressCurr' not in st.session_state:
		st.session_state.simlaProgressCurr = 0
	if 'simlaProgressDelta' not in st.session_state:
		st.session_state.simlaProgressDelta = 0

	#	Initialize run type and extended print switch
	if 'SimulateRuns' not in st.session_state:
		st.session_state.SimulateRuns = False
	if 'ExtendedPrint' not in st.session_state:
		st.session_state.ExtendedPrint = False

	#	Initialize analysis check boxes
	if 'GenerateInputs' not in st.session_state:
		st.session_state.GenerateInputs = True
	if 'RunAnalyses' not in st.session_state:
		st.session_state.RunAnalyses = True
	if 'ResultsCalculated' not in st.session_state:
		st.session_state.ResultsCalculated = False

	#	Initialize options in selectboxes
	if 'SeabedOptions' not in st.session_state:
		st.session_state.SeabedOptions = ['V&S Sand', 'V&L Clay', 'NGI Drained', 'NGI Undrained', 'DNV Model 2 Undrained', 'Rock']
		st.session_state.SeabedValues  = [ 1        ,  2        ,  3           ,  4             ,  5                     ,  6    ]
	if 'PenetrationOptions' not in st.session_state:
		st.session_state.PenetrationOptions = ['Specify', 'Calculate']
		st.session_state.PenetrationValues  = [ 1       ,  2         ]
	if 'WaveSpectraOptions' not in st.session_state:
		st.session_state.WaveSpectraOptions = ['PM', 'JONSWAP']
		st.session_state.WaveSpectraValues  = [ 1  ,  2       ]
	if 'WaveSpreadingOptions' not in st.session_state:
		st.session_state.WaveSpreadingOptions = ['Long-crested', 'Short-crested']
		st.session_state.WaveSpreadingValues  = ['long'        , 'short'        ]
	if 'TSResultOptions' not in st.session_state:
		st.session_state.TSResultOptions = ['None'                            ,
											'Seabed contact force y-dir [N/m]', 'Seabed contact force z-dir [N/m]', 'Hydrodynamic load y-dir [N/m]',
											'Hydrodynamic load z-dir [N/m]'   , 'Displacement y-dir [m]'          , 'Soil penetration z-dir [m]'   ]
		st.session_state.TSResultIDs     = [ 0                                ,
											 1                                ,  2                                ,  3                             ,
											 4                                ,  5                                ,  6                             ]
		st.session_state.TSLineColors    = ['red'    ,'blue'    , 'green'  , 'black'  , 'gray'   , 'purple', 'orange', 'pink'     , 'brown' , 'cyan'  ,
											'magenta','lime'    , 'maroon' , 'navy'   , 'olive'  , 'teal'  , 'aqua'  , 'fuchsia'  , 'gold'  , 'indigo',
											'ivory'  , 'khaki'  ,'lavender', 'plum'   , 'salmon' , 'sienna', 'tan'   , 'turquoise', 'violet']
		st.session_state.TSLineTypes     = ['solid'  , 'dashed' , 'dotted' , 'dotdash', 'dashdot']

	#	Assign default values
	if 'df_Product' not in st.session_state:
		st.session_state.df_Product,st.session_state.Product_OK = S4O_Product_Defaults()
	if 'df_Seabed' not in st.session_state:
		st.session_state.df_Seabed,st.session_state.Seabed_OK = S4O_Seabed_Defaults()
	if 'df_Environment' not in st.session_state:
		st.session_state.df_Environment,st.session_state.Environment_OK = S4O_Environment_Defaults()
	if 'df_Execution' not in st.session_state:
		st.session_state.df_Execution,st.session_state.Execution_OK = S4O_Execution_Defaults()
	if 'df_Results' not in st.session_state:
		st.session_state.df_Results = pd.DataFrame()

	# Initiate the SIMLA4OBS dashboard layout
	st.set_page_config(layout='wide')

	#	SIMLA4OBS dashboard title
	st.title('SIMLA for On-bottom Stability Analysis')
	st.subheader(st.session_state.S4O_versionID)
	if st.session_state.modelMainTitle != '':
		st.subheader('Model title : ' + st.session_state.modelMainTitle)
	if st.session_state.modelFilePath != '':
		st.write('Model file path : ' + st.session_state.modelFilePath)
	st.write("---")

	#	SIMLA4OBS sidebar title
	st.sidebar.title('SIMLA4OBS Menu :')

	#	SIMLA4OBS sidebar task selector
	S4O_Options = ['MODEL','PRODUCT','SEABED','ENVIRONMENT','EXECUTION', 'RESULTS']
	S4O_Task = st.sidebar.selectbox('Select Task :', S4O_Options)
	
	# Repository for images used on Dashboard
	path_images = st.session_state.SIMLA4OBS_PATH
	image = Image.open(path_images + '/s4oimg.png')
	st.sidebar.image(image)

#	Update SIMLA4OBS dashboard with task information
	if(S4O_Task == 'MODEL'):			#	Reads model data into pandas dataframe

		st.session_state.Model_OK = S4O_Model()

	elif(S4O_Task == 'PRODUCT'):		#	Reads product data into pandas dataframe

		st.session_state.df_Product,st.session_state.Product_OK = S4O_Product()

	elif (S4O_Task =='SEABED'):			#	Reads seabed data into pandas dataframe

		st.session_state.df_Seabed,st.session_state.Seabed_OK = S4O_Seabed()

	elif (S4O_Task =='ENVIRONMENT'):	#	Reads enviromental data into pandas dataframe

		st.session_state.df_Environment,st.session_state.Environment_OK = S4O_Environment()

	elif (S4O_Task == 'EXECUTION'):		#	Reads execution data into pandas dataframe

		st.session_state.df_Execution,st.session_state.Execution_OK = S4O_Execution()

	elif (S4O_Task == 'RESULTS'):		#	Reads results into pandas dataframe

		st.session_state.df_Results,st.session_state.Results_OK = S4O_Results()

#
# 	Execute main
#

if __name__ == "__main__":
    main()