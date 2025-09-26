"""
File: S4O_Results.py
Description:
These functions initiates and updates the df_Results pandas dataframe.
Revisions:
2025-09-19: S4O_ReadTSArrays, S4O_ReadTSMaxMin; Cleaned up wording and code related to "Assign index to the last non-zero time value".
2025-09-23: S4O_ReadTSArrays, S4O_ReadTSMaxMin; Added "ndxstart" as input parameter to be able to remove the "static configuration + wave load ramping time" from the time series if specified by the user.
2025-09-23: S4O_Show_TS_Plot; Added checkbox "Include wave load ramping time". Default = True.
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2025-03-27"
__maintainer__ = "Egil Giertsen"
__email__ = "Egil.Giertsen@sintef.no"

import streamlit as st
import os
import random
import math
import numpy as np
from rafina import pyraf as pr
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.models import Title
from bokeh.models import HoverTool

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

	#	Assign number of runs
	nruns = int(st.session_state.df_Execution.iloc[3,1])

	#	Echo of input data
	if Echo_Inputs:
		st.write("---")
		st.subheader('Echo of input parameters')
		st.write("Product parameters :")
		st.write(st.session_state.df_Product)
		st.write("Seabed parameters :")
		st.write("Seabed model - y-direction : " + st.session_state.SeabedOptions[int(st.session_state.df_Seabed.iloc[0,1])])
		st.write("Seabed model - z-direction : " + st.session_state.SeabedOptions[int(st.session_state.df_Seabed.iloc[9,1])])
		st.write("Initial penetration mode : " + st.session_state.PenetrationOptions[int(st.session_state.df_Seabed.iloc[14,1])])
		st.write(st.session_state.df_Seabed)
		st.write("Environment parameters :")
		st.write("Selected wave spectrum : " + st.session_state.WaveSpectraOptions[int(st.session_state.df_Environment.iloc[4,1])])
		st.write("Selected wave spreading : " + st.session_state.WaveSpreadingOptions[int(st.session_state.df_Environment.iloc[6,1])])
		st.write(st.session_state.df_Environment)
		st.write("Execution parameters :")
		st.write(st.session_state.df_Execution)

	#	If simulate runs, generate results from pre-generated DYNPOST files
	if st.session_state.SimulateRuns: S4O_Generate_Results(nruns)

	#	Check if SIMLA has already been executed, and if yes generate results from existing DYNPOST files
	if not st.session_state.ResultsCalculated and S4O_CheckIfSIMLARunsExist(nruns):
		#	Generate results
		S4O_Generate_Results(nruns)

	#	Check if the pandas Results dataframe is empty
	if st.session_state.df_Results.empty:
		st.error("No results available!", icon="🚨")
		return st.session_state.df_Results,st.session_state.Results_OK
	
	#	Print results
	#	-------------
	st.write("---")
	#	Display the "Recalculate" button
	recalculate = st.button("Recalculate time series statistics")
	if recalculate:
		st.session_state.ResultsCalculated = False
		st.session_state.stdtolRunNumber = 0
		S4O_Generate_Results(nruns)

	#	Write results table
	st.subheader('Lateral displacement statistics ($u_{y}$) [m]')
	st.write("Table 1 : Results summary.")
	st.write(st.session_state.df_Results)

	ptol = float(st.session_state.df_Execution.iloc[4,1])
	if st.session_state.stdtolRunNumber != 0:
		st.info('Specified maximum change in standard deviation (' + str(ptol) + '%) reached after ' + str(st.session_state.stdtolRunNumber) + ' runs.')
	else:
		if ptol != 0.0: st.warning('Specified maximum change in standard deviation (' + str(ptol) + '%) not reached for number of runs available (' + str(st.session_state.noRunsPostprocessed) + ')!', icon="⚠️")

	S4O_Show_Results_Plot()

	S4O_Show_TS_Plot()

	st.session_state.Results_OK = True

	return st.session_state.df_Results,st.session_state.Results_OK
#
#

def S4O_Generate_Results(lrun):

	#	Check if time series statistics have already been calculated
	if st.session_state.ResultsCalculated: return

	#	Initialize pandas Results dataframe
	st.session_state.df_Results = pd.DataFrame()

	#	Check that at least one realisation has been run
	if lrun <= 0: return

	#	Assign model path
	mod_path = st.session_state.modelFileDir + "/" + st.session_state.modelFileName

	#	Generate list of results for displacement in y direction (tsid=5)
	#	-----------------------------------------------------------------
	tsid = 5

	#	Initialize temporary result arrays
	runlist = []
	meanlist = []
	stdlist = []
	dstdlist = []
	m1stdlist = []
	maxmalist = []
	maxlist = []
	minlist = []

	#	Initialise progress bar
	tsProgressCurr = int(0)
	tsProgressDelta = int(100/lrun)
	tsProgressBar = st.progress(tsProgressCurr)

	#	Loop over all realisations (runs)
	#	---------------------------------
	ndxstart = 0

	irun     = 0
	for ndx in range(lrun):
		#	Assign current run number
		irun += 1

		#	Assign DYNPOST file name and check if it exists
		dynfile = mod_path + "/r" + str(irun) + "/s.dyn"
		if not os.path.exists(dynfile):
			st.error("DYNPOST file (.dyn) " + dynfile + " does not exist!", icon="🚨")
			return

		#	Assign the DYNPOST file as a DYNPOST object
		try:
			dynobj = pr.Dyn(dynfile)
		except:
			st.error("Failed to assign " + dynfile + " as a DYNPOST object", icon="🚨")
			raise

		#	Get total number of non-zero time series values
		st.session_state.SIMLA_nstep_dynres = S4O_ReadTSNNZVals(dynobj)

		#	Get time series max and min values for the current run
		maxval, maxtime, minval, mintime = S4O_ReadTSMaxMin(dynobj, tsid, ndxstart)

		#	Append current run number
		runlist.append(irun)

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

		#	Finished processing the time series for the current realisation (run)
		tsProgressCurr += tsProgressDelta
		tsProgressBar.progress(tsProgressCurr)

	#	Finished proessing the time series for all realisation (runs)
	tsProgressBar.progress(100)
	tsProgressBar.empty()

	#	Check change in standard deviation
	tolno = 0
	ptol = float(st.session_state.df_Execution.iloc[4,1])
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
	st.session_state.df_Results['Realisation'] = runlist
	st.session_state.df_Results['Mean'] = meanlist
	st.session_state.df_Results['StdDev'] = stdlist
	st.session_state.df_Results['ΔStdDev [%]'] = dstdlist
	st.session_state.df_Results['Mean+1StdDev'] = m1stdlist
	st.session_state.df_Results['Maxima'] = maxmalist
	st.session_state.df_Results['Max'] = maxlist
	st.session_state.df_Results['Min'] = minlist

	#	Set ResultsCalculated status to True
	st.session_state.ResultsCalculated = True

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

	nruns = st.session_state.df_Results.shape[0]
	for irun in range(nruns):
		runlist.append(int(st.session_state.df_Results.iloc[irun,0]))
		meanlist.append(float(st.session_state.df_Results.iloc[irun,1]))
		stdlist.append(float(st.session_state.df_Results.iloc[irun,2]))
		m1stdlist.append(float(st.session_state.df_Results.iloc[irun,4]))

	#	Assign design value
	dval = float(st.session_state.df_Execution.iloc[5,1])*float(st.session_state.df_Product.iloc[0,1])

	#	Assign maximum y value for all result curves
	mval = max(np.max(meanlist), np.max(m1stdlist), dval)

	#	Build and show bokeh plot
	st.write("---")
	st.subheader('Lateral displacement ($u_{y}$) as function of number of sea state realisations')
	plt = figure()
	plt.line(runlist[1:nruns], m1stdlist[1:nruns], color='blue', line_width=3, legend_label='Mean+1SD uy,max')
	plt.scatter(runlist[1:nruns], m1stdlist[1:nruns], marker='inverted_triangle', fill_color="blue", size=12, legend_label='Mean+1SD uy,max')
	plt.line(runlist, meanlist, color='blue', line_width=3, line_dash='dashed', legend_label='Mean uy,max')
	if dval > 0.0:
		dline = []
		for irun in range(nruns): dline.append(dval)
		plt.line(runlist, dline, color='red', line_width=3, line_dash='dashdot', legend_label='Design value, uy')
	plt.legend.location = 'bottom_right'
	plt.add_layout(Title(text='Lateral displacement as function of number of sea state realisations.', align='left', text_font_size='12pt'), 'below')
	plt.xaxis.axis_label = 'Number of sea state realisations'
	plt.yaxis.axis_label = 'Lateral displacement, uy [m]'
	plt.xaxis.axis_label_text_font_size = "12pt"
	plt.yaxis.axis_label_text_font_size = "12pt"
	plt.x_range = Range1d(0, nruns+1)
	plt.y_range = Range1d(0, math.ceil(mval))
	st.bokeh_chart(plt, use_container_width=True)

	return
#
#

# Define the displacement statistics table formatting function
def custom_format_displacements(x):
	if isinstance(x, float):
		return '{:.4f}'.format(x)
	else:
		return x
#
#

def S4O_CheckIfSIMLARunsExist(lrun):

	#	Assign model path name
	mod_path = st.session_state.modelFileDir + "/" + st.session_state.modelFileName

	#	Loop through all run folders and check is the DYNPOST file (.dyn) file is missing
	dynexists = True
	for irun in range(lrun):
		dynfile = mod_path + "/r" + str(irun+1) + "/s.dyn"
		if not os.path.exists(dynfile): dynexists = False

	#	Check if any DYNPOST files are missing
	if not dynexists: st.error("One or several DYNPOST files (.dyn) are missing!", icon="🚨")

	return dynexists
#
#

def S4O_Show_TS_Plot():

	#	Show the selected time series for all realisations (runs)
	st.write("---")
	st.subheader('Plot the selected time series for the selected realisations (runs)')

	#	Assign model path and number of realisations (runs)
	mod_path = st.session_state.modelFileDir + "/" + st.session_state.modelFileName
	nruns    = st.session_state.df_Results.shape[0]

	#	Build the list of available realisations (runs)
	realisations = []
	for irun in range(nruns): realisations.append('r' + str(irun+1))

	#	Assign number of available colors and line types
	nocolors = len(st.session_state.TSLineColors)
	nlintyps = len(st.session_state.TSLineTypes)

	#	Assign the time step used in the dynamic analysis and the default time step to be used for curve plotting
	dtdyn = float(st.session_state.df_Execution.iloc[0,1])
	dtvis = 0.5

	#	Assign time step for the dynamic analysis and the wave load ramping time
	dtdyn   = float(st.session_state.df_Execution.iloc[0,1])
	tdursim = float(st.session_state.df_Execution.iloc[1,1])*3600.0

	#	Assign start index for the time series to plot
	if st.session_state["IncludeWaveRamping"]: ndxstart = 0
	else:									   ndxstart = st.session_state.SIMLA_nstep_dynres - math.ceil(tdursim/dtdyn)

	#	Group the widgets required to select which time series to plot into a form to avoid unwanted refresh of page
	#	------------------------------------------------------------------------------------------------------------
	with st.form(key='Time series plot'):

		#	Select the time series
		tsndx = st.session_state.TSResultOptions.index('None')
		TS_Selected = st.selectbox('Select the time series :', st.session_state.TSResultOptions, index=tsndx)
		tsndx = st.session_state.TSResultOptions.index(TS_Selected)
		tsid = st.session_state.TSResultIDs[tsndx]

		#	Select which sea state realisations (runs) to plot (default=all)
		selected_realisations = st.multiselect('Select which realisations (runs) to plot :', realisations, default=realisations)

		#	Specify time step to be used for the time series plots
		dtvis = st.number_input("Specify time step to be used for the time series plots [s] :", min_value=dtdyn, value=dtvis, format="%.4f")

		#	Specify whether to include the "Wave load ramping time" as part of the time series
		st.checkbox('Include wave load ramping time', key='IncludeWaveRamping', value=st.session_state.IncludeWaveRamping)

		#	Display the "Plot" button
		plot = st.form_submit_button("Plot", help="Plot the time series for the selected realisations (runs)")

	#	Do nothing if no time series or realisations (runs) have been selected
	if TS_Selected == 'None' or len(selected_realisations) == 0: return

	#	Plot the selected time series for all selected realisations (runs)
	#	------------------------------------------------------------------
	#	Initialise progress bar
	tsProgressCurr = int(0)
	tsProgressDelta = int(100/len(selected_realisations))
	tsProgressBar = st.progress(tsProgressCurr)

	#	Initialize the bokeh plot object
	plt = figure()

	#	Loop through all selected realisations (runs) and build the time series plot
	pltcount = 0
	for realisation in selected_realisations:

		#	Assign DYNPOST file name and check if it exists
		dynfile = mod_path + "/" + realisation + "/s.dyn"
		if not os.path.exists(dynfile):
			st.error("DYNPOST file (.dyn) " + dynfile + " does not exist!", icon="🚨")
			return

		#	Assign the DYNPOST file as a DYNPOST object
		try:
			dynobj = pr.Dyn(dynfile)
		except:
			st.error("Failed to assign " + dynfile + " as a DYNPOST object", icon="🚨")
			raise

		#	Get the time series (time=x, value=y), maximum value + time and minimum value + time for the current run from the specified time series
		x, y, maxval, maxtime, minval, mintime = S4O_ReadTSArrays(dynobj, tsid, dtdyn, dtvis, ndxstart)

		#	Check that number of points in the time series to plot is below or equal to maximum number of points
		npoints = len(x)
		if npoints > st.session_state.MaxPointsTSPlot:
			ndxend    = np.argmax(dynobj.time)
			minstride = math.ceil((ndxend+1)/st.session_state.MaxPointsTSPlot)
			mindtvis  = dtdyn*minstride
			st.error("Too many points in the time series, unable to plot! Please increase the time step to be used for the plots to at least " + str(mindtvis) + " seconds.", icon="🚨")
			return

		#	Add the time series for the current run to the time series plot
		#	---------------------------------------------------------------
		#	Assign color and line type index
		nopass = int(pltcount/nocolors)
		colndx = pltcount - nopass*nocolors
		ltyndx = nopass - int(nopass/nlintyps)*nlintyps

		#	Assign time series label
		tslabel = realisation

		#	Add current time series to the plot
		plt.line(x, y, color=st.session_state.TSLineColors[colndx], line_dash=st.session_state.TSLineTypes[ltyndx], line_width=3, legend_label=tslabel)

		#	Add circles to max (filled) and min (hollow) values
		plt.circle(maxtime, maxval, line_color=st.session_state.TSLineColors[colndx], fill_color=st.session_state.TSLineColors[colndx], size=12)
		plt.circle(mintime, minval, line_color=st.session_state.TSLineColors[colndx], fill_color='white', size=12)

		#	Finished reading time series for current realisation (run)
		tsProgressCurr += tsProgressDelta
		tsProgressBar.progress(tsProgressCurr)
		pltcount += 1

	#	Finished reading the selected time series for all selected realisations (runs)
	tsProgressBar.progress(100)
	tsProgressBar.empty()

	#	Write plot title
	st.subheader(TS_Selected)

	#	Add hover tooltips
	hover = HoverTool()
	hover.tooltips = [("(t, y)", "($x, $y)")]
	plt.add_tools(hover)

	#	Show the time series plot
	plt.legend.location = 'bottom_right'
	plt.add_layout(Title(text=TS_Selected + ' as function of time.', align='left', text_font_size='12pt'), 'below')
	plt.xaxis.axis_label = 'Time [s]'
	plt.yaxis.axis_label = TS_Selected
	plt.xaxis.axis_label_text_font_size = "12pt"
	plt.yaxis.axis_label_text_font_size = "12pt"
	st.bokeh_chart(plt, use_container_width=True)

	return
#
#

def S4O_ReadTSArrays(dynobj, tsid, dtdyn, dtvis, ndxstart):

	#	Get the time series, maximum value + time and minimum value + time for the specified dyn object and time series id

	#	Assign index to the last non-zero time value
	ndxend = np.argmax(dynobj.time)

	#	Assign the stride number (step) to be used when extracting the time series arrays
	stride = math.ceil(dtvis/dtdyn)

	#	Assign selection
	selection = range(ndxstart, ndxend+1, stride)

	#	Extract the time serie arrays
	x = dynobj.time[selection]
	y = dynobj.dynres[selection, tsid]

	#	Get the max and min values and times
	ndxmax  = np.argmax(y)
	maxtime = x[ndxmax]
	maxval  = y[ndxmax]
	ndxmin  = np.argmin(y)
	mintime = x[ndxmin]
	minval  = y[ndxmin]

	return x, y, maxval, maxtime, minval, mintime
#
#

def S4O_ReadTSMaxMin(dynobj, tsid, ndxstart):

	#	Get the maximum value + time and minimum value + time for the specified dyn object and time series id

	#	Assign index to the last non-zero time value
	ndxend = np.argmax(dynobj.time)

	#	Assign selection
	selection = range(ndxstart, ndxend+1)

	#	Extract the time serie arrays
	x = dynobj.time[selection]
	y = dynobj.dynres[selection, tsid]

	#	Get the max and min values and times
	ndxmax  = np.argmax(y)
	maxtime = x[ndxmax]
	maxval  = y[ndxmax]
	ndxmin  = np.argmin(y)
	mintime = x[ndxmin]
	minval  = y[ndxmin]

	return maxval, maxtime, minval, mintime
#
#

def S4O_ReadTSNNZVals(dynobj):

	#	Get total number of non-zero time series values

	#	Assign index to the last non-zero time value
	ndxend = np.argmax(dynobj.time)

	return ndxend + 1
#
#
