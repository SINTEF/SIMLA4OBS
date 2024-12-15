"""
File: S4O_Execution.py
Description:
These functions initiates and updates the df_Execution pandas dataframe, runs SIMLA executions and reads and processes results.
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2024"
__maintainer__ = "Egil Giertsen"
__email__ = "giertsen@sintef.no"

import pandas as pd
import streamlit as st
import os
from S4O_SIMLA import *

#
#	EXECUTION input function
#

def S4O_Execution():

	#	Set Streamlit subtitle
	st.header('Execution parameters')

	#	Set ResultsCalculated to False 
	st.session_state.ResultsCalculated = False

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)
	
	#	Assign execution parameters
	if 'df_Execution' not in st.session_state:
		st.warning('S4O_Execution : Should not be here!', icon="⚠️")
	else:
		tsSize = float(st.session_state.df_Execution.iloc[0,1])
		seaDur = float(st.session_state.df_Execution.iloc[1,1])
		wlRamp = float(st.session_state.df_Execution.iloc[2,1])
		maxRel = st.session_state.currentMaxRel
		sdTol  = float(st.session_state.df_Execution.iloc[4,1])
		odFac  = float(st.session_state.df_Execution.iloc[5,1])

	#	Prompt for execution parameters
	tsSize = st.number_input("Time step size in dynamic analysis [s] :", min_value=0.0, value=tsSize, format="%.4f")
	seaDur = st.number_input("Sea state duration [h] :", min_value=0.0, value=seaDur, format="%.2f")
	wlRamp = st.number_input("Wave load ramping time [s] :", min_value=1.0, value=wlRamp, format="%.1f")
	maxRel = st.number_input("Maximum number of sea state realisations [-] :", min_value=1, value=maxRel, format="%i")
	sdTol  = st.number_input("Maximum change in standard deviation [%] :",
							 help="Maximum percentage change in standard deviation of the calculated maximum lateral displacement [%]. Set value to zero (0) if you want to run through all sea states.",
							 min_value=0.0, value=sdTol, format="%.2f")
	odFac  = st.number_input("Design curve value as factor of outer diameter [-] :",
							 help="Set value to zero (0.0) if you do not want to add a design curve.",
							 min_value=0.0, value=odFac, format="%.1f")

	if st.session_state.modelFilePath == '':
		st.session_state.currentMaxRel = maxRel
	elif maxRel != int(st.session_state.df_Execution.iloc[3,1]) and os.path.exists(st.session_state.modelFilePath):
		st.warning('The changed maximum number of realisations ('+str(maxRel)+') does not take effect before you save your model on a new file!', icon="⚠️")
		st.session_state.currentMaxRel = maxRel
		maxRel = int(st.session_state.df_Execution.iloc[3,1])
	else:
		st.session_state.currentMaxRel = maxRel

	# Update df_Execution dataframe
	Exdata = [['Time step size in dynamic analysis [s] :', tsSize], ['Sea state duration [h] :', seaDur], ['Wave load ramping time [s] :', wlRamp],
			  ['Maximum number of realisations [-] :', maxRel], ['Maximum change in standard deviation [%] :', sdTol], ['Design curve value as factor of outer diameter [-] :', odFac]]
	st.session_state.df_Execution = pd.DataFrame(Exdata, columns=['Execution parameters','Value'])
	
	#	Assign total number of blocks to run
	st.session_state.noBlocksToRun = int(maxRel/st.session_state.maxRunsPB)
	if (maxRel % st.session_state.maxRunsPB) > 0: st.session_state.noBlocksToRun += 1

	#	Display check boxes for generation of input files and/or running of analyses
	st.write("---")
	st.session_state.GenerateInputs = st.checkbox('Generate input files', value=st.session_state.GenerateInputs)
	st.session_state.RunAnalyses = st.checkbox('Run analyses', value=st.session_state.RunAnalyses)
	st.session_state.ExtendedPrint = st.checkbox('Extended print', value=st.session_state.ExtendedPrint)

	#	Start SIMLA button
	st.write("")
	run = st.button("Run SIMLA", key=None, help="Run SIMLA in batch mode")

	#	Run SIMLA
	if run:
		S4O_Run_SIMLA()

	#	Echo df_Execution dataframe
	if Echo_Inputs:
		st.write("---")
		st.write("Stored execution parameters :")
		st.write(st.session_state.df_Execution)
		st.write('Execution Ok: ', st.session_state.Execution_OK)

	st.session_state.Execution_OK = True

	return st.session_state.df_Execution,st.session_state.Execution_OK
#
#

#
# EXECUTION set defaults function
#

def S4O_Execution_Defaults():
	
	#	Assign default execution parameters
	if 'df_Execution' not in st.session_state:
		tsSize = 0.02
		seaDur = 0.15
		wlRamp = 5.0
		maxRel = 7
		sdTol = 0.0
		odFac = 10.0
	else:
		st.warning('S4O_Execution_Defaults : Should not be here (1)!', icon="⚠️")

	if 'currentMaxRel' not in st.session_state:
		st.session_state.currentMaxRel = maxRel
	else:
		st.warning('S4O_Execution_Defaults : Should not be here (2)!', icon="⚠️")

	Exdata = [['Time step size in dynamic analysis [s] :', tsSize], ['Sea state duration [h] :', seaDur], ['Wave load ramping time [s] :', wlRamp],
			  ['Maximum number of realisations [-] :', maxRel], ['Maximum change in standard deviation [%] :', sdTol], ['Design curve value as factor of outer diameter [-] :', odFac]]
	st.session_state.df_Execution = pd.DataFrame(Exdata, columns=['Execution parameters','Value'])

	st.session_state.Execution_OK = True

	return st.session_state.df_Execution,st.session_state.Execution_OK
#
#
