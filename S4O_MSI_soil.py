import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

def soil( file        , zSu          , gamma      ,
          Su          , submasspipe  , EI         ,
          T0          , ODpipe       , gacc       ,
          Su_r        , isu_zdir     ):


    def Qvcurve(z_vec,ODpipe,Su,gamma,Qv_equ):

        # Equations taken from Model 2 in DNV-RP-F114

        Qval0=0
        z0=0
        Qv_vec =np.array([])

        for z in z_vec:

            # Contact width
            if z<0.5*ODpipe:
                B = 2*np.sqrt(ODpipe*z-np.power(z,2))
            else:
                B = ODpipe

            # Soil-penetrating area
            if z<0.5*ODpipe:
                Abm = np.arcsin(B/ODpipe)*0.25*np.power(ODpipe,2)-0.25*B*ODpipe*np.cos(np.arcsin(B/ODpipe))
            else:
                Abm = 0.125*np.pi*np.power(ODpipe,2) + ODpipe*(z-0.5*ODpipe)

            # Su-parameter
            Su_val = np.interp(z,zSu,Su)

            zrel = z/ODpipe
            zfac1 = 6.0*np.power(zrel,0.25)
            zfac2 = 3.4*np.sqrt(10*zrel)
            zfac = np.min( [zfac1, zfac2] )

            # Vertical force
            Qval = ( zfac + ( 1.5*gamma*Abm ) / (ODpipe*Su_val)   ) * ODpipe*Su_val
            Qv_vec = np.append(Qv_vec,Qval)


            # Equilibrium penetration
            if Qval0<Qv_equ and Qval>=Qv_equ:

                # Linear interpolation
                zpen_equ = ( z*(Qv_equ-Qval0)+z0*(Qval-Qv_equ)  )/(Qval-Qval0)


            # For calculation of equilibrium penetration
            Qval0=Qval
            z0=z

        return Qv_vec, zpen_equ

    # Submerged weight
    ws = submasspipe*gacc

    # Penetrations
    dz = 0.001                                  # dz must be maximum 0.001 due to the linear interpolation applied to compute equilibrium penetration
    z_vec =np.arange(zSu[0], zSu[2], dz)


    if isu_zdir==1:
        Su_zdir = Su_r      # Use remoulded soil shear strength to account for laying effects in a simplified way
    else:
        Su_zdir = Su


    # Calculate vertical force "Qv_vec" for each embedment in "z_vec", and equilibrium penetration "zpen_equ" for cable submerged weight "ws"
    #  Assume "Su" undisturbed shear strength shall be used in calculation of initial embedment
    Qv_vec, zpen_equ = Qvcurve(z_vec,ODpipe,Su_zdir,gamma,ws)


    # Static lay factor according to DNV-RP-F114
    # Initial embedment for OBS analysis based on max vertical force in laying operation, accounting only for the static effect due to force concentration at TDP)
    #  Assume "Su" undisturbed shear strength shall be used in calculation of initial embedment. NOTE: RP-114 suggest "remoulded" shear strength can be applied to account for laying dynamics, however, this is not specified in design basis
    T0min = np.power( 3*np.sqrt(EI)*ws, (2.0/3.0) )
    if T0>T0min:

        delta_klay = 1.0e12
        Qvmax = ws
        Qv_vec, zpen_ini = Qvcurve(z_vec,ODpipe,Su_zdir,gamma,Qvmax)

        while delta_klay>1e-6:

            klay_old = Qvmax/ws
            kz_secant = Qvmax/zpen_ini
            klay = 0.6 + 0.4*np.power((EI*kz_secant)/(np.power(T0,2.0)),0.25)

            Qvmax = klay*ws
            Qv_vec, zpen_ini = Qvcurve(z_vec,ODpipe,Su_zdir,gamma,Qvmax)

            delta_klay = klay - klay_old
            klay_old

        if klay>3.0 or klay<1.0:
            print("klay factor outside of validity range")
            quit()

    else:
        klay=1.0
        Qvmax = klay*ws
        zpen_ini = zpen_equ


    # Estimate vertical stiffness by considering displacement around zpen_ini  (Not used)
    Q1 = 0.99*Qvmax
    Q2 = 1.01*Qvmax
    Qv_vec, z1 = Qvcurve(z_vec,ODpipe,Su_zdir,gamma,Q1)
    Qv_vec, z2 = Qvcurve(z_vec,ODpipe,Su_zdir,gamma,Q2)
    kz_seabed = (Q2-Q1)/(z2-z1) 

    # Undisturbed soil shear strength shall be used in y-direction, since laying is assumed to not affect the soil properties in y-direction
    Su_val = np.interp(zpen_ini,zSu,Su)

    # DNV-RP-F114 breakout resistance based on "remoulded" shear strengt Su_r
    #Fl_brk_Sur = (  1.7*np.power(zpen_ini/ODpipe,0.61) + 0.23*np.power(ws/(Sur_val*ODpipe),0.83) + 0.6*gamma*ODpipe/Sur_val*np.power(zpen_ini/ODpipe,2.0)   ) *Sur_val*ODpipe

    # DNV-RP-F114 breakout resistance based on "undisturbed" shear strengt Su
    Fl_brk = (  1.7*np.power(zpen_ini/ODpipe,0.61) + 0.23*np.power(ws/(Su_val*ODpipe),0.83) + 0.6*gamma*ODpipe/Su_val*np.power(zpen_ini/ODpipe,2.0)   ) *Su_val*ODpipe

    # DNV-RP-F114 residual resistance
    Fl_res = ( 0.32 + 0.8*np.power(zpen_ini/ODpipe,0.8) ) * ws

    # DNV-RP-F114 breakout mobilization displacements
    ybrk_LE = 0.004*ODpipe + 0.02*zpen_ini
    ybrk_BE = 0.02*ODpipe  + 0.25*zpen_ini
    ybrk_HE = 0.1*ODpipe   + 0.70*zpen_ini

    # DNV-RP-F114 residual mobilization displacements
    yres_LE = 0.6*ODpipe
    yres_BE = 1.5*ODpipe
    yres_HE = 2.8*ODpipe









    # NGI breakout resistance based on "remoulded" shear strengt Su_r
    #Fl_brk_NGI_Sur = (  0.78*np.power(zpen_ini/ODpipe,0.61) + 0.12*np.power(ws/(Sur_val*ODpipe),0.83) + 0.71*gamma*ODpipe/Sur_val*np.power(zpen_ini/ODpipe,2.0)   ) *Sur_val*ODpipe

    # NGI breakout resistance based on "undisturbed" shear strengt Su
    Fl_brk_NGI = (  0.78*np.power(zpen_ini/ODpipe,0.61) + 0.12*np.power(ws/(Su_val*ODpipe),0.83) + 0.71*gamma*ODpipe/Su_val*np.power(zpen_ini/ODpipe,2.0)   ) *Su_val*ODpipe

    # NGI residual resistance
    Fl_res_NGI = ( 0.3 + 0.76*np.power(zpen_ini/ODpipe,0.8) ) * ws

    # NGI breakout mobilization displacements
    ybrk_LE_NGI = 0.15*( 1.0 + 0.42*np.log(zpen_ini/ODpipe + 0.1) ) *ODpipe
    ybrk_BE_NGI = 0.40*( 1.0 + 0.41*np.log(zpen_ini/ODpipe + 0.1) ) *ODpipe
    ybrk_HE_NGI = 0.80*( 1.0 + 0.40*np.log(zpen_ini/ODpipe + 0.1) ) *ODpipe

    # NGI residual mobilization displacements
    yres_LE_NGI = ODpipe *np.min([0.80*zpen_ini/ODpipe+0.03, 0.6])
    yres_BE_NGI = ODpipe*np.min([1.85*zpen_ini/ODpipe+0.20, 1.5])
    yres_HE_NGI = ODpipe *np.min([2.90*zpen_ini/ODpipe+0.37, 2.8])



    # Validity check for residual resistance
    #if ws > (2*Sur_val*ODpipe):
    #    print("Residual resistance is not valid for the considered remoulded shear strength")
    if ws > (2*Su_val*ODpipe):
        print("Residual resistance is not valid for the considered undisturbed shear strength")


    iplot=0
    if iplot==1:

        # For curve plotting
        y_LE_NGI =np.array([0.0, ybrk_LE_NGI, yres_LE_NGI, 10*ODpipe])
        y_BE_NGI =np.array([0.0, ybrk_BE_NGI, yres_BE_NGI, 10*ODpipe])
        y_HE_NGI =np.array([0.0, ybrk_HE_NGI, yres_HE_NGI, 10*ODpipe])
        Fl_NGI =np.array([0.0, Fl_brk_NGI, Fl_res_NGI, Fl_res_NGI])

        # For curve plotting
        y_LE =np.array([0.0, ybrk_LE, yres_LE, 10*ODpipe])
        y_BE =np.array([0.0, ybrk_BE, yres_BE, 10*ODpipe])
        y_HE =np.array([0.0, ybrk_HE, yres_HE, 10*ODpipe])
        Fl =np.array([0.0, Fl_brk, Fl_res, Fl_res])

        #kz_secant = Qvmax/z_vec[1:len(z_vec)]
        #klay = 0.6 + 0.4*np.power((EI*kz_secant)/(np.power(T0,2.0)),0.25)


        #plt.figure('klay plot')
        #plt.axes([0.11,0.121,0.88,0.805])
        #plt.plot(Qv_vec/ws, np.flip(z_vec) ,color='k',linewidth=1, label='klay1')
        #plt.plot(klay ,np.flip(z_vec[1:len(z_vec)]) ,color='g',linewidth=1, label='klay2')
        #plt.plot(Qv_vec/ws, (z_vec) ,color='b',linewidth=1, label='klay1')
        #plt.plot(klay ,(z_vec[1:len(z_vec)]) ,color='r',linewidth=1, label='klay2')
        #plt.legend(loc=1)
        #plt.xlabel(r'klay [-]')
        #plt.ylabel(r'Penetration $[\mathrm{m}]$')
        #plt.xlim(0,5)
        #plt.ylim(0,0.1)
        #plt.grid()



        plt.figure('Hyper-elastic curve for vertical force vs. penetration ')
        plt.axes([0.11,0.121,0.88,0.805])
        plt.plot(z_vec ,Qv_vec ,color='b',linewidth=1, label='Vertical force')
        plt.plot([zSu[0],zSu[2]] ,[ws,ws] ,color='r',linewidth=1,linestyle='dashed',label='Cable submerged weight')
        plt.plot([zSu[0],zSu[2]] ,[Qvmax,Qvmax] ,color='k',linewidth=1,linestyle='dashed',label='Maximum vertical force during installation')
        plt.plot([0.5*ODpipe,0.5*ODpipe] ,[0,np.max(Qv_vec)] ,color='g',linewidth=1,linestyle='dashed',label='Penetration limit z/ODpipe=0.5')
        plt.plot([zpen_ini,zpen_ini] ,[0,np.max(Qv_vec)] ,color='c',linewidth=1,linestyle='dashed',label='Initial embedmendt for OBS analysis')
        plt.plot([zpen_equ,zpen_equ] ,[0,np.max(Qv_vec)] ,color='m',linewidth=1,linestyle='dashed',label='Equilibrum penetration for cable submerged weight')
        plt.legend(loc=1)
        plt.xlabel(r'Penetration $[\mathrm{m}]$')
        plt.ylabel(r'$[\mathrm{N/m}]$')
        plt.xlim(zSu[0],ODpipe)
        plt.ylim(0,1.5*Qvmax)
        #plt.ylim(0,750)
        plt.grid()


        plt.figure('Lateral resistance vs. lateral displacement')
        plt.axes([0.11,0.121,0.88,0.805])
        plt.plot(y_LE ,Fl ,color='r',linewidth=1, label='DNV LE')
        plt.plot(y_BE ,Fl ,color='g',linewidth=1, label='DNV BE')
        plt.plot(y_HE ,Fl ,color='b',linewidth=1, label='DNV HE')
        plt.plot(y_LE_NGI ,Fl_NGI ,color='r',linewidth=1, linestyle='dashed',label='NGI LE')
        plt.plot(y_BE_NGI ,Fl_NGI ,color='g',linewidth=1, linestyle='dashed',label='NGI BE')
        plt.plot(y_HE_NGI ,Fl_NGI ,color='b',linewidth=1, linestyle='dashed',label='NGI HE')
        plt.plot([0,5*ODpipe] ,[Fl_brk,Fl_brk] ,color='c',linestyle='dashdot',linewidth=1, label='DNV breakout force')
        plt.plot([0,5*ODpipe] ,[Fl_brk_NGI,Fl_brk_NGI] ,color='m',linestyle='dashdot',linewidth=1, label='NGI breakout force')
        plt.legend(loc=1)
        plt.xlabel(r'Lateral displacement $[\mathrm{m}]$')
        plt.ylabel(r'Lateral force $[\mathrm{N/m}]$')
        plt.xlim(0,0.8)
        plt.ylim(0,220)
        #plt.ylim(0,650)
        plt.grid()

        plt.show()



    return zpen_ini, Fl_brk, Fl_res, ybrk_BE, yres_BE

