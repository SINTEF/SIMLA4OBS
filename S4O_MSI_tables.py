"""
File: S4O_MSI_tables.py
Description:
The "tables" function writes table information to the SIMLA input file (.sif).
Revisions:
YYYY-MM-DD: 
"""
__author__ = "Vegard Longva"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "2024-10-31"
__maintainer__ = "Vegard Longva"
__email__ = "Vegard.Longva@sintef.no"

import numpy as np

def tables( file         , uz_ini      , fyhydpenfac  ,
            fzhydpenfac  , Cm          , Cd           ,
            Cl           ) :
    
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# TABLES\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#       name         columns    KP-val            initial embedment\n")
    file.write("TABLE   inizpen      2         %f   %f\n"  % ( -1e6  , -uz_ini ))
    file.write("                                %f   %f\n"  % (  1e6  , -uz_ini ))
    file.write("#\n")

    file.write("#       name         columns    penetration       load reduction factor\n")
    file.write("TABLE   fyhydpenfac  2\n")
    for row in fyhydpenfac:
        file.write("                           \t%f         %f\n" %  (row[0], row[1]) )                                   #  Streamlit: User-defined table. Or should it be fixed according to RP109 ?
    file.write("#\n")

    file.write("#       name         columns    penetration       load reduction factor\n")
    file.write("TABLE   fzhydpenfac  2\n")
    for row in fzhydpenfac:
        file.write("                           \t%f         %f\n" %  (row[0], row[1]) )                                   #  Streamlit: User-defined table. Or should it be fixed according to RP109 ?
    file.write("#\n")

    file.write("#       name         columns    gap        coefficient\n")
    file.write("TABLE   masscoef     2         -1000.0     %f\n" % Cm )
    file.write("                                1000.0     %f\n" % Cm )
    file.write("#\n")
    file.write("#       name         columns    gap        coefficient\n")
    file.write("TABLE   dragcoef     2         -1000.0     %f\n" % Cd )
    file.write("                                1000.0     %f\n" % Cd )
    file.write("#\n")
    file.write("#       name         columns    gap        coefficient\n")
    file.write("TABLE   liftcoef     2         -1000.0     %f\n" % Cl )
    file.write("                                1000.0     %f\n" % Cl )
    file.write("#\n")
