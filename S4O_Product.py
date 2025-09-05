"""
File: S4O_Product.py
Description:
These functions initiates and updates the df_Product pandas dataframe.
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
#	PRODUCT input function
#

def S4O_Product():

	#	Set Streamlit subtitle
	st.header('Product parameters')

	#	Update Dashboard layout
	Echo_Inputs = st.sidebar.checkbox('Echo input parameters',value=True)

	#	Assign product parameters
	if 'df_Product' not in st.session_state:
		st.warning('S4O_Product : Should not be here!', icon="⚠️")
	else:
		Od = float(st.session_state.df_Product.iloc[0,1])
		Sm = float(st.session_state.df_Product.iloc[1,1])
		MGt = float(st.session_state.df_Product.iloc[2,1])
		MGd = float(st.session_state.df_Product.iloc[3,1])
	
	# Prompt for product parameters
	Od = st.number_input("Outer diameter [m] :", min_value=0.0, max_value=2.0, value=Od, format="%.4f")
	Sm = st.number_input("Submerged mass [kg/m] :", min_value=0.0, value=Sm, format="%.2f")
	st.subheader('Marine growth')
	MGt = st.number_input("Thickness [m] :", value=MGt, format="%.4f")
	MGd = st.number_input("Density [kg/m3] :", value=MGd, format="%.2f")
	
	Pdata = [['Outer diameter [m] :', Od], ['Submerged mass [kg/m] :', Sm],
			 ['Thickness [m] :', MGt], ['Density [kg/m3] :', MGd]]
	st.session_state.df_Product = pd.DataFrame(Pdata, columns=['Product parameter','Value'])

	# Echo df_Product dataframe
	if Echo_Inputs: 
		st.write("---")
		st.write("Stored product parameters :")
		st.write(st.session_state.df_Product)
		st.write('Product Ok: ', st.session_state.Product_OK)
	
	st.session_state.Product_OK = True

	return st.session_state.df_Product,st.session_state.Product_OK
#
#

#
# PRODUCT set defaults function
#

def S4O_Product_Defaults ():

	#	Assign default product parameters
	if 'df_Product' not in st.session_state:
		Od = 0.190
		Sm = 36.0
		MGt = 0.01
		MGd = 1265.0
	else:
		st.warning('S4O_Product_Defaults : Should not be here!', icon="⚠️")

	Pdata = [['Outer diameter [m] :', Od], ['Submerged mass [kg/m] :', Sm],
			 ['Thickness [m] :', MGt], ['Density [kg/m3] :', MGd]]
	st.session_state.df_Product = pd.DataFrame(Pdata, columns=['Product parameter','Value'])
	
	st.session_state.Product_OK = True

	return st.session_state.df_Product,st.session_state.Product_OK
#
#