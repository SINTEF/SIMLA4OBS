import numpy as np

def elements( file           , Lpipe          , mass           ,
              nelpipe        , diam           , zseabed        ,
              submass        , uz_ini         , tend_static    ,
              iel1pipe       , inod1pipe      , iel1seabedcont ,
              iel1seasurf    , inod1seasurf   , ipenmod        ,
              czdamp_seabed  , rho_margrow    , th_margrow     ,
              rho_sea        , uz_cont        ):


    # Postion vectors to pipe ends 1 and 2
    r1pipe = np.array([-0.5*Lpipe, 0.0, zseabed+0.5*diam-0.001])
    r2pipe = np.array([ 0.5*Lpipe, 0.0, zseabed+0.5*diam-0.001])

    # Position vector increment along one pipe element
    drpipe = (r2pipe-r1pipe)/nelpipe

    # Marine growth area calculation
    radi_int = 0.5*diam
    radi_ext = 0.5*diam + th_margrow

    if uz_ini<0:                 # Gap between invert of pipe and seabed                     ####   Må beregne zpen_ini for tilfellet ipenmod==2
        zpen_int = 0.0
    elif uz_ini>2.0*radi_int:    # Fully penetrated pipe into seabed
        zpen_int = 2.0*radi_int
    else:                          # Partly penetrated pipe into seabed
        zpen_int = uz_ini

    if uz_ini<-th_margrow:                    # Gap between invert of marine growth area and seabed
        zpen_ext = 0.0
    elif uz_ini>(2.0*radi_int+th_margrow):    # Fully penetrated marine growth area into seabed
        zpen_ext = 2.0*radi_ext
    else:                                       # Partly penetrated marine growth area into seabed
        zpen_ext = uz_ini + th_margrow
        
    theta_int = np.arccos( (radi_int-zpen_int)/radi_int )
    theta_ext = np.arccos( (radi_ext-zpen_ext)/radi_ext )
        
    Area_submerged_int = np.power(radi_int,2)*theta_int - np.power(radi_int,2)*np.cos(theta_int)*np.sin(theta_int)
    Area_submerged_ext = np.power(radi_ext,2)*theta_ext - np.power(radi_ext,2)*np.cos(theta_ext)*np.sin(theta_ext)
    Area_full_annulus = np.pi*( np.power(radi_ext,2) - np.power(radi_int,2) )

    Area_margrow = Area_full_annulus - Area_submerged_ext + Area_submerged_int

    # Total pipe mass
    masstot = mass + rho_margrow*Area_margrow

    # Total submerged pipe mass
    submasstot = submass + rho_margrow*Area_margrow - Area_margrow*rho_sea

    # Trick to get correct hydrodynamic diameter in SIMLA
    OD_wrap = 1e-5
    rks = (2*th_margrow)/(OD_wrap-diam)

    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# NODAL COORDINATES\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#                    nodID        x             y                z\n")
    file.write("NOCOOR coordinates       1       %f\t%f\t%f\n" % ( r1pipe[0], r1pipe[1], r1pipe[2] ))
    file.write("                         %i        %f\t%f\t%f\n" % ( nelpipe+1, r2pipe[0], r2pipe[1], r2pipe[2]))
    file.write("#\n")
    file.write("#                    nodID        x          y          z\n")
    file.write("NOCOOR coordinates   %i        1.0       -1.0        0.0\n" % inod1seasurf   )
    file.write("                     %i        1.0        1.0        0.0\n" % (inod1seasurf+1) )
    file.write("                     %i       -1.0        1.0        0.0\n" % (inod1seasurf+2) )
    file.write("                     %i        1.0       -1.0        0.0\n" % (inod1seasurf+3) )
    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# ELEMENT CONNECTIVITY\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#      elgroup   elty     material    elID      nod1    nod2              nrepeat   elinc   nodinc\n")
    file.write("ELCON  pipe      pipe31   pipemat     %i\t\t%i\t%i\trepeat\t  %i\t    1\t    1\n" % ( iel1pipe, inod1pipe, inod1pipe+1, nelpipe ))
    file.write("#\n")
    file.write("#      elgroup   elty     cosurfname  elID      nod1              nrepeat   elinc   nodinc\n") 
    file.write("ELCON  seabed    cont126  cosurf      %i\t%i\trepeat\t  %i\t    1\t    1\n" % ( iel1seabedcont, inod1pipe, nelpipe+1 ))
    file.write("#\n")
    file.write("#      elgroup   elty     material    elID      nod1    nod2    nod3    nod4\n")
    file.write("ELCON  sea       sea150   seamat      %i\t%i\t%i\t%i\t%i\n" % 
               ( iel1seasurf, inod1seasurf, inod1seasurf+1, inod1seasurf+2, inod1seasurf+3 ))
    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# ELEMENT ORIENTATION\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#         type         elID     x          y          z                   nrepeat   elinc  xinc      yinc      zinc\n")
    file.write("ELORIENT  coordinates  %i       %f   %f  %f   repeat   %i       1      %f  %f  %f\n" % 
               ( iel1pipe, r1pipe[0], r1pipe[1]+1.0, r1pipe[2], nelpipe, drpipe[0], drpipe[1], drpipe[2] ))
    file.write("#\n")
    file.write("#         type         elID    eulx    euly   eulz          nrepeat  elinc   eulxinc   eulyinc   eulzinc\n")
    file.write("ELORIENT  eulerangle  %i    0.0     0.0    0.0    repeat   %i\t     1\t     0.0       0.0       0.0\n" % ( iel1seabedcont, nelpipe+1 ))
    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# ELEMENT PROPERTIES\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#       elgroup  type  rad        th      CDr   Cdt   CMr   CMt   wd           ws           ODp         ODw         rks\n")
    file.write("ELPROP  pipe     pipe  %f   0.002   0.0   0.0   1.0   1.0   %f    %f    %f    %f   %f\n" % 
               ( 0.5*diam, masstot, submasstot, diam, OD_wrap, rks ))
    file.write("#\n")
    file.write("#       elgroup  type         tx     ty    tz    ttx   thistx  thisty  thistz  thisttx\n") 
    file.write("ELPROP  seabed   soilcontact  1e6    0.0   1e6   1e6   220     210     220     220\n")
    file.write("#\n")
    if uz_ini<uz_cont:
        file.write("#       xname  yname  zname  txname\n")  
        file.write("        kzero  kzero  kzero  kzero\n" )
    else:
        file.write("#       xname  yname  zname  txname   t0_uz      thistuz   uzname\n")  
        file.write("        kzero  kyini  kzero  kzero    %f   250       inizpen\n" % tend_static )
    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# ELEMENT DAMPING\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#       elgroup  type     c1   c2   c3\n")
    file.write("ELDAMP  seabed   contact  0.0  0.0  %f\n" % czdamp_seabed )
    file.write("#\n")
    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# CONTACT INTERFACES\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#        elgroup  master  slavename   is1   isn   tx    ty         tz    maxit  igap\n")
    file.write("CONTINT  seabed   pipe    cosurf      %i\t    %i\t  1e6   %f   0.0   60     2\n" % 
               ( inod1pipe, inod1pipe+nelpipe, tend_static))
    file.write("CONTINT  sea      sea     pipe\n")
    file.write("#\n")