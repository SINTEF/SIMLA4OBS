"""
File: S4O_Seabed.py
Description:
These functions initiates and updates the df_Seabed pandas dataframe.
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
		#	Y-direction
		cmnx_y = int(st.session_state.df_Seabed.iloc[0,1])
		Ssuw_y = float(st.session_state.df_Seabed.iloc[1,1])
		Ushs_y = float(st.session_state.df_Seabed.iloc[2,1])
		Cduw_y = float(st.session_state.df_Seabed.iloc[3,1])
		Dsuw_y = float(st.session_state.df_Seabed.iloc[4,1])
		Ussy_y = float(st.session_state.df_Seabed.iloc[5,1])
		Usuw_y = float(st.session_state.df_Seabed.iloc[6,1])
		Cfac_y = float(st.session_state.df_Seabed.iloc[7,1])
		Elas_y = float(st.session_state.df_Seabed.iloc[8,1])
		#	Z-direction
		cmnx_z = int(st.session_state.df_Seabed.iloc[9,1])
		Dsuw_z = float(st.session_state.df_Seabed.iloc[10,1])
		Ussz_z = float(st.session_state.df_Seabed.iloc[11,1])
		Usuw_z = float(st.session_state.df_Seabed.iloc[12,1])
		Elas_z = float(st.session_state.df_Seabed.iloc[13,1])
		#	Initial penetration
		cpnx = int(st.session_state.df_Seabed.iloc[14,1])
		IPpv = float(st.session_state.df_Seabed.iloc[15,1])
		IPtn = float(st.session_state.df_Seabed.iloc[16,1])
		Smly = float(st.session_state.df_Seabed.iloc[17,1])
		Bstf = float(st.session_state.df_Seabed.iloc[18,1])

	#	Select seabed parameters - y-direction
	st.subheader('Seabed parameters - y-direction')
	Seabed_Selected_y = st.selectbox('Select seabed model :', st.session_state.SeabedOptions, index=cmnx_y)
	smnx_y = st.session_state.SeabedOptions.index(Seabed_Selected_y)

	#	Prompt for model dependent seabed parameters
	if Seabed_Selected_y == 'V&S Sand':
		Ssuw_y = st.number_input("Sand saturated unit weight [N/m3] : ", min_value=0.0, value=Ssuw_y, format="%.2f")
		disabled_options = ['V&L Clay']
	if Seabed_Selected_y == 'V&L Clay':
		Ushs_y = st.number_input("Undrained shear strength [N/m2] : ", min_value=0.0, value=Ushs_y, format="%.2f")
		Cduw_y = st.number_input("Clay dry unit weight [N/m3] : ", min_value=0.0, value=Cduw_y, format="%.2f")
		disabled_options = ['V&S Sand']
	if Seabed_Selected_y == 'NGI Drained':
		Dsuw_y = st.number_input("Drained submerged unit weight [N/m3] : ", min_value=0.0, value=Dsuw_y, format="%.2f")
		disabled_options = ['V&S Sand', 'V&L Clay']
	if Seabed_Selected_y == 'NGI Undrained':
		Ussy_y = st.number_input("Undrained shear strength [N/m2] : ", min_value=0.0, value=Ussy_y, format="%.2f")
		Usuw_y = st.number_input("Undrained submerged unit weight [N/m3] : ", min_value=0.0, value=Usuw_y, format="%.2f")
		disabled_options = ['V&S Sand', 'V&L Clay']
	if Seabed_Selected_y == 'DNV Model 2 Undrained':
		Ussy_y = st.number_input("Undrained shear strength [N/m2] : ", min_value=0.0, value=Ussy_y, format="%.2f")
		Usuw_y = st.number_input("Undrained submerged unit weight [N/m3] : ", min_value=0.0, value=Usuw_y, format="%.2f")
		disabled_options = ['V&S Sand', 'V&L Clay']
	if Seabed_Selected_y == 'Rock':
		Cfac_y = st.number_input("Coloumb friction factor [-] : ", min_value=0.0, value=Cfac_y, format="%.2f")
		disabled_options = ['V&S Sand', 'V&L Clay']

	#	Prompt for elastic stiffness parameter
	Elas = st.number_input("Elastic stiffness [N/m2] : ", min_value=0.0, value=Elas_y, format="%.2f")

	#	Select seabed parameters - z-direction
	st.subheader('Seabed parameters for initial penetration calculation')

	Seabed_Selected_z, ndx_z = custom_selectbox('Select seabed model z-dir :', st.session_state.SeabedOptions, disabled_options, cmnx_z)

	smnx_z = checkPSIModelCombinations (Seabed_Selected_y, Seabed_Selected_z, ndx_z)

	#	Prompt for model dependent seabed parameters
	if Seabed_Selected_z == 'NGI Drained':
		Dsuw_z = st.number_input("Drained submerged unit weight z-dir [N/m3] : ", min_value=0.0, value=Dsuw_z, format="%.2f")
	if Seabed_Selected_z == 'NGI Undrained':
		Ussz_z = st.number_input("Undrained shear strength z-dir [N/m2] : ", min_value=0.0, value=Ussz_z, format="%.2f")
		Usuw_z = st.number_input("Undrained submerged unit weight z-dir [N/m3] : ", min_value=0.0, value=Usuw_z, format="%.2f")
	if Seabed_Selected_z == 'DNV Model 2 Undrained':
		Ussz_z = st.number_input("Undrained shear strength z-dir [N/m2] : ", min_value=0.0, value=Ussz_z, format="%.2f")
		Usuw_z = st.number_input("Undrained submerged unit weight z-dir [N/m3] : ", min_value=0.0, value=Usuw_z, format="%.2f")
	if Seabed_Selected_z == 'Rock':
		Elas_z = st.number_input("Elastic stiffness z-dir [N/m2] : ", min_value=0.0, value=Elas_z, format="%.2f")
	
	#	Prompt for initial penetration parameters
	st.subheader('Specify initial penetration model')

	#	Select initial penetration mode
	Penetration_Selected = st.selectbox("Select initial penetration model :", st.session_state.PenetrationOptions, index=cpnx)
	spnx = st.session_state.PenetrationOptions.index(Penetration_Selected)

	if Penetration_Selected == 'Specify':
		IPpv = st.number_input("Penetration [m] : ", value=IPpv, format="%.4f")
	if Penetration_Selected == 'Calculate':
		IPtn = st.number_input("Lay tension [N] : ",
								help="If lay tension is set equal to zero (0) no additional static penetration due to laying is applied, i.e. the k_lay factor is set equal to one (1.0).",
								value=IPtn, format="%.2f")
		Smly = st.number_input("Submerged mass during lay [kg/m] :", min_value=0.0, value=Smly, format="%.2f")
		Bstf = st.number_input("Bending stiffness [Nm2] :", value=Bstf, format="%.4e")
	
	#	Save parameters
	Sdata = [['Selected seabed model index [-] :', smnx_y],
			 ['Sand saturated unit weight [N/m3] :', Ssuw_y],
			 ['Undrained shear strength [N/m2] :', Ushs_y], ['Clay dry unit weight [N/m3] :', Cduw_y], 
			 ['Drained submerged unit weight [N/m3] :', Dsuw_y],
			 ['Undrained shear strength [N/m2] :', Ussy_y], ['Undrained submerged unit weight [N/m3] :', Usuw_y], 
	         ['Coloumb friction factor [-] :', Cfac_y],
	         ['Elastic stiffness [N/m2] :', Elas_y],
	         ['Selected seabed model index z-dir [-] :', smnx_z],
			 ['Drained submerged unit weight z-dir [N/m3] :', Dsuw_z],
			 ['Undrained shear strength z-dir [N/m2] :', Ussz_z], ['Undrained submerged unit weight z-dir [N/m3] :', Usuw_z], 
	         ['Elastic stiffness z-dir [N/m2] :', Elas_z],
	         ['Selected penetration model index [-] :', spnx], ['Penetration [m] :', IPpv], ['Lay tension [N] :', IPtn],
	         ['Submerged mass during lay [kg/m] :', Smly], ['Bending stiffness [Nm2] :', Bstf]]	
	st.session_state.df_Seabed = pd.DataFrame(Sdata, columns=['Seabed parameter','Value'])

	# Echo Input dataframe
	if Echo_Inputs:
		st.write("---")
		st.write("Stored seabed parameters :")
		st.write("Selected seabed model : " + Seabed_Selected_y)
		if Seabed_Selected_z != None: st.write("Selected seabed model z-dir : " + Seabed_Selected_z)
		st.write("Selected initial penetration model : " + Penetration_Selected)
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
		#	Y direction
		cmnx_y = 0
		Ssuw_y = 11800.0
		Ushs_y = 800.0
		Cduw_y = 18000.0
		Dsuw_y = 11800.0
		Ussy_y = 800.0
		Usuw_y = 18000.0
		Cfac_y = 0.6
		Elas_y = 65000.0
		#	Z direction
		cmnx_z = 0
		Dsuw_z = 11800.0
		Ussz_z = 800.0
		Usuw_z = 18000.0
		Elas_z = 65000.0
		#	Initial penetration
		cpnx = 0
		IPpv = 0.02
		IPtn = 5000.0
		Smly = 36.0
		Bstf = 2.4e7	
	else:
		st.warning('S4O_Seabed_Defaults : Should not be here!', icon="⚠️")
	
	Sdata = [['Selected seabed model index [-] :', cmnx_y],
			 ['Sand saturated unit weight [N/m3] :', Ssuw_y],
			 ['Undrained shear strength [N/m2] :', Ushs_y], ['Clay dry unit weight [N/m3] :', Cduw_y], 
			 ['Drained submerged unit weight [N/m3] :', Dsuw_y],
			 ['Undrained shear strength [N/m2] :', Ussy_y], ['Undrained submerged unit weight [N/m3] :', Usuw_y], 
	         ['Coloumb friction factor [-] :', Cfac_y],
	         ['Elastic stiffness [N/m2] :', Elas_y],
	         ['Selected seabed model index z-dir [-] :', cmnx_z],
			 ['Drained submerged unit weight z-dir [N/m3] :', Dsuw_z],
			 ['Undrained shear strength z-dir [N/m2] :', Ussz_z], ['Undrained submerged unit weight z-dir [N/m3] :', Usuw_z], 
	         ['Elastic stiffness z-dir [N/m2] :', Elas_z],
	         ['Selected penetration mode index [-] :', cpnx], ['Penetration [m] :', IPpv], ['Lay tension [N] :', IPtn],
	         ['Submerged mass during lay [kg/m] :', Smly], ['Bending stiffness [Nm2] :', Bstf]]	
	st.session_state.df_Seabed = pd.DataFrame(Sdata, columns=['Seabed parameter','Value'])

	st.session_state.Seabed_OK = True

	return st.session_state.df_Seabed,st.session_state.Seabed_OK
#
#
def custom_selectbox(label, options, disabled_options, cmnx):

	#	Customize st.selectbox to make spesific options unselectable
	selected_option = st.selectbox(label, options, index=cmnx)

	ndx = 0
	if selected_option in disabled_options:
		ndx = options.index(selected_option)
		return None, ndx

	return selected_option, ndx
#
#
def checkPSIModelCombinations (model_y, model_z, ndx_z):

	#	Available PSI models = ['V&S Sand', 'V&L Clay', 'NGI Drained', 'NGI Undrained', 'DNV Model 2 Undrained', 'Rock']

	#	Check if the user have selected illegal combinations of PSI models in y- and z-direction
	if model_z == None:
		st.error("You cannot combine PSI model '" + model_y + "' in y-direction with PSI model '" + st.session_state.SeabedOptions[ndx_z] + "' in z-direction!", icon="🚨")
		smnx_z = st.session_state.SeabedOptions.index(model_y)
	else:
		smnx_z = st.session_state.SeabedOptions.index(model_z)

	#	Check if the user have selected unphysical combinations of PSI models in y- and z-direction
	if model_y == 'V&S Sand' and ((model_z == 'NGI Undrained') or (model_z == 'DNV Model 2 Undrained')):
		st.warning("Combining PSI model '" + model_y + "' in y-direction with PSI model '" + model_z + "' in z-direction is unphysical!", icon="⚠️")
	if model_y == 'V&L Clay' and (model_z == 'NGI Drained'):
		st.warning("Combining PSI model '" + model_y + "' in y-direction with PSI model '" + model_z + "' in z-direction is unphysical!", icon="⚠️")
	if model_y == 'NGI Drained' and ((model_z == 'NGI Undrained') or (model_z == 'DNV Model 2 Undrained')):
		st.warning("Combining PSI model '" + model_y + "' in y-direction with PSI model '" + model_z + "' in z-direction is unphysical!", icon="⚠️")
	if model_y == 'NGI Undrained' and (model_z == 'NGI Drained'):
		st.warning("Combining PSI model '" + model_y + "' in y-direction with PSI model '" + model_z + "' in z-direction is unphysical!", icon="⚠️")
	if model_y == 'DNV Model 2 Undrained' and (model_z == 'NGI Drained'):
		st.warning("Combining PSI model '" + model_y + "' in y-direction with PSI model '" + model_z + "' in z-direction is unphysical!", icon="⚠️")

	return smnx_z
