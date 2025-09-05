"""
File: S4O_MakeSIMLAInput.py
Description:
This function creates a SIMLA input file for the SIMLA4OBS application.
Revisions:
2025-06-24: Corrected error in wave and current directions by converting to radians.
"""
__author__ = "Vegard Longva"
__credits__ = ["Egil Giertsen"]
__license__ = "GPLv3"
__version__ = "2025-06-24"
__maintainer__ = "Egil Giertsen, Vegard Longva"
__email__ = "Egil.Giertsen@sintef.no"

# Packages
import streamlit as st
import numpy as np
import os

# Functions
from S4O_MSI_control import control
from S4O_MSI_penetration import penetration
from S4O_MSI_elements import elements
from S4O_MSI_seabed import seabed
from S4O_MSI_loading import loading
from S4O_MSI_thist import thist
from S4O_MSI_boncon import boncon
from S4O_MSI_materials import materials
from S4O_MSI_tables import tables
from S4O_MakeRESULTSInput import results

def S4O_MakeSIMLAInput(sifname, irun):

    #   Assign physical constants
    rho_sea = 1025.0        #   Density of sea water [kg/m3]
    gacc = 9.80665          #   Gravity acceleration [m/s2]

    #   Assign element constants
    Lpipe = 2.0     #   Element length [m]
    nelpipe = 1     #   Number of elements

    #   Assign PRODUCT parameters
    diam = float(st.session_state.df_Product.iloc[0,1])             #   Outer diameter (without marine growth) [m]
    submass = float(st.session_state.df_Product.iloc[1,1])          #   Submerged mass [kg/m]
    mass = submass + np.pi*(diam**2/4)*rho_sea                      #   Structural mass [kg/m]
    EI_dum = 0.0                                                    #   Bending stiffness [Nm2] (dummy value)
    EA_dum = 1.0                                                    #   Axial stiffness [N] (dummy value)
    GJ_dum = 0.0                                                    #   Torsion stiffness [Nm2] (dummy value)
    th_margrow = float(st.session_state.df_Product.iloc[2,1])       #   Thickness of marine growth [m]
    rho_margrow = float(st.session_state.df_Product.iloc[3,1])      #   Density of marine growth [kg/m3]

    #   Assign SEABED parameters
    #   Y-direction PSI model (imody) - 1: 'V&S Sand', 2: 'V&L Clay', 3: 'NGI Drained', 4: 'NGI Undrained', 5: 'DNV Model 2 Undrained', 6: 'Rock / Coulomb friction']
    ndx   = int(st.session_state.df_Seabed.iloc[0,1])
    imody = st.session_state.SeabedValues[ndx]                      #   Y-direction PSI model
    gamd_sand = float(st.session_state.df_Seabed.iloc[1,1])         #   Sand dry unit weight [N/m3]
    su_clay = float(st.session_state.df_Seabed.iloc[2,1])           #   Undrained shear strength [N/m2] 
    gamd_clay = float(st.session_state.df_Seabed.iloc[3,1])         #   Clay dry unit weight [N/m3]
    gams_drain = float(st.session_state.df_Seabed.iloc[4,1])        #   Drained submerged unit weight [N/m3]
    su_y_undrain = float(st.session_state.df_Seabed.iloc[5,1])      #   Undrained shear strength [N/m2] 
    gams_undrain = float(st.session_state.df_Seabed.iloc[6,1])      #   Undrained submerged unit weight [N/m3]
    muy     = float(st.session_state.df_Seabed.iloc[7,1])           #   Coulomb friction factor [-]
    kstick  = float(st.session_state.df_Seabed.iloc[8,1])           #   Elastic stick stiffness [N/m2]

    #   Z-direction PSI model (imodz) - 1: 'V&S Sand', 2: 'V&L Clay', 3: 'NGI Drained', 4: 'NGI Undrained', 5: 'DNV Model 2 Undrained', 6: 'Rock / Constant stiffness']
    ndx   = int(st.session_state.df_Seabed.iloc[9,1])
    imodz = st.session_state.SeabedValues[ndx]                      #   Z-direction PSI model
    gams_z_drain = float(st.session_state.df_Seabed.iloc[10,1])     #   Drained submerged unit weight z-dir [N/m3] 
    su_z_undrain = float(st.session_state.df_Seabed.iloc[11,1])     #   Undrained shear strength z-dir [N/m2] 
    gams_z_undrain = float(st.session_state.df_Seabed.iloc[12,1])   #   Undrained submerged unit weight z-dir [N/m3] 
    kz_const = float(st.session_state.df_Seabed.iloc[13,1])         #   Elastic stiffness z-dir [N/m2]

    #   Initial penetration
    ndx     = int(st.session_state.df_Seabed.iloc[14,1])
    ipenmod = st.session_state.PenetrationValues[ndx]               #   Initial penetration mode : 1=Specify, 2=Calculate
    uz_ini = float(st.session_state.df_Seabed.iloc[15,1])           #   Initial penetration, specified [m]
    T0 = float(st.session_state.df_Seabed.iloc[16,1])               #   Horizontal lay tension, for klay-calculations [N]
    submass_lay = float(st.session_state.df_Seabed.iloc[17,1])      #   Submerged mass during lay [kg/m]
    EI = float(st.session_state.df_Seabed.iloc[18,1])               #   Bending stiffness, for klay-calculations [Nm2]

    #   Assign ENVIRONMENT parameters
    zseabed = -float(st.session_state.df_Environment.iloc[0,1])              #   Z-cordinate of seafloor [m] (-[Water depth])
    Hs = float(st.session_state.df_Environment.iloc[1,1])                    #   Significant wave height [m]
    Tp = float(st.session_state.df_Environment.iloc[2,1])                    #   Significant wave period [s]
    wavang = float(st.session_state.df_Environment.iloc[3,1])/180.0*np.pi    #   Wave direction [deg]
    ndx = int(st.session_state.df_Environment.iloc[4,1])
    iwavespec = st.session_state.WaveSpectraValues[ndx]                      #   Wave spectrum : 1=PM, 2=JONSWAP
    pkdness = float(st.session_state.df_Environment.iloc[5,1])               #   Peakedness parameter
    ndx = int(st.session_state.df_Environment.iloc[6,1])
    chspread = st.session_state.WaveSpreadingValues[ndx]                     #   Wave spreading type : "long", "short"
    ndir = int(st.session_state.df_Environment.iloc[7,1])                    #   Number of directions
    spreadpar = float(st.session_state.df_Environment.iloc[8,1])             #   Spreading function exponent
    curvel = float(st.session_state.df_Environment.iloc[9,1])                #   Current velocity [m/s]
    curang = float(st.session_state.df_Environment.iloc[10,1])/180.0*np.pi   #   Current direction [deg]
    cuhref = float(st.session_state.df_Environment.iloc[11,1])               #   Current reference height [m]
    curough = float(st.session_state.df_Environment.iloc[12,1])              #   Seabed roughness [m]
    d50 = float(st.session_state.df_Environment.iloc[13,1])                  #   Median grain size [m]

    #   Assign EXECUTION parameters

    tstart_uzini = 0.0                                              #   Start time for ramping initial penetration.
    tend_static = 1.0                                               #   End of static analysis and ramping of initial penetration, also used as reference time for initial penetration [s].
    dtdyn = float(st.session_state.df_Execution.iloc[0,1])          #   Time step size in dynamic analysis.

    #   Total wave duration = (Sea state duration [h])*3600 + Wave load ramping time [s]  +  static load ramping time [s]
    tendwaveramp = float(st.session_state.df_Execution.iloc[2,1])  +  tend_static
    tdurwave = float(st.session_state.df_Execution.iloc[1,1])*3600.0 + float(st.session_state.df_Execution.iloc[2,1])
    
    iwaveseed = st.session_state.listOfSeedNumbers[irun-1]
    wavetype = "irregular"
    dtwave = 0.5                                #   Time increment for wave kinematics
    tstartwave = tend_static                    #   Start time DROPS LOAD
    chcurprof = "rpf109"                        #   Use RPF109 current profile as "standard" is more conservative

    thist_wavecur = np.array([[  0.0          ,  0.0  ],
                              [  tend_static  ,  0.0  ],
                              [  tendwaveramp ,  1.0  ]])

    iroughydload = 3                            #   iroughydload=3 is recommended in PONDUS user manual
    fyhydfac = 1.0                              #   Scale factor for hydrodynamic load in y-direction
    fzhydfac = 1.0                              #   Scale factor for hydrodynamic load in z-direction
    chhydloadmodel = "wake"                     #   "wake" is the only rational load model option for products resting on the seabed

    Cm = 1.0     # =1.0 gives zero added mass. Dummy for this application since Morison model is never used as gapmori=1e6.
    Cd = 0.0     # Dummy for this application since Morison model is never used as gapmori=1e6.
    Cl = 0.0     # Dummy for this application since Morison model is never used as gapmori=1e6. 

    time_gapudate = np.array([  ])              #   Time for updating gap- and penetration-dependent tables. Safe choice: Assign no time, as then gap
    nstep_gapupdate = len(time_gapudate)        #   and penetetration is updated at every time step 

    kpstartgrid = -0.5*Lpipe - 0.2              #   Start point of hydrodynamic grid (KP=0 is placed at midpoint of pipe)
    kpendgrid = 0.5*Lpipe + 0.2                 #   Userdefined value. End point of hydrodynamic grid (KP=0 is placed at midpoint of pipe)
    dxgrid = 2.0                                #   dx is longitudinal spacing for hydrodynamic grid along the pipe 

    fyhydpenfac = np.array([[-1000.0  ,  0.3  ],
                            [   -0.5  ,  0.3  ],
                            [    0.0  ,  1.0  ]])    # Reduction factors for vertical hydrodynamic loading due to soil penetration, according to RP109

    fzhydpenfac = np.array([[-1000.0   ,  0.0  ],
                            [   -0.869 ,  0.0  ],
                            [   -0.1   ,  1.0  ],
                            [    0.0   ,  1.0  ]])   # Reduction factors for lateral hydrodynamic loading due to soil penetration, according to RP109

    iel1pipe = 1  
    inod1pipe = 1
    iel1seabedcont = 10001
    iel1seasurf = 20001
    inod1seasurf = 20001

    ivisual = 1       # ivisual=1 must be used as ivisual=0 gives error return from SIMLA.
    iprint = 0        # Streamlit: Parameter controlling print to out-file. See User manual for allowable values
 
    thist_inizpen = np.array([[  0.0         ,  0.0  ],
                              [  tend_static ,  1.0  ]])

    if kstick<1e-3:            #   Stabilizing startup spring in y-direction [N/m2]    
        ky_inispring = 1e3
    else:
        ky_inispring  = kstick

    #  Estimate dynamic z-direction stiffness that ensures quasi-static response in z-direction.
    #  Assume minimum load period T_load=1.0 second and that associated DAF=1.01 gives quasi-static response. Assume maximum marine growth to maximize z-dir stiffness.
    DAF = 1.01
    T_load = 1.0
    cm_pondus = 2.5 
    meff = mass + np.pi/4.0*np.power(diam,2.0)*rho_sea*(cm_pondus-1.0) + np.pi*(diam+th_margrow)*th_margrow*rho_margrow
    kz_seabed1 = np.power(2.0*np.pi/T_load,2.0 )*meff / (1.0-1.0/DAF)

    # Ensure that penetration change is less than 1% of OD, assuming max lift force is equal to weight of mass.
    kz_seabed2 = mass*gacc/0.01/diam

    kz_seabed = np.max(np.array([kz_seabed1,kz_seabed2]))
    uz_cont = submass*gacc/kz_seabed

    lamda = 0.025                                        # Damping ratio [-]
    czdamp_seabed = lamda*2.0*np.sqrt(meff*kz_seabed)    # Nodal seabed damping constant [Ns/m2]

    file = open(sifname,"w")

    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("HEAD\n")
    file.write("HEAD %s\n" % (st.session_state.modelMainTitle))
    file.write("HEAD\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")


    if ipenmod==2:
        uz_ini = penetration( 
                 submass_lay ,  diam          ,  EI            ,  
                 T0          ,  rho_sea       ,  gamd_sand     ,
                 gamd_clay   ,  gams_z_drain  ,  gams_z_undrain,
                 su_clay     ,  su_z_undrain  ,  kz_const      ,  
                 gacc        ,  imodz         )

    nstep_dynres = control(
              file            , iprint         , gacc          ,
              tend_static     , tendwaveramp   , tdurwave      ,
              dtdyn           , uz_cont        , uz_ini        ,
              tstart_uzini    )

    elements( file           , Lpipe          , mass           ,
              nelpipe        , diam           , zseabed        ,
              submass        , uz_ini         , tend_static    ,
              iel1pipe       , inod1pipe      , iel1seabedcont ,
              iel1seasurf    , inod1seasurf   , ipenmod        ,
              czdamp_seabed  , rho_margrow    , th_margrow     ,
              rho_sea        , uz_cont        )

    seabed(   file           , Lpipe          , zseabed        ,
              sifname )

    loading( file            , curvel         , curang         , 
             cuhref          , curough        , wavetype       ,
             wavang          , Tp             , Hs             ,
             dtwave          , tdurwave       , tstartwave     ,
             iwaveseed       , iwavespec      , pkdness        ,
             chspread        , ndir           , spreadpar      ,
             chcurprof       , d50            , iroughydload   , 
             fyhydfac        , fzhydfac       , nstep_gapupdate,
             time_gapudate   , chhydloadmodel , kpstartgrid    ,
             kpendgrid       , dxgrid         , inod1pipe      ,
             nelpipe         )

    thist(   file            , thist_inizpen  , thist_wavecur  ,
             tend_static     )

    boncon(  file            , inod1pipe      , inod1seasurf   ,
             nelpipe         )

    materials( file          , rho_sea        ,  kz_seabed     ,
               EA_dum        , EI_dum         ,  GJ_dum        ,
               muy           , imody          ,  kstick        ,
               gamd_sand     , su_clay        ,  gamd_clay     ,
               gams_drain    , su_y_undrain   ,  gams_undrain  ,
               submass       , gacc           ,  ky_inispring  ,
               tend_static   )


    tables( file             , uz_ini         , fyhydpenfac    ,
            fzhydpenfac      , Cm             , Cd             ,
            Cl               )          

    results( file            , ivisual        , nelpipe        , 
             inod1pipe       , iel1seabedcont , iel1pipe       , 
             sifname         )

    file.close()

    #   Update global parameter nstep_dynres
    st.session_state.SIMLA_nstep_dynres = int(nstep_dynres)

    return
