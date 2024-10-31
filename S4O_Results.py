"""
File: S4O_Results.py
Description:
These functions initiates and updates the df_Results pandas dataframe.
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
import random
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

#
#	RESULTS input function
#

def S4O_Results():

	#	Set Streamlit subtitle
	st.header('Analysis results')

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)

	#	Check if the current model exists and is valid
	file_name = st.session_state.modelFileName
	file_path = st.session_state.modelFilePath
	if file_name == '' or file_path == '' or not os.path.exists(file_path):
		st.error("You have to select a valid model before you can show results!", icon="🚨")
		return st.session_state.df_Results,st.session_state.Results_OK

	if Echo_Inputs:
		#	Echo of input data
		st.write("---")
		st.subheader('Echo of input parameters')
		st.write("Product parameters :")
		st.write(st.session_state.df_Product)
		st.write("Seabed parameters :")
		st.write("Seabed model : " + st.session_state.SeabedOptions[int(st.session_state.df_Seabed.iloc[0,1])])
		st.write("Initial penetration mode : " + st.session_state.PenetrationOptions[int(st.session_state.df_Seabed.iloc[10,1])])
		st.write(st.session_state.df_Seabed)
		st.write("Environment parameters :")
		st.write("Selected wave spectrum : " + st.session_state.WaveSpectraOptions[int(st.session_state.df_Environment.iloc[4,1])])
		st.write("Selected wave spreading : " + st.session_state.WaveSpreadingOptions[int(st.session_state.df_Environment.iloc[6,1])])
		st.write(st.session_state.df_Environment)
		st.write("Execution parameters :")
		st.write(st.session_state.df_Execution)

	#	If fake runs, generate results from pre-generated DYNPOST EXT files
	if st.session_state.FakeRuns: S4O_Generate_Results()

	#	Check if the pandas Results dataframe is empty
	if st.session_state.df_Results.empty:
		st.error("No results available!", icon="🚨")
		return st.session_state.df_Results,st.session_state.Results_OK
	
	#	Print results
	st.write("---")
	st.subheader('Lateral displacement statistics ($d_{y}$) [m]')
	st.write("Table 1 : Results summary.")
	st.write(st.session_state.df_Results)

	ptol = float(st.session_state.df_Execution.iloc[3,1])
	if st.session_state.stdtolRunNumber != 0:
		st.info('Specified maximum change in standard deviation (' + str(ptol) + '%) reached after ' + str(st.session_state.stdtolRunNumber) + ' runs.')
	else:
		if ptol != 0.0: st.warning('Specified maximum change in standard deviation (' + str(ptol) + '%) not reached for number of runs available (' + str(st.session_state.noRunsPostprocessed) + ')!', icon="⚠️")

	S4O_Show_Results_Plot()

	st.session_state.Results_OK = True

	return st.session_state.df_Results,st.session_state.Results_OK
#
#

def S4O_Generate_Results():

	#	Initialize pandas Results dataframe
	st.session_state.df_Results = pd.DataFrame()

	#	Build DYNPOST file names
	ndir = st.session_state.modelFileDir
	nmod = st.session_state.modelFileName
	max_path = ndir + "/" + nmod + "/disp-uy-max.txt"
	min_path = ndir + "/" + nmod + "/disp-uy-min.txt"

	#	Check if DYNPOST files exist
	if not os.path.exists(max_path):
		st.error("Max file does not exist!", icon="🚨")
		return

	if not os.path.exists(min_path):
		st.error("Min file does not exist!", icon="🚨")
		return

	#	Open DYNPOST files and read max and min results
	fmax = open(max_path, "r")
	maxlines = fmax.readlines()
	fmax.close()	
	fmin = open(min_path, "r")
	minlines = fmin.readlines()
	fmin.close()

	if len(maxlines) != len(minlines):
		st.error("Max and Min files does not contain the same number of lines!", icon="🚨")
		return

	#	Generate list of results
	runlist = []
	meanlist = []
	stdlist = []
	dstdlist = []
	m1stdlist = []
	maxmalist = []
	maxlist = []
	minlist = []

	irun = 0
	for iline in range(len(maxlines)):

		if iline > 1:

			#	Increment and append current run number
			irun += 1
			runlist.append(irun)

			#	Extract max and min values from current lines in DYNPOST output files
			clmax = maxlines[iline]
			clmax = clmax.strip()
			colmax = clmax.split()
			clmin = minlines[iline]
			clmin = clmin.strip()
			colmin = clmin.split()
			maxval = float(colmax[1])
			minval = float(colmin[1])

			#	Append lists with absolute maxima, max and min values
			maxmalist.append(max(abs(maxval),abs(minval)))
			maxlist.append(maxval)
			minlist.append(minval)

			#	Calculate and append mean so far from the list with absolute maxima values
			if irun == 1:
				meanlist.append(maxmalist[irun-1])
			else:
				meanlist.append(np.mean(maxmalist[0:irun]))

			#	Calculate and append standard deviation so far from the list with mean values
			if irun == 1:
				stdlist.append(0.0)
			else:
				stdlist.append(np.std(meanlist[0:irun]))

			#	Calculate and append mean+1std so far from the list with absolute maxima values
			m1stdlist.append((meanlist[irun-1] + stdlist[irun-1]))

			#	Calculate change in standard deviation
			pdiff = 0.0
			if irun > 1:
				std1 = stdlist[irun-2]
				std2 = stdlist[irun-1]
				diff = abs(std2-std1)
				if std1 != 0.0:
					pdiff = (diff/std1)*100
				elif std1 == 0.0 and std2 != 0.0:
					pdiff = 100.0
			dstdlist.append(pdiff)

	#	Check change in standard deviation
	tolno = 0
	ptol = float(st.session_state.df_Execution.iloc[3,1])
	for ndx in range(len(dstdlist)):
		if ndx > 0 and ptol != 0.0 and dstdlist[ndx] < ptol:
			tolno = runlist[ndx]
			break

	#	Assign number of runs processed
	nruns = irun
	st.session_state.noRunsPostprocessed = nruns

	#	Assign run number for which tolerance was reached
	if tolno > 0:
		st.session_state.stdtolRunNumber = tolno
	else:
		st.session_state.stdtolRunNumber = 0

	#	Build pandas Results dataframe
	st.session_state.df_Results['Sea state'] = runlist
	st.session_state.df_Results['Mean'] = meanlist
	st.session_state.df_Results['StdDev'] = stdlist
	st.session_state.df_Results['ΔStdDev [%]'] = dstdlist
	st.session_state.df_Results['Mean+1StdDev'] = m1stdlist
	st.session_state.df_Results['Maxima'] = maxmalist
	st.session_state.df_Results['Max'] = maxlist
	st.session_state.df_Results['Min'] = minlist

	return
#
#

def S4O_Show_Results_Plot():

	#	Check if the pandas Results dataframe is empty
	if st.session_state.df_Results.empty:
		st.error("No results available!", icon="🚨")
		return

	#	Assign list of results
	runlist = []
	meanlist = []
	stdlist = []
	m1stdlist = []
	maxmalist = []

	nruns = st.session_state.df_Results.shape[0]
	for irun in range(nruns):
		runlist.append(int(st.session_state.df_Results.iloc[irun,0]))
		meanlist.append(float(st.session_state.df_Results.iloc[irun,1]))
		stdlist.append(float(st.session_state.df_Results.iloc[irun,2]))
		m1stdlist.append(float(st.session_state.df_Results.iloc[irun,4]))
		maxmalist.append(float(st.session_state.df_Results.iloc[irun,5]))

	#	Assign value for absolute maxima
	mval = np.max(maxmalist)

	#	Assign design value
	dval = float(st.session_state.df_Execution.iloc[4,1])*float(st.session_state.df_Product.iloc[0,1])

	#	Build and show pyplot plot
	plt.close("all")
	st.write("---")
	st.subheader('Lateral displacement ($d_{y}$) versus number of sea states')
	plt.plot(runlist[1:nruns], m1stdlist[1:nruns], color='b', marker='v', linewidth=1, linestyle='solid', label='Mean+1SD $d_{y,max}$')
	plt.plot(runlist, meanlist, color='b', linewidth=1, linestyle='dashed', label='Mean $d_{y,max}$')
	plt.axhline(y=dval, color='r', linewidth=1, linestyle='dashed', label='Design value $d_{y}$')
	plt.legend(loc='lower right')
	plt.xticks(range(1, nruns*2, 2))
	plt.xlim([0, nruns+1])
	plt.ylim([0, 1.1*max(dval, mval)])
	plt.xlabel('Number of sea state realisations')
	plt.ylabel('Lateral displacement $d_{y}$ [m]')
	st.pyplot(plt)
	st.write("Figure 1 : Lateral displacement ($d_{y}$) versus number of sea states.")

	return
#
#

# Define the displacement statistics table formatting function
def custom_format_displacements(x):
	if isinstance(x, float):
		return '{:.4f}'.format(x)
	else:
		return x
