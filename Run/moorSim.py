import numpy as np

def simLinesInit():
    import ctypes
    # Setup
    X = (ctypes.c_double*6)(0.0)                     # platform position
    XD = (ctypes.c_double*6)(0.0)                    # platform velocity
    
    # Initialization
    MD_lib = ctypes.windll.LoadLibrary('lines.dll')
    MD_lib.LinesInit(X,XD)   # initialize MoorDyn
    MD_lib.GetFairTen.restype = ctypes.c_double
    
    return MD_lib
    
def simLines(moorLib,pos,vel,time,dt,dof):
    import ctypes
    # Correct form of pos & vel
    pos1 = np.zeros(6)
    vel1 = np.zeros(6)
    if sum(dof) < 2:
        pos1[dof.index(1)] = pos
        vel1[dof.index(1)] = vel
    else:
        for i in range(6):
            if dof[i]==1:
                pos1[i] = pos[i]
                vel1[i] = vel[i]

    # Setup
    X = (ctypes.c_double*6)(0.0)                     # platform position
    XD = (ctypes.c_double*6)(0.0)                    # platform velocity
    for i in range(6):
        if dof[i]==1:
            X[i] = pos1[i]
            XD[i] = vel1[i]
    
    dtc = ctypes.c_double(dt)
    
    FairTens1 = np.zeros(2)           # array for storing fairlead 1 tension time series
    
    Flines_p = (ctypes.c_double*6)(0.0)           # going to make a pointer so LinesCalc can modify FLines
    Fmoor = np.zeros(6)
    
    # Simulation
    tc = ctypes.c_double(time)
    moorLib.LinesCalc(X,XD,Flines_p,ctypes.byref(tc),ctypes.byref(dtc))
    FairTens1[1] = moorLib.GetFairTen(ctypes.c_int(1))           # store fairlead 1 tension
        
    # Ending
    for i in range(6):
        Fmoor[i] = Flines_p[i]

    # Return force matrix
    if sum(dof)<2:
        return Fmoor[dof.index(1)]
    else:
        return Fmoor
    
def simClose(moorLib):
    moorLib.LinesClose()
    del moorLib

def openLines(fileName):
    with open(fileName,'r') as f:
        data = f.readlines()
        
    mdLines = dict()
    # Find different sections
    indList = []
    for iL in range(len(data)):
        if data[iL][0:2] == '--':
            indList.append(iL)
            
    # Line Dictionary
    count = 1
    mdLines['nrLineTypes'] = 0
    for iL in range(indList[0]+3,indList[1]):
        line = data[iL].split()
        mdLines['nrLineTypes'] += 1
        mdLines['linetype_{:d}'.format(count)] = line
        count += 1
        
    # Node Properties
    count = 1
    mdLines['nrNodes'] = 0
    for iL in range(indList[1]+3,indList[2]):
        line = data[iL].split()
        mdLines['nrNodes'] += 1
        mdLines['node_{:d}'.format(count)] = line[1::]
        count += 1

    # Line Properties
    count = 1
    mdLines['nrLines'] = 0
    for iL in range(indList[2]+3,indList[3]):
        line = data[iL].split()
        mdLines['nrLines'] += 1
        mdLines['line_{:d}'.format(count)] = line[1::]
        count += 1

    return mdLines