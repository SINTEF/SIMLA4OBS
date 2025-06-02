"""
File: S4O_Model.py
Description:
These functions initiates and updates the df_Model pandas dataframe.
"""
__author__ = "Egil Giertsen"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "2025-06-02"
__maintainer__ = "Egil Giertsen"
__email__ = "giertsen@sintef.no"

import pandas as pd
import streamlit as st
import tkinter as tk
from tkinter import filedialog
import os
import random
from random import randint

#
#	MODEL input function
#

def S4O_Model():

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)

	#	Set Streamlit subtitle
	st.subheader('Model title :')
	st.session_state.modelMainTitle = st.text_input(" ", value=st.session_state.modelMainTitle)
	st.write("---")

	#	Set ResultsCalculated to False 
	st.session_state.ResultsCalculated = False

	#	Set Streamlit subtitle
	st.subheader('Open or save model :')

	#	Display the Open, Save and Save As buttons
	mopen = st.button("Open...", key=None, help="Read an existing model from a .s4o file")
	msave = st.button("Save", key=None, help="Save model to the current .s4o file")
	msaveas = st.button("Save As...", key=None, help="Save the current model to a new .s4o file")

	if mopen:
		selected_file_path = S4O_select_file2open()
		selected_file_dir = os.path.dirname(selected_file_path)
		selected_file_name = os.path.splitext(os.path.basename(selected_file_path))[0]
		st.session_state.modelFilePath = selected_file_path
		st.session_state.modelFileDir = selected_file_dir
		st.session_state.modelFileName = selected_file_name

		if selected_file_path != '' and os.path.exists(selected_file_path):
			S4O_Read_Model()
		else:
			st.error("File does not exist!", icon="🚨")

	elif msave:
		file_path = st.session_state.modelFilePath
		if file_path != '' and os.path.exists(file_path):
			S4O_Write_Model()
		else:
			st.error("File does not exist!", icon="🚨")

	elif msaveas:
		selected_file_path = CheckIfFileExtensionExist(S4O_select_file2saveas())
		selected_file_dir = os.path.dirname(selected_file_path)
		selected_file_name = os.path.splitext(os.path.basename(selected_file_path))[0]
		st.session_state.modelFilePath = selected_file_path
		st.session_state.modelFileDir = selected_file_dir
		st.session_state.modelFileName = selected_file_name

		st.session_state.df_Execution.iloc[3,1] = st.session_state.currentMaxRel

		if selected_file_path != '':
			S4O_Generate_Seed_Numbers()
			S4O_Write_Model()
		else:
			st.error("File does not exist!", icon="🚨")

	#	Change working directory to current directory
	if os.path.exists(st.session_state.modelFilePath): os.chdir(st.session_state.modelFileDir)

	st.session_state.Model_OK = True

	return st.session_state.Model_OK
#
#

def S4O_select_file2open():
	
	root = tk.Tk()
	root.withdraw()
	root.lift()
	root.attributes('-topmost', True)
	answer = filedialog.askopenfilename(parent=root,
                                  		initialdir=st.session_state.modelFileDir,
  										title="Please select a model file to open...",
  										filetypes=(("S4O files","*.s4o*"),
                                                   ("All files","*.*")))
	root.destroy()

	return answer
#
#

def S4O_select_file2saveas():
	
	root = tk.Tk()
	root.withdraw()
	root.lift()
	root.attributes('-topmost', True)
	answer = filedialog.asksaveasfilename(parent=root,
										  initialdir=st.session_state.modelFileDir,
										  title="Please specify a file to save model as...",
										  filetypes=(("S4O files","*.s4o*"),
                                                     ("All files","*.*")))
	root.destroy()

	return answer
#
#

def S4O_Generate_Seed_Numbers():

	numseeds = int(st.session_state.df_Execution.iloc[3,1])

	st.session_state.listOfSeedNumbers = []
	for i in range(numseeds):
		seedno = random.randint(10000,10000000)
		st.session_state.listOfSeedNumbers.append(seedno)

	return
#
#

def S4O_Write_Model():

	#	Open file
	f = open(st.session_state.modelFilePath, "w")

	#	Program version
	f.write("# SIMLA4OBS program version\n")
	f.write("%s\n" % ( st.session_state.S4O_versionID ) )

	#	Model parameters
	f.write("# Model parameters\n")
	f.write("%s\n" % ( st.session_state.modelMainTitle ) )

	#	Product parameters
	f.write("# Product parameters\n")
	nvals = st.session_state.df_Product.shape[0]
	for ndx in range(nvals):
		f.write("\t%.6e" % ( st.session_state.df_Product.iloc[ndx,1] ) )
	f.write("\n")

	#	Seabed parameters
	f.write("# Seabed parameters\n")
	nvals = st.session_state.df_Seabed.shape[0]
	for ndx in range(nvals):
		if ndx == 0 or ndx == 9 or ndx == 14:
			f.write("\t%i" % ( st.session_state.df_Seabed.iloc[ndx,1] ) )
		else:
			f.write("\t%.6e" % ( st.session_state.df_Seabed.iloc[ndx,1] ) )
	f.write("\n")

	#	Environment parameters
	f.write("# Environment parameters\n")
	nvals = st.session_state.df_Environment.shape[0]
	for ndx in range(nvals):
		if ndx == 4 or ndx == 6 or ndx == 7:
			f.write("\t%i" % ( st.session_state.df_Environment.iloc[ndx,1] ) )
		else:
			f.write("\t%.6e" % ( st.session_state.df_Environment.iloc[ndx,1] ) )
	f.write("\n")

	#	Execution parameters
	f.write("# Execution parameters\n")
	nvals = st.session_state.df_Execution.shape[0]
	for ndx in range(nvals):
		if ndx == 3 or ndx == 6 :
			f.write("\t%i" % ( st.session_state.df_Execution.iloc[ndx,1] ) )
		else:
			f.write("\t%.6e" % ( st.session_state.df_Execution.iloc[ndx,1] ) )
	f.write("\n")

	#	Seed numbers
	f.write("# Seed numbers\n")
	nvals = int(st.session_state.df_Execution.iloc[3,1])
	for ndx in range(nvals):
		f.write("\t%i" % ( st.session_state.listOfSeedNumbers[ndx] ) )
	f.write("\n")

	#	Close file
	f.close()

	st.rerun()

	return
#
#

def S4O_Read_Model():

	#	Open file
	f = open(st.session_state.modelFilePath, "r")

	#	Read all lines
	lines = f.readlines()

	#	Close file
	f.close()

	#	Loop through all lines in the file
	nlines = len(lines)
	for iline in range(nlines):

		# Extract current line
		cline = lines[iline]
		cline = cline.strip()

		if iline == 0 or iline == 2 or iline == 4 or iline == 6 or iline == 8 or iline == 10 or iline == 12:
			#	Comment line, do nothing
			continue
		elif iline == 1:
			#	Check and store program version
			version = cline
			if version != st.session_state.S4O_versionID:
				st.error("You have to open the model with the same program version (" + version + ") as you used when saving it!", icon="🚨")
				return
			else:
				st.session_state.S4O_versionID = version

		elif iline == 3:
			#	Store model title
			st.session_state.modelMainTitle = cline

		else:
			#	STORE PARAMETERS READ FROM FILE

			#	Split the current line into columns
			columns = cline.split()
			nvals = len(columns)

			if iline == 5:
				#	Check number of Product parameters on file
				pvals = st.session_state.df_Product.shape[0]
				if nvals != pvals:
					st.error("Number of Product parameters on file (" + str(nvals) + ") is different from the expected number (" + str(pvals) + ")!", icon="🚨")
					return
				#	Store Product parameters
				for ndx in range(nvals):
					st.session_state.df_Product.iloc[ndx,1] = float(columns[ndx])

			elif iline == 7:
				#	Check number of Seabed parameters on file
				pvals = st.session_state.df_Seabed.shape[0]
				if nvals != pvals:
					st.error("Number of Seabed parameters on file (" + str(nvals) + ") is different from the expected number (" + str(pvals) + ")!", icon="🚨")
					return
				#	Store Seabed parameters
				for ndx in range(nvals):
					if ndx == 0 or ndx == 9 or ndx == 14:
						st.session_state.df_Seabed.iloc[ndx,1] = int(columns[ndx])
					else:
						st.session_state.df_Seabed.iloc[ndx,1] = float(columns[ndx])

			elif iline == 9:
				#	Check number of Environment parameters on file
				pvals = st.session_state.df_Environment.shape[0]
				if nvals != pvals:
					st.error("Number of Environment parameters on file (" + str(nvals) + ") is different from the expected number (" + str(pvals) + ")!", icon="🚨")
					return
				#	Store Environment parameters
				for ndx in range(nvals):
					if ndx == 4 or ndx == 6 or ndx == 7:
						st.session_state.df_Environment.iloc[ndx,1] = int(columns[ndx])
					else:
						st.session_state.df_Environment.iloc[ndx,1] = float(columns[ndx])

			elif iline == 11:
				#	Check number of Execution parameters on file
				pvals = st.session_state.df_Execution.shape[0]
				if nvals != pvals:
					st.error("Number of Execution parameters on file (" + str(nvals) + ") is different from the expected number (" + str(pvals) + ")!", icon="🚨")
					return
				#	Store Execution parameters
				for ndx in range(nvals):
					if ndx == 3 :
						st.session_state.df_Execution.iloc[ndx,1] = int(columns[ndx])
						st.session_state.currentMaxRel = int(columns[ndx])
					elif ndx == 6 :
						st.session_state.df_Execution.iloc[ndx,1] = int(columns[ndx])
						st.session_state.maxRunsPB = int(columns[ndx])
					else:
						st.session_state.df_Execution.iloc[ndx,1] = float(columns[ndx])

			elif iline == 13:
				#	Check number of Seed values on file
				pvals = int(st.session_state.df_Execution.iloc[3,1])
				if nvals != pvals:
					st.error("Number of Seed values on file (" + str(nvals) + ") is different from the expected number (" + str(pvals) + ")!", icon="🚨")
					return
				#	Store Seed values
				st.session_state.listOfSeedNumbers = []
				for ndx in range(nvals):
					st.session_state.listOfSeedNumbers.append(int(columns[ndx]))

			else:
				st.error("Unexpected number of lines (" + str(nlines) + ") in model file!", icon="🚨")
				return

	st.rerun()

	return
#
#
def CheckIfFileExtensionExist(existing_path):

	#	Do nothing if existing file path is empty
	if existing_path == '': return ''

	#	Extract file base name and extension
	base = os.path.splitext(existing_path)[0]
	exte = os.path.splitext(existing_path)[1]

	#	Check that a file extension exists, and if not assign it to '.s4o'
	if exte == '': exte = '.s4o'

	#	Assign new path
	new_path = base + exte

	return new_path
#
#
