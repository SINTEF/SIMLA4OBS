def loading( file              , curvel           , curang          , 
             cuhref            , curough          , wavetype        ,
             wavang            , Tp               , Hs              ,
             dtwave            , tdurwave         , tstartwave      ,
             iwaveseed         , iwavespec        , pkdness         ,
             chspread          , ndir             , spreadpar       ,
             chcurprof         , d50              , iroughydload    , 
             fyhydfac          , fzhydfac         , nstep_gapupdate ,
             time_gapudate     , chhydloadmodel   , kpstartgrid     ,
             kpendgrid         , dxgrid           , inod1pipe       ,
             nelpipe           ):
             


    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# HYDRODYNAMIC LOADING\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#             elgrp   loadno   histno   curvel     curang      cuhref     crough       type        x0    y0    wavang\n")
    file.write("DROPS_LOAD    sea     100      300      %f   %f   %f   %.9f  %s   0.0   0.0   %f\n" % 
               ( curvel, curang, cuhref, curough, wavetype, wavang) ) 
    file.write("#\n")

    if chcurprof=="standard":

        file.write("#             Tp          Hs          dt         tdur           tstart     seed         spec   curprof\n")
        file.write("              %f   %f   %f   %f   %f   %i   %i      standard\n" %
                   (  Tp, Hs, dtwave, tdurwave, tstartwave, iwaveseed, iwavespec) )
        file.write("#\n")

        if chspread=="short":
            file.write("#             pkdness    spread  ndir   spreadpar\n")
            file.write("              %f   short   %i     %f\n" % ( pkdness, ndir, spreadpar) )
        elif chspread=="long":
            file.write("#             pkdness    spread  ndir   spreadpar\n")
            file.write("              %f   long    1      0.0\n" % pkdness )

    elif chcurprof=="rpf109":

        file.write("#             Tp          Hs          dt         tdur           tstart     seed         spec   curprof   d50\n")
        file.write("              %f   %f   %f   %f   %f   %i   %i      rpf109    %.9f\n" %
                   (  Tp, Hs, dtwave, tdurwave, tstartwave, iwaveseed, iwavespec, d50) )
        file.write("#\n")

        if chspread=="short":
            file.write("#             pkdness    spread  ndir   spreadpar\n")
            file.write("              %f   short   %i     %f\n" % ( pkdness, ndir, spreadpar) )
        elif chspread=="long":
            file.write("#             pkdness    spread  ndir   spreadpar\n")
            file.write("              %f   long    1      0.0\n" % pkdness )


    file.write("#\n")
    file.write("#             irough   yredfac    zredfac    nstep   nelgrp   t_1 ... t_n\n")
    file.write("DROPS_HCOEF   %i        %f   %f   %i       1        " % 
               ( iroughydload, fyhydfac, fzhydfac, nstep_gapupdate) )
    
    for elem in time_gapudate:
        file.write("%f   " %  elem )

    file.write("\n#\n")
    file.write("#             gapmori   loadtyp   massname   liftname   dragname   elgrp   ypenredname   zpenredname\n")
    file.write("              1e6       %s      masscoef   liftcoef   dragcoef   pipe    fyhydpenfac    fzhydpenfac\n" % chhydloadmodel )   
    file.write("#\n")
    file.write("#             coname   loadno   kpstart    kpend      dx \n")
    file.write("DROPS_GRID    cosurf   100     %f   %f   %f \n" % (kpstartgrid, kpendgrid, dxgrid) ) 


    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# EXTERNAL PRESSURE AND GRAVITY LOADING\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")
    file.write("#        preshist   gravhist\n")
    file.write("PELOAD   100        150\n")
    file.write("#\n")