import numpy as np


def penetration(  submass_lay ,  diam         ,  EI           ,  
                  T0          ,  rho_sea      ,  gamd_sand    ,
                  gamd_clay   ,  gams_drain   ,  gams_undrain ,
                  su_clay     ,  su_z_undrain ,  kz_const     ,  
                  gacc        ,  imodz        ):

    # Verley & Sotberg
    def sand( diam, gamd_sand, rho_sea, gacc, Fz ):

        a = 0.037
        b = 2.0/3.0

        gams_sand = gamd_sand - rho_sea*gacc
        if gams_sand<1e-6:
            gams_sand = 1e-6

        uz = a*diam*(Fz/gams_sand/diam**2)**b

        return uz

    # Verley & Lund
    def clay( diam, gamd_clay, su_clay, Fz ):

        a = 0.0071
        b = 0.062
        c = 0.3
        d = 3.2
        e = 0.7

        G = su_clay/gamd_clay/diam

        uz = a*diam*(G**c/su_clay/diam*Fz)**d + b*diam*(G**c/su_clay/diam*Fz)**e

        return uz
    
    # NGI drained soil
    def ngi_drain( diam, gams_drain, Fz ):

        a = 0.09
        b = 0.75

        uz = a*diam*(Fz/gams_drain/diam**2)**b

        return uz

    # NGI undrained soil / DNV model 2 undrained soil
    def ngi_undrain( diam, gams_undrain, su_z_undrain, Fz ):

        uz = 0.0          #   Start at uz=0.0 to avoid diverging Newton-Raphson
        zr_tol = 1e-12

        a = 6.0
        b = 0.25
        c = 3.4
        d = 0.5
        e = 1.5
        f = 1.0
    
        cw_tol=1e-20      # Contact width tolerance for avoiding division by zero
        Ap_tol=1e-25      # Soil penetration area tolerance for avoiding division by zero if f<1.0
        dSu_dz = 0.0      # = 0 since constant su wrt. depth in current implementation

        g = 1000
        iter = 0
        itermax = 100

        while g>1e-6 and iter<itermax:

            iter = iter + 1
            zr = uz/diam

            # Force and stiffness from Su-proportional term
            r1 = a*zr**b
            r2 = c*(10.0*zr)**d
            if r1<r2:
                fz1 = r1*diam*su_z_undrain
                if zr<zr_tol:
                    r2  = a*b*zr_tol**(b-1.0)
                else:
                    r2  = a*b*zr**(b-1.0)
                kz1 = r2*su_z_undrain + r1*diam*dSu_dz
            else:
                fz1 = r2*diam*su_z_undrain
                if zr<zr_tol:
                    r1  = c*d*(10.0*zr_tol)**(d-1.0)
                else:
                    r1  = c*d*(10.0*zr)**(d-1.0)
                kz1 = r1*10.0*su_z_undrain + r2*diam*dSu_dz

            # Penetrated soil area and its derivative
            if zr<0.5: 
                # Contact width
                cw = 2.0*diam*np.sqrt(zr-zr**2)
                if cw<cw_tol:
                    cw = cw_tol
                    zr = 0.5 - 0.5*np.sqrt(1.0 - 4.0*(cw/diam/2.0)**2.0)

                r1 = 1.0 - np.cos(np.asin(cw/diam))*(1.0-2.0*zr)
                r2 = 0.5*diam**2 * r1
                dAp_dz = 0.5*cw + r2/cw 

                Ap = 0.25*diam**2.0 * np.asin(cw/diam) - 0.25*cw*diam*np.cos(np.asin(cw/diam))
                if Ap<Ap_tol and f<1.0:
                    Ap=dAp_dz*np.abs(uz)
            else:
                # contact width
                cw = diam

                Ap = 0.125*np.pi*diam**2.0 + diam**2.0*(zr-0.5)
                dAp_dz = diam


            r1 = e*(gams_undrain*Ap/diam/su_z_undrain)**f
            r2 = e*f*(gams_undrain*Ap/diam/su_z_undrain)**(f-1.0)

            # Stiffness from gams-term
            kz2 = r2*gams_undrain*dAp_dz
            kz3 = -r2*gams_undrain*Ap/su_z_undrain*dSu_dz
            kz4 = r1*diam*dSu_dz

            # Total stiffness
            kz = kz2 + kz3 + kz4 + kz1

            # Residual force
            g = Fz - r1*diam*su_z_undrain - fz1

            uz = uz + g/kz

        return uz



    # CALCULATE INITIAL PENETRATION

    uz_ini = 0.0
    uz_equ = uz_ini
    uz_zero = 1e-12
    T0_zero = 1e-6
    T0_min = (3.0*np.sqrt(EI)*submass_lay)**(2.0/3.0)

    delta_klay = 1e6
    delta_klay_tol = 1e-6
    klay = 1.0
    itermax = 50
    iter = 0

    while abs(delta_klay)>delta_klay_tol and iter<=itermax:

        iter = iter + 1
        klay_old = klay

        Fz = submass_lay*gacc*klay

        # 1: 'V&S Sand', 2: 'V&L Clay', 3: 'NGI Drained', 4: 'NGI Undrained/DNV Model 2 Undrained', 5: 'Constant stiffness']
        if imodz==1:
            uz_ini = sand( diam, gamd_sand, rho_sea, gacc, Fz )
        elif imodz==2:
            uz_ini = clay( diam, gamd_clay, su_clay, Fz )
        elif imodz==3:
            uz_ini = ngi_drain( diam, gams_drain, Fz )
        elif imodz==4:
            uz_ini = ngi_undrain( diam, gams_undrain, su_z_undrain, Fz )
        elif imodz==5:
            uz_ini = Fz/kz_const

        if iter==1:
            uz_equ=uz_ini

        if T0>T0_min and T0>T0_zero and uz_ini>uz_zero:
            kz_secant = Fz/uz_ini
            klay = 0.6 + 0.4*(EI*kz_secant/T0**2)**0.25

        delta_klay = klay - klay_old

    if klay<1.0 or abs(delta_klay)>delta_klay_tol:
        uz_ini = uz_equ


    return uz_ini






