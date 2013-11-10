##def openResults(modelName):
##    odbName = "%s.odb" % (modelName)
##    odb = session.openOdb(odbName)
##    return odb
##
##def getReactionForces(odb):
##    frame = odb.steps['ApplyLoad'].frames[-1]
##    rfField = frame.fieldOutputs['RF']
##    xFaceNodes = odb.rootAssembly.nodeSets['XFACENODES']
##    rfSubField = rfField.getSubset(region=xFaceNodes)
##    rf1, rf2, rf3 = 0, 0, 0
##    for value in rfSubField.values:
##        rf1 = rf1+value.data[0]
##        rf2 = rf2+value.data[1]
##        rf3 = rf3+value.data[2]
##    return (rf1, rf2, rf3)
##
##def getJTable(odb):
##    region = odb.steps['ApplyLoad'].historyRegions['ElementSet  PIBATCH']
##    jList = []
##    nodeSetLabel = 'CRACKLINE'
##    crackNodes=odb.rootAssembly.nodeSets[nodeSetLabel].nodes[0]
##    for i in range(1,len(crackNodes)+1): # positions along crack
##        jTempRow = []
##        nodeSetLabel = 'JINT_CRACK_J_CRACKLINE-F%d__Contour_%d' % (i, 1)
##        crackNode = odb.rootAssembly.nodeSets[nodeSetLabel].nodes[0][0]
##        nodeLabel = crackNode.label
##        nodeCoords = crackNode.coordinates.tolist()
##        jTempRow.append(nodeLabel)
##        for coord in nodeCoords:
##            jTempRow.append(coord)
##        for j in range(1,7): # contours around position
##            jLabel = 'J at JINT_CRACK_CRACKLINE-F%d__Contour_%d' % (i, j)
##            jTemp = region.historyOutputs[jLabel]
##            jTempValue = jTemp.data[-1][1] # value at last time increment
##            jTempRow.append(jTempValue)
##        jList.append(jTempRow)
##    return jList
##
##def makeHTable(table,alpha,epsilon_0,sigma_0,t,sigma,n):
##    hTable = []
##    for row in table:
##        jValues=row[4:]
##        h1Values=[]
##        hRow=[]
##        for Jpl in jValues:
##            h1 = Jpl/(alpha*epsilon_0*sigma_0*t*math.pow(sigma/sigma_0,n+1))
##            h1Values.append(h1)
##        hRow.extend(row[:4])
##        hRow.extend(h1Values)
##        hTable.append(hRow)
##    return hTable
##
##def closeResults(odb):
##    visualization.closeOdb(odb)

# From http://ginstrom.com/scribbles/2007/09/04/pretty-printing-a-table-in-python/
##def format_num(num):
##    """Format a number according to given places.
##    Adds commas, etc. Will truncate floats into ints!"""
##    try:
##        #inum = int(num)
##        return locale.format("%.*f", num, True)
##    except (ValueError, TypeError):
##        return str(num)
##
##def get_max_width(table, index):
##    """Get the maximum width of the given column index"""
##    return max([len(format_num(row[index])) for row in table])
##
##def pprint_table(out, table):
##    """Prints out a table of data, padded for alignment
##    @param out: Output stream (file-like object)
##    @param table: The table to print. A list of lists.
##    Each row must have the same number of columns. """
##    col_paddings = []
##    for i in range(len(table[0])):
##        col_paddings.append(get_max_width(table, i))
##    for row in table:
##        # left col
##        #print >> out, row[0].ljust(col_paddings[0] + 1),
##        # rest of the cols
##        #for i in range(1, len(row)):
##        for i in range(len(row)):
##            col = format_num(row[i]).rjust(col_paddings[i] + 2)
##            print >> out, col,
##        print >> out

if __name__ == "__main__":
    '''
    -------------------------------------------------------------------------
     Semi elliptic crack in a rectangular plate modeled using continuum
     elements (C3D8).
    -------------------------------------------------------------------------
    '''
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
    import testUtils
    import os, sys
    import math
    import locale
    from pprint_table import *
    from generic_crack_functions import *
    from model_geometry import modelList
    testUtils.setBackwardCompatibility()

##    modelList = [
##        {'t': 1.00, 'a': 0.20, 'c': 1.00, 'W':  4.00, 'H':  4.00}, # 1, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.20, 'c': 0.33, 'W':  1.33, 'H':  1.33}, # 2, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.20, 'c': 0.20, 'W':  0.80, 'H':  0.80}, # 3, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.50, 'c': 2.50, 'W': 10.00, 'H': 10.00}, # 4, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.50, 'c': 0.83, 'W':  3.33, 'H':  3.33}, # 5, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.50, 'c': 0.50, 'W':  2.00, 'H':  2.00}, # 6, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.80, 'c': 4.00, 'W': 16.00, 'H': 16.00}, # 7, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.80, 'c': 1.33, 'W':  5.33, 'H':  5.33}, # 8, 2012/10/22, passed
##        {'t': 1.00, 'a': 0.80, 'c': 0.80, 'W':  3.20, 'H':  3.20}, # 9, 2012/10/22, passed
##        ]

    E = 30e6   # psi
    nu = 0.3
    referenceStress = 40e3 # psi
    alpha = 0.5

    rootdir = os.getcwd()

    print "==="
    for root, subFolders, files in os.walk(rootdir):
        for folder in subFolders:
            if folder.find('McClung-')==0:
                print "%s has subdirectory %s" % (root, folder)
                for newRoot, newFolders, newFiles in os.walk(folder):                    
                    for filename in newFiles:
                        if filename.endswith('.odb'):
                            if 'plastic' in filename:
                                filePath = os.path.join(folder, filename)
                                (odbBasename, _, _) = filePath.rpartition('.odb')
                                (_, modelNumber, _) = filename.split('-', 2)
                                modelNumber=int(modelNumber)
                                (_, _, n) = odbBasename.rpartition('-')
                                n=int(n)
                                modelIndex=modelNumber-1
                                W = modelList[modelIndex]['W']
                                t = modelList[modelIndex]['t']

                                odb = openResults(odbBasename)
                                (rf1, rf2, rf3) = getReactionForces(odb)
                                jTable = getJTable(odb)
                                print "model %s, n %d" % (modelNumber, n)
                                hTable = makeHTable(table=jTable,
                                                    alpha=alpha,
                                                    epsilon_0=referenceStress/E,
                                                    sigma_0=referenceStress,
                                                    t=t,
                                                    sigma=-rf2/(W*t),
                                                    n=n)
                                closeResults(odb)
                                modelOutName="h1_%s-plastic-%d.out" % (folder, n)
                                outFile=open(modelOutName,'w')
                                pprint_table(out=outFile,table=hTable)
                                outFile.close()
