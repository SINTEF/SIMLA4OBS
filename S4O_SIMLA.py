"""
File: S4O_SIMLA.py
Description:
These functions creates SIMLA input files, runs SIMLA and reads results.
Revisions:
2025-09-03: S4O_SIMLA_Subprocess_Open; Added print of SIMLA run command if "Extended print" and "Simulate runs" both are ticked on.
2025-09-04: S4O_Run_SIMLA_Block; Rewrote function to use process.wait() to wait for subprocesses, and added calculation of elapsed wall-clock time per block.
2025-09-04: S4O_Run_SIMLA; Added calculation of total elapsed wall-clock time for all runs.
"""
__author__ = "Egil Giertsen"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "2025-09-04"
__maintainer__ = "Egil Giertsen"
__email__ = "Egil.Giertsen@sintef.no"

import pandas as pd
import streamlit as st
import subprocess
import os
import time
import random
from random import randint
from S4O_MakeSIMLAInput import S4O_MakeSIMLAInput

def S4O_Create_Input_Files(frun, lrun):
	
	#	Check if model has been stored
	file_path = st.session_state.modelFilePath
	if file_path == '' or not os.path.exists(file_path):
		st.error("You have to save your model before you can create input files!", icon="🚨")
		return

	#	Check if model directory exists and create it if not
	mod_path = st.session_state.modelFileDir + "/" + st.session_state.modelFileName
	if not os.path.exists(mod_path):
		if st.session_state.ExtendedPrint: st.info("Creating model directory : " + mod_path)
		os.mkdir(mod_path)

	#	Create dummy input files
	irun = frun
	while irun <= lrun:

		#	Assign run directory and create it if it does not exist
		run_path = mod_path + "/r" + str(irun)
		if not os.path.exists(run_path):
			if st.session_state.ExtendedPrint: st.info("Creating run directory : " + run_path)
			os.mkdir(run_path)

		#	Assign SIMLA input file
		sifname = run_path + "/s.sif"

		#	Generate SIMLA input file
		S4O_Generate_SIMLA_Input(sifname, irun)

		#	Assign next run number
		irun += 1

	#	Generate DYNPOST EXT input file
	S4O_Generate_DYNPOST_EXT_Input(mod_path, lrun)

	return
#
#

def S4O_Generate_SIMLA_Input(sifname, irun):

	#	Generate DYNPOST EXT input file
	if st.session_state.ExtendedPrint: st.write('Generating SIMLA input file : ' + sifname)
	if st.session_state.ExtendedPrint: st.write('Generating DYNPOST MPF input file : ' + os.path.dirname(sifname) + '/s.sdi')

	S4O_MakeSIMLAInput(sifname, irun)

	return
#
#
def S4O_Generate_DYNPOST_EXT_Input(mod_path, lrun):

	#	Generate DYNPOST EXT input file
	sdiname = mod_path + '/extremes.sdi'
	if st.session_state.ExtendedPrint: st.write('Generating DYNPOST EXT input file : ' + sdiname)

	#	Open file
	sdifile = open(sdiname, 'w')

	#	Write input for lateral displacement maximum values (type=1, idynres=5[node=1,dof=2])
	irun = 0
	for ndx in range(lrun):
		irun += 1
		if irun == 1:
			dynname = "r" + str(irun) + "/s"
			sdifile.write("#        type   frac   idynres   nmax    time0    -out.txt          dyn\n")
			sdifile.write("MXPLOT   %i      %.2f   %i         %i       %.1f      \"disp-uy-max\"     \"%s\"\n" % ( 1, 0.0, 5, 1, 0.0, dynname) )
		else:
			dynname = "r" + str(irun) + "/s"
			sdifile.write("                                                                    \"%s\"\n" % ( dynname) )

	#	Write input for lateral displacement minimum values (type=-1, idynres=5[node=1,dof=2])
	irun = 0
	for ndx in range(lrun):
		irun += 1
		if irun == 1:
			dynname = "r" + str(irun) + "/s"
			sdifile.write("#        type   frac   idynres   nmax    time0    -out.txt          dyn\n")
			sdifile.write("MXPLOT   %i     %.2f   %i         %i       %.1f      \"disp-uy-min\"     \"%s\"\n" % ( -1, 0.0, 5, 1, 0.0, dynname) )
		else:
			dynname = "r" + str(irun) + "/s"
			sdifile.write("                                                                    \"%s\"\n" % ( dynname) )

	#	Close file
	sdifile.close()

	return
#
#

def S4O_Run_SIMLA():

	#
	#	Generate input files, run SIMLA analyses (SIMLA + DYNPOST) and generate results
	#	-------------------------------------------------------------------------------
	#	Set ResultsCalculated to False 
	st.session_state.ResultsCalculated = False
	
	#	Check if model has been stored
	file_path = st.session_state.modelFilePath
	if file_path == '' or not os.path.exists(file_path):
		st.error("You have to save your model before you can run it!", icon="🚨")
		return

	#	Assign run parameters
	nrunsmax = int(st.session_state.df_Execution.iloc[3,1])
	nblocks = st.session_state.noBlocksToRun 
	nrunspb = st.session_state.maxRunsPB

	#	Assign block number and first and last run number for the first block to be run
	cblock = 1
	frun = 1
	nrunscb = nrunspb
	if nrunscb > nrunsmax: nrunscb = nrunsmax
	lrun = frun + nrunscb - 1

	#	Simulate SIMLA runs with the sleep command?
	if st.session_state.RunAnalyses:
		if st.session_state.SimulateRuns:
			st.warning('Simulating ' + str(nblocks) + ' SIMLA blocks with the sleep command for runs 1 to ' + str(nrunsmax) + '!', icon="⚠️")
		else:
			st.info('Executing ' + str(nblocks) + ' SIMLA blocks for runs 1 to ' + str(nrunsmax) + '.')

	#	Show SIMLA progress bar
	if st.session_state.GenerateInputs or st.session_state.RunAnalyses:
		st.session_state.simlaProgressCurr = int(0)
		st.session_state.simlaProgressDelta = int(100/nrunsmax)
		st.session_state.simlaProgressBar = st.progress(st.session_state.simlaProgressCurr)

	#	Loop over number of blocks to be run
	wclstart = time.perf_counter()

	while cblock <= nblocks:

		if not st.session_state.SimulateRuns: st.write('Executing SIMLA block number ' + str(cblock) + ' for runs ' + str(frun) + ' to ' + str(lrun) + '.')

		#	Create input files if the "Generate input files" check box is checked
		if st.session_state.GenerateInputs: S4O_Create_Input_Files(frun, lrun)

		#	Run the current SIMLA block
		#	---------------------------
		if st.session_state.RunAnalyses:

			#	Run the SIMLA block if the "Run analyses" check box is checked
			S4O_Run_SIMLA_Block(frun, lrun)

		elif st.session_state.GenerateInputs and not st.session_state.RunAnalyses:			
			#	Update the progress bar if only the "Generate input files" check box is checked
			st.session_state.simlaProgressCurr += (lrun-frun+1)*st.session_state.simlaProgressDelta
			st.session_state.simlaProgressBar.progress(st.session_state.simlaProgressCurr)

		#	Update block number for next block to be run
		cblock +=1

		#	Update first and last run number for next block to be run
		frun = lrun + 1
		lrun = frun + nrunspb - 1
		if lrun > nrunsmax: lrun = nrunsmax

	#	Calculate elapsed wall-clock time for all blocks
	wclend     = time.perf_counter()
	wclelapsed = wclend - wclstart

	#	All SIMLA runs completed
	st.write('All SIMLA blocks (' + str(nblocks) + ') covering runs 1 to ' + str(lrun) + ' have finished.' +
			 ' Total elapsed wall-clock time : ' + str(int(wclelapsed)) + ' seconds.')

	#	Set progress bar to "Complete" (100)
	if st.session_state.GenerateInputs or st.session_state.RunAnalyses:
		st.session_state.simlaProgressBar.progress(100)
		st.session_state.simlaProgressBar.empty()

	return
#
#

def S4O_Run_SIMLA_Block_OLD(frun, lrun):

	#	------------------------------------
	#	Start all SIMLA runs as subprocesses
	#	------------------------------------
	irun = frun
	ndx = 0
	plist = []
	rlist = []
	while irun <= lrun:
		p = S4O_SIMLA_Subprocess_Open(irun)
		plist.append(p)
		rlist.append(True)
		irun += 1
		ndx += 1

	#	Check if any of the SIMLA subprocesses are still running
	stillrunning = True
	while stillrunning:

		#	Check status for all runs in current block
		irun = frun
		ndx = 0
		nprunning = 0
		while irun <= lrun:
			if plist[ndx].poll() is not None:
				if rlist[ndx]:
					if st.session_state.ExtendedPrint: st.write('SIMLA run number ' + str(irun) + ' has finished.')
					st.session_state.simlaProgressCurr += st.session_state.simlaProgressDelta
					st.session_state.simlaProgressBar.progress(st.session_state.simlaProgressCurr)
					rlist[ndx] = False
					if not S4O_SIMLA_Check_Run_Success(irun):
						st.error('SIMLA run number ' + str(irun) + ' failed!', icon="🚨")
						break
			else:
				nprunning += 1

			irun += 1
			ndx += 1

		if nprunning == 0: stillrunning = False

		if stillrunning:
			st.session_state.simlaProgressBar.progress(st.session_state.simlaProgressCurr)
			time.sleep(1)

	if not st.session_state.SimulateRuns and st.session_state.ExtendedPrint: st.write('All SIMLA runs ' + str(frun) + ' to ' + str(lrun) + ' have finished.')

	return
#
#

def S4O_Run_SIMLA_Block(frun, lrun):

	#	-----------------------------------------------------------
	#	Execute all SIMLA runs in the current block as subprocesses
	#	-----------------------------------------------------------
	wclstart = time.perf_counter()

	#	Start subprocesses
	irun  = frun
	plist = []
	while irun <= lrun:
		p = S4O_SIMLA_Subprocess_Open(irun)
		plist.append(p)
		irun += 1

	#	Make all subprocesses wait until they have finished
	for p in plist:
		p.wait()

	#	All subprocesses have finished, update progress bar and check for errors
	irun = frun
	while irun <= lrun:
		if st.session_state.ExtendedPrint: st.write('SIMLA run number ' + str(irun) + ' has finished.')

		#	Update progress bar
		st.session_state.simlaProgressCurr += st.session_state.simlaProgressDelta
		st.session_state.simlaProgressBar.progress(st.session_state.simlaProgressCurr)

		#	Check for errors
		if not S4O_SIMLA_Check_Run_Success(irun):
			st.error('SIMLA run number ' + str(irun) + ' failed!', icon="🚨")
			break
	
		irun += 1

	#	Calculate elapsed wall-clock time for the current block
	wclend     = time.perf_counter()
	wclelapsed = wclend - wclstart

	if not st.session_state.SimulateRuns: st.write('All SIMLA runs ' + str(frun) + ' to ' + str(lrun) + ' have finished.' +
												   ' Elapsed wall-clock time : ' + str(int(wclelapsed)) + ' seconds.')

	return
#
#

def S4O_SIMLA_Subprocess_Open(irun):

	#	Change working directory to the current SIMLA run directory
	cwd = st.session_state.modelFileDir + "/" + st.session_state.modelFileName + '/r' + str(irun)
	os.chdir(cwd)

	#	Run SIMLA or simulate a SIMLA run with the sleep command?
	if st.session_state.SimulateRuns:
		#	Assign a sleep command to simulate a SIMLA run
		s2w = random.randint(15,30)
		runcmd = 'sleep(' + str(s2w) + ')'
		if st.session_state.ExtendedPrint:
			sruncmd = st.session_state.SIMLA_EXE + ' -n s' + ' -s2 ' + str(st.session_state.SIMLA_nstep_dynres) + ' > simla_print.out'
			st.write('SIMLA run command : '+ sruncmd)
			st.write('SIMLA run number ' + str(irun) + ' waits for ' + str(s2w) + ' seconds.')
	else:
		#	Assign the SIMLA run command
		runcmd = st.session_state.SIMLA_EXE + ' -n s' + ' -s2 ' + str(st.session_state.SIMLA_nstep_dynres) + ' > simla_print.out'

	#	Open the SIMLA subprocess
	p = subprocess.Popen(["powershell", runcmd])

	return p
#
#

def S4O_DYNPOST_Subprocess_Open(irun):

	#	Change working directory to the current SIMLA run directory
	cwd = st.session_state.modelFileDir + "/" + st.session_state.modelFileName + '/r' + str(irun)
	os.chdir(cwd)

	#	Run DYNPOST or simulate a DYNPOST run with the sleep command?
	if st.session_state.SimulateRuns:
		#	Assign a sleep command to simulate a DYNPOST MPF run
		s2w = random.randint(1,5)
		runcmd = 'sleep(' + str(s2w) + ')'
		if st.session_state.ExtendedPrint: st.write('DYNPOST MPF run number ' + str(irun) + ' waits for ' + str(s2w) + ' seconds.')
	else:
		#	Assign the DYNPOST run command
		runcmd = st.session_state.DYNPOST_EXE + ' -n s > dympf_print.out'

	#	Open the DYNPOST subprocess
	p = subprocess.Popen(["powershell", runcmd])

	return p
#
#

def S4O_SIMLA_DYNPOST_EXT_Run(lrun):

	#	Change working directory to current model directory
	cwd = st.session_state.modelFileDir + "/" + st.session_state.modelFileName
	os.chdir(cwd)

	#	Run DYNPOST or simulate a DYNPOST run with the sleep command?
	if st.session_state.SimulateRuns:
		#	Assign a sleep command to simulate a DYNPOST EXT run
		s2w = random.randint(5,10)
		runcmd = 'sleep(' + str(s2w) + ')'
		if st.session_state.ExtendedPrint: st.write('DYNPOST EXT run waits for ' + str(s2w) + ' seconds.')
	else:
		#	Assign the DYNPOST run command
		runcmd = st.session_state.DYNPOST_EXE + ' -n extremes > dyext_print.out'

	#	Execute DYNPOST to generate EXT values
	rext = subprocess.run(["powershell", runcmd])

	if rext.returncode != 0: st.error('DYNPOST EXT run failed!', icon="🚨")

	return
#
#

def S4O_SIMLA_Check_Run_Success(irun):

	#	Return True if simulated run
	if st.session_state.SimulateRuns: return True

	#	Set default return value
	success = False

	#	Assign SIMLA list file name
	slfname = st.session_state.modelFileDir + "/" + st.session_state.modelFileName + '/r' + str(irun) + '/s.slf'

	#	Open the SIMLA list file in read mode and extract the last 16 lines
	with open(slfname, "r") as slf:
		#	Read all lines in the file
		all_lines = slf.readlines()
		#	Extract the last 16 lines
		last_16_lines = all_lines[-16:]
	
	#	Search for the string "SIMLA successfully completed" in the last 16 lines
	strsuccess = 'SIMLA successfully completed'
	for ndx in range(len(last_16_lines)):
		if strsuccess in last_16_lines[ndx]:
			success = True
			break

	return success
#
#

def S4O_DYNPOST_MPF_Check_Run_Success(irun):

	#	Return True if simulated run
	if st.session_state.SimulateRuns: return True

	#	Set default return value
	success = False

	#	Assign DYNPOST list file name
	sdoname = st.session_state.modelFileDir + "/" + st.session_state.modelFileName + '/r' + str(irun) + '/s.sdo'

	#	Open the DYNPOST list file in read mode and extract the last 17 lines
	with open(sdoname, "r") as sdo:
		#	Read all lines in the file
		all_lines = sdo.readlines()
		#	Extract the last 17 lines
		last_17_lines = all_lines[-17:]
	
	#	Search for the string "DYNPOST successfully completed" in the last 17 lines
	strsuccess = 'DYNPOST successfully completed'
	for ndx in range(len(last_17_lines)):
		if strsuccess in last_17_lines[ndx]:
			success = True
			break

	return success
#
#

def S4O_DYNPOST_EXT_Check_Run_Success():

	#	Return True if simulated run
	if st.session_state.SimulateRuns: return True

	#	Set default return value
	success = False

	#	Assign DYNPOST list file name
	sdoname = st.session_state.modelFileDir + "/" + st.session_state.modelFileName + '/extremes.sdo'

	#	Open the DYNPOST list file in read mode and extract the last 17 lines
	with open(sdoname, "r") as sdo:
		#	Read all lines in the file
		all_lines = sdo.readlines()
		#	Extract the last 17 lines
		last_17_lines = all_lines[-17:]
	
	#	Search for the string "DYNPOST successfully completed" in the last 17 lines
	strsuccess = 'DYNPOST successfully completed'
	for ndx in range(len(last_17_lines)):
		if strsuccess in last_17_lines[ndx]:
			success = True
			break

	return success
#
#
