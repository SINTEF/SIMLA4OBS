import numpy as np

def boncon( file         , inod1pipe    , inod1seasurf  ,
            nelpipe      ):


    file.write("#\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# BOUNDARY CONDITIONS\n")
    file.write("#-----------------------------------------------------------------------------------------------------------------------------\n")
    file.write("#\n")

    inod2pipe = inod1pipe + nelpipe

    file.write("#        type     nodID    dof\n")
    file.write("BONCON   global   %i        1\n" %  ( inod1pipe ))  
    file.write("BONCON   global   %i        4\n" %  ( inod1pipe ))  
    file.write("BONCON   global   %i        5\n" %  ( inod1pipe ))  
    file.write("BONCON   global   %i        6\n" %  ( inod1pipe ))  
    file.write("#\n")
    file.write("BONCON   global   %i        1\n" %  ( inod1pipe+nelpipe )) 
    file.write("BONCON   global   %i        4\n" %  ( inod1pipe+nelpipe )) 
    file.write("BONCON   global   %i        5\n" %  ( inod1pipe+nelpipe )) 
    file.write("BONCON   global   %i        6\n" %  ( inod1pipe+nelpipe ))

    file.write("#\n")
    file.write("#        type     refsys    slnod  sldof  c0   manod  madof  c1\n")
    file.write("CONSTR   coneq    global    %i      2      0.0  %i      2      1.0\n" %  ( inod1pipe+nelpipe, inod1pipe  ))
    file.write("CONSTR   coneq    global    %i      3      0.0  %i      3      1.0\n" %  ( inod1pipe+nelpipe, inod1pipe  )) 


    file.write("#\n")
    file.write("#        type     nodID    dof             nrepeat   nodinc\n")
    file.write("BONCON   global   %i    1     repeat    4         1\n" % inod1seasurf )
    file.write("BONCON   global   %i    2     repeat    4         1\n" % inod1seasurf )
    file.write("BONCON   global   %i    3     repeat    4         1\n" % inod1seasurf )
    file.write("#\n")
