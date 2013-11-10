if __name__ == "__main__":
    from model_geometry import *
    from generic_crack_functions import *
    from circular_seeds import *
    from circular_topology import *

    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
    import testUtils
    testUtils.setBackwardCompatibility()
    import part, material, section, assembly, step, interaction
    import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
    import inpReader
    
    import math
    import os, shutil # for creating folders and moving files
    from pprint_table import *

    modelBaseName = 'McClung'
    seedIndex = 1

    E = 30e6   # psi
    nu = 0.3
    referenceStress = 40e3 # psi
    alpha = 0.5

    runJob=False
    runElastic=False
    runPlastic=True
##    for modelIndex in range(0, len(modelList)):
##    for modelIndex in range(7, 9):
    for modelIndex in [ 6 ]:
        McClungNumber=modelIndex+1
        W = modelList[modelIndex]['W']
        H = modelList[modelIndex]['H']
        t = modelList[modelIndex]['t']
        c = modelList[modelIndex]['c']
        a = modelList[modelIndex]['a']
        # Define acceptably small outerRadius (must not risk running into block edges,
        # or cause self-intersecting sweep around crack front).
        outerRadius = min( [ 0.2, 0.5*(t-a), 0.5*a, 0.5*(W-c), 0.9*(c*c)/a, 0.9*(a*a)/c ] )
        # Define acceptable innerRadius (much smaller than outerRadius, but large enough to
        # avoid roundoff errors for sharper ellipses -- outerRadius/40 was too small for McClung 1)
        innerRadius = min( [ outerRadius/10.0, 0.005 ] )
        
        modelGeometry = { 't': t, 'W': W, 'H': H, 'c': c, 'a': a,
                          'outerRadius': outerRadius, 'innerRadius': innerRadius }

##        for seedIndex in range(0, len(seeds[modelIndex])):
##        for seedIndex in [ len(seeds[modelIndex])-1 ]:
        for seedIndex in [ 1 ]:
            caeName="%s-%d" % (modelBaseName, McClungNumber)
            if runElastic==True:
                Mdb() # uncomment to wipe out existing database and start new
                # Run elastic models
                modelMaterial = { 'type': 'elastic', 'E': E, 'nu': nu }
                modelName = "%s-%d-elastic" % (modelBaseName, McClungNumber)
                modelLoad = -10e3
                McClungModel(modelName=modelName,
                             modelGeometry=modelGeometry,
                             modelMaterial=modelMaterial,
                             modelLoad=modelLoad,
                             modelSeeds=seeds[modelIndex][seedIndex])
                elementCount=len(mdb.models[modelName].rootAssembly.allSets['myPtBlock-1.All'].elements)
                caeName = "%s-%d-%d-elements" % (modelBaseName, McClungNumber, elementCount)
                if runJob==True:
                    # Run job
                    submitJob(modelName=modelName)
                else:
                    writeInput(modelName=modelName)
                    inpName = "%s.inp" % (modelName)
                    if not os.path.exists(caeName):
                        os.mkdir(caeName)

                    shutil.copy(inpName, caeName)
                    os.remove(inpName)
                    
                mdb.saveAs(pathName=caeName+".cae")

            # Run deformation plasticity models
            if runPlastic==True:
                Mdb() # uncomment to wipe out existing database and start new
                crackArea = (math.pi/4)*a*c
                crackLength = (math.pi/4)*(3*(a+c)-math.sqrt((3*a+c)*(a+3*c)))
                areaRatio = crackArea/(W*t)
##                for hardeningExponent in [ 5, 10, 15 ]:
                for hardeningExponent in [ 5 ]:
                    modelMaterial = { 'type': 'deformationplasticity',
                                      'E': E, 'nu': nu,
                                      'sigma_0': referenceStress,
                                      'n': hardeningExponent,
                                      'alpha': alpha }
                    modelName = "%s-%d-plastic-%d" % (modelBaseName, McClungNumber, hardeningExponent)
                    elasticPlasticRatio = 100
                    modelLoad = -math.pow((elasticPlasticRatio/alpha),(1.0/(hardeningExponent-1)))*referenceStress*(1-areaRatio)
                    McClungModel(modelName=modelName,
                                 modelGeometry=modelGeometry,
                                 modelMaterial=modelMaterial,
                                 modelLoad=modelLoad,
                                 modelSeeds=seeds[modelIndex][seedIndex])
                    elementCount=len(mdb.models[modelName].rootAssembly.allSets['myPtBlock-1.All'].elements)
                    caeName = "%s-%d-%d-elements" % (modelBaseName, McClungNumber, elementCount)
                    
                    if runJob==True:
                        # Run job
                        submitJob(modelName=modelName)

                        # Get h1 values from model
                        odb = openResults(modelName)
                        (rf1, rf2, rf3) = getReactionForces(odb)
                        jTable = getJTable(odb)
                        alpha = modelMaterial['alpha']
                        sigma_0 = modelMaterial['sigma_0']
                        E = modelMaterial['E']
                        n = modelMaterial['n']
                        W = modelGeometry['W']
                        t = modelGeometry['t']
                        hTable = makeHTable(table=jTable,
                                            alpha=alpha,
                                            epsilon_0=sigma_0/E,
                                            sigma_0=sigma_0,
                                            t=t,
                                            sigma=-rf2/(W*t),
                                            n=n)
                        modelOutName="h1_%s-%d-elements.out" % (modelName, elementCount)
                        outFile=open(modelOutName,'w')
                        pprint_table(out=outFile,table=hTable)
                        outFile.close()
                    else:
                        writeInput(modelName=modelName)
                        inpName = "%s.inp" % (modelName)
                        if not os.path.exists(caeName):
                            os.mkdir(caeName)

                        shutil.copy(inpName, caeName)
                        os.remove(inpName)

                    mdb.saveAs(pathName=caeName+".cae")
