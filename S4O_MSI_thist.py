"""
File: S4O_MSI_thist.py
Description:
The "thist" function writes time history information to the SIMLA input file (.sif).
Revisions:
YYYY-MM-DD: 
"""
__author__ = "Vegard Longva"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "2024-10-31"
__maintainer__ = "Vegard Longva"
__email__ = "Vegard.Longva@sintef.no"

def thist( file         , thist_inizpen    , thist_wavecur   ,
           tend_static  ):

    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# TIME HISTORIES\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#       no     time             fac             - buoyancy and external pressure\n")
    file.write("THIST   100    0.0              1.0\n") 
    file.write("               1000.0           1.0\n")
    file.write("#\n")
    file.write("#       no     time             fac             - gravity\n")
    file.write("THIST   150    0.0              1.0\n") 
    file.write("               1000.0           1.0\n")
    file.write("#\n")

    file.write("#       no     time             fac             - y-dir stabilizing start-up spring\n")
    file.write("THIST   210    0.0              1.0\n")
    file.write("               %f         0.0\n" % tend_static)
    file.write("#\n")


    file.write("#       no     time             fac             - dummy\n")
    file.write("THIST   220    0.0              0.0\n") 
    file.write("               1000.0           0.0\n")
    file.write("#\n")

    file.write("#       no     time             fac             - initial soil embedment\n")
    file.write("THIST   250\n")
    for row in thist_inizpen:
        file.write("               %f         %f\n" %  (row[0], row[1]) )
    file.write("#\n")

    file.write("#       no     time             fac             - DROPS load\n")
    file.write("THIST   300\n")
    for row in thist_wavecur:
        file.write("               %f         %f\n" %  (row[0], row[1]) )
    file.write("#\n")
