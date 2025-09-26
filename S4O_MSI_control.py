"""
File: S4O_MSI_control.py
Description:
The "control" function writes control data to the SIMLA input file (.sif).
Revisions:
2025-09-22: Deleted "tendwaveramp"from the "tendwaveramp+tdurwave" expressions to avoid doubling of the wave load ramping time. 
2025-09-25: Deleted subtraction of tend_static in the calculation of nstep_dynres.
2025-09-25: Added tend_static to the TIMECO card for the dynamic analysis.
"""
__author__ = "Vegard Longva"
__credits__ = [""]
__license__ = "GPLv3"
__version__ = "2024-11-28"
__maintainer__ = "Vegard Longva"
__email__ = "Vegard.Longva@sintef.no"

import numpy as np

def control( file           , iprint         , gacc         ,
             tend_static    , tendwaveramp   , tdurwave     ,
             dtdyn          , uz_cont        , uz_ini       ,
             tstart_uzini   ):


    # Time step size for avoiding singular equation system during ramping of initial penetration
    if uz_ini<uz_cont:
       nstep = 1
    else:
       nstep = np.ceil(1.1*uz_ini/uz_cont)

    dt_uzini = (tend_static-tstart_uzini) / nstep
    if dt_uzini>=1.0:
        dt_uzini=1.0
    else:
        N = -np.ceil(-np.log10(dt_uzini))
        dt_uzini = 10**N
    
    nstep_dynres = np.ceil(tend_static/dt_uzini + (tdurwave) / dtdyn)

    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# ANALYSIS CONTROL DATA\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#         maxit   ndim   isolvr   npoint   iprint   conr   gacc       istart\n")
    file.write("CONTROL   100     3      2        16       %i       1e-6   %f   stressfree\n" % (iprint, gacc) ) 
    file.write("#\n")
    file.write("#         mstat   alfa1   alfa2   HHT-alfa\n")
    file.write("DYNCONT   1       0.0     0.0    -0.05\n") 
    file.write("#\n")
    file.write("#            t                dt            dtvi    dtdy   dt0    type      hlaflag   steptype   iterco   itcrit   maxit   maxdiv   conr\n")
    file.write("TIMECO       %f         %f      1.00    1.0    601.0  static    nohla     auto       none     all      100     5        1e-7\n" % (tend_static, dt_uzini) )
    file.write("TIMECO       %f     %f      400.00    1.0    100.0  dynamic   nohla     auto       none     all      40     5        1e-6\n" % (tdurwave+tend_static, dtdyn ))
    file.write("#\n")

    return nstep_dynres