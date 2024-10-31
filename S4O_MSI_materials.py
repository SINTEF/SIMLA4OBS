import numpy as np



def materials( file           , rho_sea        ,  kz_seabed      ,
               EA_dum         , EI_dum         ,  GJ_dum         ,
               muy            , imody          ,  kstick         ,
               gamd_sand      , su_clay        ,  gamd_clay      ,
               gams_drain     , su_y_undrain   ,  gams_undrain   ,
               submass        , gacc           ,  ky_inispring   ,
               tend_static    ):


    if kstick>1e-6:
        ustick = submass*gacc/kstick
    else:
        ustick = 1e-4


    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# MATERIALS\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#         name     type    poiss  talfa    tecond  heatc  beta  EA            EIy           EIZ           GJ\n")
    file.write("MATERIAL  pipemat  linear  0.3    1.17e-5   50     800    0     %E  %E  %E  %E\n" % (EA_dum, EI_dum, EI_dum, GJ_dum ) )
    file.write("#\n")
    file.write("#         E-mod   G-mod\n")
    file.write("          2.1e11  8.0e10\n")
    file.write("#\n")
    file.write("#         name     type    density\n")
    file.write("MATERIAL  seamat   sea     %f\n" % rho_sea )
    file.write("#\n")
    file.write("#         name     type     mux   muy       xname   yname   zname\n")
    file.write("MATERIAL  soilmat  contact  0.0   %f  kzero   soily   soilz\n" % muy )
    file.write("#\n")

    if imody==1:
        file.write("#         name    type     ke              gamd             timeon         izsoil\n")
        file.write("MATERIAL  soily   sand_y   %E    %f     %f       2\n"  % ( kstick, gamd_sand, tend_static ))
    elif imody==2:
        file.write("#         name    type     ke              gamd             su            timeon         izsoil    suz3 \n")
        file.write("MATERIAL  soily   clay_y   %E    %f     %f    %f       2         4000.0\n"  % ( kstick, gamd_clay , su_clay, tend_static ))
    elif imody==3:
        file.write("#         name    type         ke                  timeon   modtyp      gams            softyp \n")
        file.write("MATERIAL  soily   breakout_y   %E   %f      drain_ngi   %f    sym\n"  % ( kstick, tend_static, gams_drain ))
    elif imody==4:
        file.write("#         name    type         ke                  timeon   modtyp        gams            su            softyp \n")
        file.write("MATERIAL  soily   breakout_y   %E   %f      undrain_ngi   %f    %f    sym\n"  % ( kstick, tend_static, gams_undrain, su_y_undrain ))
    elif imody==5:
        file.write("#         name    type         ke                  timeon   modtyp         gams            su           softyp \n")
        file.write("MATERIAL  soily   breakout_y   %E   %f      undrain_dnv2   %f    %f   sym\n"  % ( kstick, tend_static, gams_undrain, su_y_undrain ))
    elif imody==6:
        file.write("#         name    type     disp                 unitforc \n")
        file.write("MATERIAL  soily   epcurve  %f\t\t%f\n" % ( 0.0     , 0.0 ))
        file.write("                           %E\t\t%f\n" % ( ustick  , 1.0 ))
        file.write("                           %f\t%f\n" % ( 1e6     , 1.0 ))

    file.write("#\n")
    file.write("#         name     type      eps                  sigma\n")
    file.write("MATERIAL  soilz    hycurve   %f\t  %E\n"  % ( -1000.0    , -kz_seabed*1000.0 ))
    file.write("                             %f\t\t  %f\n"  % (  0.0       ,  0.0 ))
    file.write("                             %f\t  %f\n"  % (  1000.0    ,  0.0 ))
    file.write("#\n")
    file.write("#         name     type       eps           sigma\n")
    file.write("MATERIAL  kyini    hycurve   %f  %E\n" % ( -1000.0     , -ky_inispring*1000.0 ))  
    file.write("                              %f   %E\n" % (  1000.0     ,  ky_inispring*1000.0 ))
    file.write("#\n")
    file.write("#         name     type      eps           sigma     (dummy curve)\n")
    file.write("MATERIAL  kzero    hycurve  -1000.0        0.0\n")
    file.write("                             1000.0        0.0\n")
    file.write("#\n")







