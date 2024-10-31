"""
File: S4O_Seabed.py
Description:
These functions initiates and updates the df_Seabed pandas dataframe.
"""
__author__ = "Egil Giertsen"
__credits__ = ["Terje Rølvåg"]
__license__ = "GPLv3"
__version__ = "2024"
__maintainer__ = "Egil Giertsen"
__email__ = "giertsen@sintef.no"

import pandas as pd
import streamlit as st

#
#	SEABED input function
#

def S4O_Seabed():

	#	Set Streamlit subtitle
	st.header('Seabed parameters')

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)

	#	Assign seabed parameters
	if 'df_Seabed' not in st.session_state:
		st.warning('S4O_Seabed : Should not be here!', icon="⚠️")
	else:
		cmnx = int(st.session_state.df_Seabed.iloc[0,1])
		Sduw = float(st.session_state.df_Seabed.iloc[1,1])
		Ushs = float(st.session_state.df_Seabed.iloc[2,1])
		Cduw = float(st.session_state.df_Seabed.iloc[3,1])
		Dsuw = float(st.session_state.df_Seabed.iloc[4,1])
		Ussy = float(st.session_state.df_Seabed.iloc[5,1])
		Ussz = float(st.session_state.df_Seabed.iloc[6,1])
		Usuw = float(st.session_state.df_Seabed.iloc[7,1])
		Cfac = float(st.session_state.df_Seabed.iloc[8,1])
		Elas = float(st.session_state.df_Seabed.iloc[9,1])
		cpnx = int(st.session_state.df_Seabed.iloc[10,1])
		IPpv = float(st.session_state.df_Seabed.iloc[11,1])
		IPtn = float(st.session_state.df_Seabed.iloc[12,1])

	#	Select seabed model
	Seabed_Selected = st.selectbox('Select seabed model :', st.session_state.SeabedOptions, index=cmnx)
	smnx = st.session_state.SeabedOptions.index(Seabed_Selected)

	#	Prompt for model dependent seabed parameters
	if Seabed_Selected == 'V&S Sand':
		Sduw = st.number_input("Sand dry unit weight [N/m3] : ", min_value=0.0, value=Sduw, format="%.2f")
	if Seabed_Selected == 'V&L Clay':
		Ushs = st.number_input("Undrained shear strength [N/m2] : ", min_value=0.0, value=Ushs, format="%.2f")
		Cduw = st.number_input("Clay dry unit weight [N/m3] : ", min_value=0.0, value=Cduw, format="%.2f")
	if Seabed_Selected == 'NGI Drained':
		Dsuw = st.number_input("Drained submerged unit weight [N/m3] : ", min_value=0.0, value=Dsuw, format="%.2f")
	if Seabed_Selected == 'NGI Undrained':
		Ussy = st.number_input("Undrained shear strength y-dir [N/m2] : ", min_value=0.0, value=Ussy, format="%.2f")
		Ussz = st.number_input("Undrained shear strength z-dir [N/m2] : ", min_value=0.0, value=Ussz, format="%.2f")
		Usuw = st.number_input("Undrained submerged unit weight [N/m3] : ", min_value=0.0, value=Usuw, format="%.2f")
	if Seabed_Selected == 'DNV Model 2 Undrained':
		Ussy = st.number_input("Undrained shear strength y-dir [N/m2] : ", min_value=0.0, value=Ussy, format="%.2f")
		Ussz = st.number_input("Undrained shear strength z-dir [N/m2] : ", min_value=0.0, value=Ussz, format="%.2f")
		Usuw = st.number_input("Undrained submerged unit weight [N/m3] : ", min_value=0.0, value=Usuw, format="%.2f")
	if Seabed_Selected == 'Rock':
		Cfac = st.number_input("Coloumb friction factor [-] : ", min_value=0.0, value=Cfac, format="%.2f")

	#	Prompt for elastic stiffness parameter
	Elas = st.number_input("Elastic stiffness [Nm2] : ", min_value=0.0, value=Elas, format="%.2f")

	#	Prompt for penetration parameters
	st.subheader('Initial penetration')
	#	Select initial penetration mode
	Penetration_Selected = st.selectbox("Select initial penetration mode :", st.session_state.PenetrationOptions, index=cpnx)
	spnx = st.session_state.PenetrationOptions.index(Penetration_Selected)
	if Penetration_Selected == 'Specify':
		IPpv = st.number_input("Penetration [m] : ", value=IPpv, format="%.4f")
	if Penetration_Selected == 'Calculate':
		IPtn = st.number_input("Lay tension [N] : ", value=IPtn, format="%.2f")
	
	#	Save parameters
	Sdata = [['Selected seabed model index [-] :', smnx],
			 ['Sand dry unit weight [N/m3] :', Sduw],
			 ['Undrained shear strength [N/m2] :', Ushs], ['Clay dry unit weight [N/m3] :', Cduw], 
			 ['Drained submerged unit weight [N/m3] :', Dsuw],
			 ['Undrained shear strength y-dir [N/m2] :', Ussy], ['Undrained shear strength z-dir [N/m2] :', Ussz], ['Undrained submerged unit weight [N/m3] :', Usuw], 
	         ['Coloumb friction factor [-] :', Cfac],
	         ['Elastic stiffness [Nm2] :', Elas],
	         ['Selected penetration mode index [-] :', spnx], ['Penetration [m] :', IPpv], ['Lay tension [N] :', IPtn]]	
	st.session_state.df_Seabed = pd.DataFrame(Sdata, columns=['Seabed parameter','Value'])

	# Echo Input dataframe
	if Echo_Inputs:
		st.write("---")
		st.write("Stored seabed parameters :")
		st.write("Selected seabed model : " + Seabed_Selected)
		st.write("Selected initial penetration mode : " + Penetration_Selected)
		st.write(st.session_state.df_Seabed)
		st.write('Seabed OK : ', st.session_state.Seabed_OK)

	st.session_state.Seabed_OK = True

	return st.session_state.df_Seabed,st.session_state.Seabed_OK
#
#

#
#	SEABED set defaults function
#

def S4O_Seabed_Defaults():

	#	Assign default seabed parameters
	if 'df_Seabed' not in st.session_state:
		cmnx = 0
		Sduw = 11800.0
		Ushs = 800.0
		Cduw = 18000.0
		Dsuw = 11800.0
		Ussy = 800.0
		Ussz = 800.0
		Usuw = 18000.0
		Cfac = 0.6
		Elas = 65000.0
		cpnx = 0
		IPpv = 0.02
		IPtn = 5000.0	
	else:
		st.warning('S4O_Seabed_Defaults : Should not be here!', icon="⚠️")
	
	Sdata = [['Selected seabed model index [-] :', cmnx],
			 ['Sand dry unit weight [N/m3] :', Sduw],
			 ['Undrained shear strength [N/m2] :', Ushs], ['Clay dry unit weight [N/m3] :', Cduw], 
			 ['Drained submerged unit weight [N/m3] :', Dsuw],
			 ['Undrained shear strength y-dir [N/m2] :', Ussy], ['Undrained shear strength z-dir [N/m2] :', Ussz], ['Undrained submerged unit weight [N/m3] :', Usuw], 
	         ['Coloumb friction factor [-] :', Cfac],
	         ['Elastic stiffness [Nm2] :', Elas],
	         ['Selected penetration mode index [-] :', cpnx], ['Penetration [m] :', IPpv], ['Lay tension [N] :', IPtn]]	
	st.session_state.df_Seabed = pd.DataFrame(Sdata, columns=['Seabed parameter','Value'])

	st.session_state.Seabed_OK = True

	return st.session_state.df_Seabed,st.session_state.Seabed_OK
#
#