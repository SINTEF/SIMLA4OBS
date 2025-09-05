"""
File: S4O_Environment.py
Description:
These functions initiates and updates the df_Environment pandas dataframe.
Revisions:
YYYY-MM-DD:
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2025-03-14"
__maintainer__ = "Egil Giertsen"
__email__ = "Egil.Giertsen@sintef.no"

import pandas as pd
import streamlit as st

#
#	ENVIRONMENT input function
#

def S4O_Environment():

#	Set Streamlit subtitle
	st.header('Environment parameters')

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)

	#	Assign environmental parameters
	if 'df_Environment' not in st.session_state:
		st.warning('S4O_Environment : Should not be here!', icon="⚠️")
	else:
		WD = float(st.session_state.df_Environment.iloc[0,1])
		Hs = float(st.session_state.df_Environment.iloc[1,1])
		Tp = float(st.session_state.df_Environment.iloc[2,1])
		Wdir = float(st.session_state.df_Environment.iloc[3,1])
		cwsnx = int(st.session_state.df_Environment.iloc[4,1])
		Peakp = float(st.session_state.df_Environment.iloc[5,1])
		cstnx = int(st.session_state.df_Environment.iloc[6,1])
		Ndir = int(st.session_state.df_Environment.iloc[7,1])
		Sexp = float(st.session_state.df_Environment.iloc[8,1])
		Cvel = float(st.session_state.df_Environment.iloc[9,1])
		Cdir = float(st.session_state.df_Environment.iloc[10,1])
		Crefp = float(st.session_state.df_Environment.iloc[11,1])
		Csrou = float(st.session_state.df_Environment.iloc[12,1])
		Cmgsz = float(st.session_state.df_Environment.iloc[13,1])

	#	Prompt for environmental parameters
	#	Water depth
	WD = st.number_input("Water depth [m] :", min_value=0.0, value=WD, format="%.2f")

	#	Waves
	st.subheader('Waves')
	Hs = st.number_input("Significant wave height [m] :", min_value=0.0, max_value=100.0, value=Hs, format="%.2f")
	Tp = st.number_input("Significant wave period [s] :", min_value=0.0, max_value=100.0, value=Tp, format="%.2f")
	Wdir = st.number_input("Wave direction [deg] :", help="Wave direction relative to product X-axis [deg]", min_value=0.0, max_value=180.0, value=Wdir, format="%.2f")
	#	Select wave spectrum
	Spectrum_Selected = st.selectbox('Select wave spectrum :', st.session_state.WaveSpectraOptions, index=cwsnx)
	swsnx = st.session_state.WaveSpectraOptions.index(Spectrum_Selected)
	if Spectrum_Selected == 'JONSWAP':
		Peakp = st.number_input("Peakedness parameter [-] : ", min_value=0.0, value=Peakp, format="%.2f")
	#	Select wave spreading type
	Spreading_Selected = st.selectbox('Select wave spreading :', st.session_state.WaveSpreadingOptions, index=cstnx)
	sstnx = st.session_state.WaveSpreadingOptions.index(Spreading_Selected)
	#	Number of directions and spreading function exponent
	Ndir = st.number_input("Number of directions [-] : ", min_value=0, value=Ndir, format="%i")
	Sexp = st.number_input("Spreading function exponent [-] : ", min_value=0.0, value=Sexp, format="%.2f")

	#	Current
	st.subheader('Current')
	Cvel = st.number_input("Current velocity [m/s] :", min_value=0.0, max_value=10.0, value=Cvel, format="%.2f")
	Cdir = st.number_input("Current direction [deg] :", help="Current direction relative to product X-axis [deg]", min_value=0.0, max_value=180.0, value=Cdir, format="%.2f")
	Crefp = st.number_input("Reference point [m] :", help="Reference point above seabed [m]", min_value=0.0, value=Crefp, format="%.2f")
	Csrou = st.number_input("Seabed roughness [m] :", min_value=0.0, value=Csrou, format="%.4e")
	Cmgsz = st.number_input("Median grain size [m] :", help="Median grain size of soil particles (d_50) [m]", min_value=0.0, value=Cmgsz, format="%.4e")

	#	Store environment parameters
	Edata = [['Water depth [m] :', WD],
		     ['Significant wave height [m] :', Hs], ['Significant wave period [s] :', Tp], ['Wave direction [deg] :', Wdir],
		     ['Selected wave spectrum index :', swsnx], ['Peakedness parameter [-] :', Peakp], ['Selected wave spreading index :', sstnx], 
		     ['Number of directions [-] :', Ndir], ['Spreading function exponent [-] :', Sexp],
		     ['Current velocity [m/s] :', Cvel], ['Current direction [deg] :', Cdir],
		     ['Reference point [m] :', Crefp], ['Seabed roughness [m] :', Csrou], ['Median grain size [m] :', Cmgsz]]
	st.session_state.df_Environment = pd.DataFrame(Edata, columns=['Environmental parameter','Value'])

	# Echo df_Environment dataframe
	if Echo_Inputs:
		st.write("---")
		st.write("Stored environment parameters :")
		st.write("Selected wave spectrum : " + Spectrum_Selected)
		st.write("Selected wave spreading : " + Spreading_Selected)
		st.write(st.session_state.df_Environment)
		st.write('Environment Ok: ', st.session_state.Environment_OK)

	st.session_state.Environment_OK = True

	return st.session_state.df_Environment,st.session_state.Environment_OK
#
#

#
# ENVIRONMENT set defaults function
#

def S4O_Environment_Defaults():

	#	Assign default environmental parameters
	if 'df_Environment' not in st.session_state:
		WD = 50.0
		Hs = 12.0
		Tp = 14.0
		Wdir = 90.0
		cwsnx = 0
		Peakp = 3.3
		cstnx = 0
		Ndir = 1
		Sexp = 0.0
		Cvel = 0.3
		Cdir = 90.0
		Crefp = 4.0
		Csrou = 5.00e-6
		Cmgsz = 6.25e-5
	else:
		st.warning('S4O_Environment_Defaults : Should not be here!', icon="⚠️")

	Edata = [['Water depth [m] :', WD],
		     ['Significant wave height [m] :', Hs], ['Significant wave period [s] :', Tp], ['Wave direction [deg] :', Wdir],
		     ['Selected wave spectrum index :', cwsnx], ['Peakedness parameter [-] :', Peakp], ['Selected wave spreading index :', cstnx], 
		     ['Number of directions [-] :', Ndir], ['Spreading function exponent [-] :', Sexp],
		     ['Current velocity [m/s] :', Cvel], ['Current direction [deg] :', Cdir],
		     ['Reference point [m] :', Crefp], ['Seabed roughness [m] :', Csrou], ['Median grain size [m] :', Cmgsz]]
	st.session_state.df_Environment = pd.DataFrame(Edata, columns=['Environmental parameter','Value'])

	st.session_state.Environment_OK = True

	return st.session_state.df_Environment,st.session_state.Environment_OK
#
#

# Define the ENVIRONMENT formatting function
def custom_format_environment(x):
	if isinstance(x, float):
		return '{:.4e}'.format(x)
	else:
		return x
