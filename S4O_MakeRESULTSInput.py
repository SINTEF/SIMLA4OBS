import numpy as np
import os

def results( file           , ivisual       , nelpipe         , inod1pipe  ,
             iel1seabedcont , iel1pipe      , sifname         ):

    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# RESULTS\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")

    if ivisual==1:
        file.write("#        mode          factor   results\n")
        file.write("VISRES   integration   1.0      vcondis-x  vcondis-y  vcondis-z  vconfor-x  vconfor-y  vconfor-z\n") 
        file.write("#\n")

    if nelpipe < 2:
        inodpipe_mid = inod1pipe
        ielpipe_mid = iel1pipe
        ielseabedcont_mid = iel1seabedcont
    else:
        inodpipe_mid = np.ceil((inod1pipe + inod1pipe + nelpipe)/2)
        ielpipe_mid  = np.ceil((iel1pipe + iel1pipe + nelpipe-1)/2)
        ielseabedcont_mid = np.ceil((iel1seabedcont + iel1seabedcont + nelpipe)/2)

    run_dir = os.path.dirname(sifname)
    filedynpost = open(run_dir + '/s.sdi',"w")

    filedynpost.write("#         *.dyn   *.mpf         plotno   yscale\n")

    idynres = 0

    file.write("#          type   elem    end  DOF\n")
    idynres = idynres + 1
    file.write("DYNRES_E   2      %i   1    2\n" % ( ielseabedcont_mid ) )
    filedynpost.write("DYNPLOT   S       \"fy-seabed\"   %i        1.0\n" % ( idynres ))
    idynres = idynres + 1
    file.write("DYNRES_E   2      %i   1    3\n" % ( ielseabedcont_mid ) )
    filedynpost.write("DYNPLOT   S       \"fz-seabed\"   %i        1.0\n" % ( idynres ))

    idynres = idynres + 1
    file.write("DYNRES_E   3          %i   1    2\n" % ( ielpipe_mid ) )
    filedynpost.write("DYNPLOT   S       \"fy-hydro\"    %i        1.0\n" % ( idynres ))
    idynres = idynres + 1
    file.write("DYNRES_E   3          %i   1    3\n" % ( ielpipe_mid ) )
    filedynpost.write("DYNPLOT   S       \"fz-hydro\"    %i        1.0\n" % ( idynres ))

    file.write("#\n")
    file.write("#          type  nodID  DOF\n")
    idynres = idynres + 1
    file.write("DYNRES_N   1     %i      2\n" % ( inodpipe_mid ) )
    filedynpost.write("DYNPLOT   S       \"uy-pipe\"     %i        1.0\n" % ( idynres ))

    file.write("#\n")
    file.write("#          type   elem    igau  ipoint\n")
    idynres = idynres + 1
    file.write("DYNRES_I   3      %i   1     1\n" % ( ielseabedcont_mid ) )
    filedynpost.write("DYNPLOT   S       \"soilpen\"     %i        1.0\n" % ( idynres ))

    file.write("#\n")

    filedynpost.close()

    return
#
#