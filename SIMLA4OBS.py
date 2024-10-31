"""
File: SIMLA4OBS.py
Description:
This program generates SIMLA input files for on-bottom stability analysis,
runs them and reads and reports the results from the executed analyses.
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2024"
__maintainer__ = "Egil Giertsen"
__email__ = "giertsen@sintef.no"

import sys
import pandas as pd
import streamlit as st
import multiprocessing as mp
import os
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
		st.session_state.S4O_versionID = 'SIMLA4OBS version 0.3 / 2024'

	#	Set initial model path, directory and name
	if 'modelMainTitle' not in st.session_state:
		st.session_state.modelMainTitle = 'SIMLA4OBS Test Case 01'
	if 'modelFilePath' not in st.session_state:
		st.session_state.modelFilePath = 'C:/Users/vegardl/Documents/SIMLA4OBS/case1.s4o'
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
	if 'SIMLA4OBS_path' not in st.session_state:
		st.session_state.SIMLA4OBS_path = 'C:/302004604-simla/deepline/streamlit/'
		sys.path.append(st.session_state.SIMLA4OBS_path)
	if 'SIMLA_HOME' not in st.session_state:
		#	Set the SIMLA_HOME and HLALIB_PATH environment variables
		st.session_state.SIMLA_HOME = 'C:/Program Files/SIMLA-3.23.2'
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

	#	Initialize addiitonal global application parameters
	if 'CPU_count' not in st.session_state:
		st.session_state.CPU_count = mp.cpu_count()
	if 'maxRunsPB' not in st.session_state:
		st.session_state.maxRunsPB = int(st.session_state.CPU_count/3)
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
	if 'FakeRuns' not in st.session_state:
		st.session_state.FakeRuns = True
	if 'ExtendedPrint' not in st.session_state:
		st.session_state.ExtendedPrint = True

	#	Initialize analysis check boxes
	if 'GenerateInputs' not in st.session_state:
		st.session_state.GenerateInputs = True
	if 'RunAnalyses' not in st.session_state:
		st.session_state.RunAnalyses = True

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
	path_images = st.session_state.SIMLA4OBS_path + '/images'
	image = Image.open(path_images + '/simla4obs.png')
	st.sidebar.image(image)

#	Update SIMLA4OBS dashboard with task information
	if(S4O_Task == 'MODEL'):			#	Reads model data into pandas dataframe

		st.session_state.Model_OK = S4O_Model()

	elif(S4O_Task == 'PRODUCT'):		#	Reads product data into pandas dataframe

		st.session_state.df_Product,st.session_state.Product_OK = S4O_Product()

	elif (S4O_Task =='SEABED'):			#	Reads seabed data into pandas dataframee

		st.session_state.df_Seabed,st.session_state.Seabed_OK = S4O_Seabed()

	elif (S4O_Task =='ENVIRONMENT'):	#	Reads enviromental data into pandas dataframee

		st.session_state.df_Environment,st.session_state.Environment_OK = S4O_Environment()

	elif (S4O_Task == 'EXECUTION'):		#	Reads execution data into pandas dataframe

		st.session_state.df_Execution,st.session_state.Execution_OK = S4O_Execution()

	elif (S4O_Task == 'RESULTS'):		#	Reads results into pandas dataframe

		st.session_state.df_Results,st.session_state.Results_OK = S4O_Results()

#
#	Save to EXCEL?
#
#	st.session_state.Export_to_EXCEL = st.sidebar.checkbox('Export data to EXCEL',value=False)
	st.session_state.Export_to_EXCEL = False

	if st.session_state.Export_to_EXCEL:

		df_Info = pd.DataFrame(
		    {'Pipe': ['Start', 'Stop'],
		     'Latitude': [63.464, 63.4537, ],
		     'Longitude': [9.935, 10.3756]})

		with pd.ExcelWriter('SIMLA4OBS output.xlsx') as writer: 
			df_Info.to_excel(writer, sheet_name='SIMLA4OBS route information')
			if st.session_state.Product_OK:
				st.session_state.df_Product.to_excel(writer, sheet_name='SIMLA4OBS Product')
			if st.session_state.Seabed_OK:
				st.session_state.df_Seabed.to_excel(writer, sheet_name='SIMLA4OBS Seabed')
			if st.session_state.Environment_OK:
				st.session_state.df_Environment.to_excel(writer, sheet_name='SIMLA4OBS Enviroment')
			if st.session_state.Execution_OK:
				st.session_state.df_Execution.to_excel(writer, sheet_name='SIMLA4OBS Execution')
			if st.session_state.Results_OK:
				st.session_state.df_Results.to_excel(writer, sheet_name='SIMLA4OBS Results')

#
# 	Execute main
#

if __name__ == "__main__":
    main()