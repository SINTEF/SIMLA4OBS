import os

def seabed( file    ,  Lpipe  ,  zseabed  ,
            siffile   ):

    run_dir = os.path.dirname(siffile)
    fileseabed = open(run_dir + '/seabed.txt',"w")

    x1 = -Lpipe
    x2 = -x1
    dy = 50.0
    
    fileseabed.write("%f   %f   %f   0.0   0.0   1.0   %f   %f   %f   0.0   0.0   1.0   %f   %f   %f   0.0   0.0   1.0\n" %
                     (x1, 0.0, zseabed, x1, dy, zseabed, x1, -dy, zseabed) )
    fileseabed.write(" %f   %f   %f   0.0   0.0   1.0    %f   %f   %f   0.0   0.0   1.0    %f   %f   %f   0.0   0.0   1.0\n" %
                     (x2, 0.0, zseabed, x2, dy, zseabed, x2, -dy, zseabed) )
    

    file.write("#\n")
    file.write("#           name     datafile       nlin    kp0        x0     y0     fi    lineids \n")
    file.write("COSURFPR    cosurf   \"seabed.txt\"   3      %f   0.0    0.0    0.0   100     100   100\n" % -Lpipe ) 
    file.write("#\n")

    file.write("#\n")
    file.write("#        lineID   kp1       kp2       matname\n")
    file.write("COSUPR   100     -10000.0   10000.0   soilmat\n") 
    file.write("#\n")

    fileseabed.close()
