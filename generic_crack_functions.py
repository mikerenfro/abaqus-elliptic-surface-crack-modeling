from abaqus import *
from abaqusConstants import *
from caeModules import *
import testUtils
testUtils.setBackwardCompatibility()
import part, material, section, assembly, step, interaction
import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
from rectangular_topology import * ## For testing purposes only. Shouldn't have to do this.

import math

def findNear(instance,coordinates,searchTolerance=0.002,items='edges'):
    # Find edges or areas near a set of coordinates -- often (possibly
    # always) a good substitute for instance.edges.findAt() or
    # instance.areas.findAt()
    if items=='edges':
        getClosestItems = instance.edges.getClosest(coordinates=coordinates)
    elif items=='faces':
        getClosestItems = instance.faces.getClosest(coordinates=coordinates)
        #print getClosestItems
    else:
        raise NameError('unknown item type')
        
    sanitizedItems = []
    for i in range(len(getClosestItems)):
        sanitizedItems.append(getClosestItems[i][0])

    return tuple(sanitizedItems)

def createModel(modelName):
    # Create a model
    myModel = mdb.Model(name=modelName)
    return myModel

def createViewport(modelName):
    # Create a new viewport in which to display the model
    # and the results of the analysis.
    myViewport = session.Viewport(name=modelName)
    myViewport.makeCurrent()
    myViewport.maximize()
    return myViewport

def createBaseFeature(model,geometry):
    W = geometry['W']
    H = geometry['H']
    t = geometry['t']
    # Create a sketch for the base feature
    mySketch = model.Sketch(name='barProfile',
                            sheetSize=200.0)
    mySketch.sketchOptions.setValues(viewStyle=REGULAR)
    mySketch.setPrimaryObject(option=STANDALONE)

    mySketch.rectangle(point1=(0.0, 0.0),
                       point2=(W, H))
    myBlock = model.Part(name='block',
                         dimensionality=THREE_D,
                         type=DEFORMABLE_BODY)
    myBlock.BaseSolidExtrude(sketch=mySketch,
                             depth=t)
    mySketch.unsetPrimaryObject()
    del model.sketches['barProfile']
    return myBlock

def createCrackLinePartition(block,model,geometry):
    # Create a partition for the crack line
    c = geometry['c']
    W = geometry['W']
    t = geometry['t']
    a = geometry['a']
    face1 = block.faces.findAt((c, 0, t/2),)
    edge1 = block.edges.findAt((W, 0, t/2),)
    myTransform = block.MakeSketchTransform(sketchPlane=face1,
                                            sketchUpEdge=edge1,
                                            sketchPlaneSide=SIDE1,
                                            origin=(W/2, 0.0, t/2))
    mySketch = model.Sketch(name='barProfile',
                            sheetSize=26.87,
                            gridSpacing=0.67,
                            transform=myTransform)
    g = mySketch.geometry
    mySketch.setPrimaryObject(option=SUPERIMPOSE)
    block.projectReferencesOntoSketch(sketch=mySketch,
                                      filter=COPLANAR_EDGES)
    mySketch.sketchOptions.setValues(gridOrigin=(-W/2, t/2))
    mySketch.EllipseByCenterPerimeter(center=(-W/2, t/2),
                                      axisPoint1=(-W/2+c, t/2),
                                      axisPoint2=(-W/2, (t/2)-a))
    f = block.faces
    pickedFaces = f[face1.index:(face1.index+1)]
    block.PartitionFaceBySketch(sketchUpEdge=edge1,
                                faces=pickedFaces,
                                sketch=mySketch)
    mySketch.unsetPrimaryObject()
    del model.sketches['barProfile']

def createAssembly(model,block,viewport,outertube,innertube,geometry):
    W = geometry['W']
    t = geometry['t']
    
    # Create an assembly

    # Create an instance of the bar
    myAssembly = model.rootAssembly
    viewport.setValues(displayedObject=myAssembly)
    myAssembly.DatumCsysByDefault(CARTESIAN)
    myAssembly.Instance(name='myBlock-1',
                        part=block)
    myBlockInstance = myAssembly.instances['myBlock-1']

    # Create an instance of the outer partition tube
    myAssembly.Instance(name='myOuterTube-1',
                        part=outertube,
                        dependent=OFF)
    myOuterTubeInstance = myAssembly.instances['myOuterTube-1']

    # Position the outer tube around the crack tip
    myOuterTubeInstance.rotateAboutAxis(axisPoint=(0.0, 0.0, 0.0),
                                        axisDirection=(W, 0.0, 0.0),
                                        angle=90.0)
    myOuterTubeInstance.translate(vector=(0, 0.0, t))

    # Create an instance of the inner partition tube
    myAssembly.Instance(name='myInnerTube-1',
        part=innertube, dependent=OFF)
    myInnerTubeInstance = myAssembly.instances['myInnerTube-1']

    # Position the inner tube around the crack tip
    myInnerTubeInstance.rotateAboutAxis(axisPoint=(0.0, 0.0, 0.0),
                                        axisDirection=(W, 0.0, 0.0),
                                        angle=90.0)
    myInnerTubeInstance.translate(vector=(0, 0.0, t))

    # Subtract the inner and outer tubes from the block
    myAssembly.PartFromBooleanCut(name='partitionedBlock', 
        instanceToBeCut=myBlockInstance, 
        cuttingInstances=(myInnerTubeInstance, myOuterTubeInstance, ))

    # Create an instance of the partitioned block
    myPtBlock = model.parts['partitionedBlock']
    myAssembly.Instance(name='myPtBlock-1', part=myPtBlock, dependent=OFF)
    myPtBlInstance = myAssembly.instances['myPtBlock-1']

    # Create a new assembly of the parts to be suppressed
    myAssembly1 = model.rootAssembly
    myAssembly1.suppressFeatures(('myInnerTube-1',
        'myOuterTube-1', 'myBlock-1', ))

    # Create a set for the new bar instance
    cells = myPtBlock.cells
    myPtBlock.Set(cells=cells, name='All')
    return (myPtBlock, myPtBlInstance, myAssembly)

def createContourIntegral(assembly,ptblinstance,geometry,material):
    # Create the contour integral definition for the crack
    t = geometry['t']
    a = geometry['a']
    H = geometry['H']
    crackFront = crackTip = assembly.sets['crackLine']
    v1 = ptblinstance.vertices.findAt((0, 0, t-a))
    v2 = ptblinstance.vertices.findAt((0, H, t-a))
    # SINGLE_NODE for linear elastic, DUPLICATE_NODES for elastic-plastic
    if material['type']=='elastic':
        collapsedTipType = SINGLE_NODE
    elif material['type']=='deformationplasticity':
        collapsedTipType = DUPLICATE_NODES
        
    assembly.engineeringFeatures.ContourIntegral(name='Crack',
                                                 symmetric=ON,
                                                 crackFront=crackFront,
                                                 crackTip=crackTip,
                                                 extensionDirectionMethod=CRACK_NORMAL,
                                                 crackNormal=(v1, v2),
                                                 midNodePosition=0.25,
                                                 collapsedElementAtTip=collapsedTipType)        

def assignMaterialProperties(viewport,model,ptblock,material):
    # Assign material properties
    viewport.setValues(displayedObject=ptblock)

    if material['type']=='elastic':
        # Create linear elastic material
        E = material['E']
        nu = material['nu']
        model.Material(name='LinearElastic')
        model.materials['LinearElastic'].Elastic(table=((E, nu), ))
        model.HomogeneousSolidSection(name='SolidHomogeneous',
                                      material='LinearElastic',
                                      thickness=1.0)
    elif material['type']=='deformationplasticity':
        # Create deformation plasticity material
        E = material['E']
        nu = material['nu']
        sigma_0 = material['sigma_0']
        n = material['n']
        alpha = material['alpha']
        model.Material(name='DeformationPlasticity')
        model.materials['DeformationPlasticity'].DeformationPlasticity(table=((E, nu, sigma_0, n, alpha), ))
        model.HomogeneousSolidSection(name='SolidHomogeneous',
                                      material='DeformationPlasticity',
                                      thickness=1.0)
                                      
    region = ptblock.sets['All']

    # Assign the above section to the part
    ptblock.SectionAssignment(region=region,
                              sectionName='SolidHomogeneous')
    
def createLoadStep(model,material):
    # Create a step for applying a load
    if material['type']=='elastic':
        fullyPlasticSet=''
    else:
        #fullyPlasticSet='xFaceElements'
        fullyPlasticSet=''
        
    model.StaticStep(name='ApplyLoad',
                     previous='Initial',
                     description='Apply the load',
                     fullyPlastic=fullyPlasticSet,
                     initialInc=1e-5,
                     maxInc=0.1,
                     minInc=1e-5,
                     maxNumInc=100)

def createBoundaryConditions(model,assembly,material,load):
    # Create loads and boundary conditions

    # Fix the X face in the Y directions
    region = assembly.sets['xFace']
    model.DisplacementBC(name='yFixed',
                         createStepName='Initial',
                         region=region,
                         u2=0.0,
                         fixed=OFF,
                         distributionType=UNIFORM,
                         localCsys=None)

    # Fix the Y face in the X direction
    region = assembly.sets['yFace']
    model.DisplacementBC(name='xFixed',
                         createStepName='Initial',
                         region=region,
                         u1=0.0,
                         fixed=OFF,
                         distributionType=UNIFORM,
                         localCsys=None)

    # Fix a vertex in the Z direction
    region = assembly.sets['pt']
    model.DisplacementBC(name='zFixed',
                         createStepName='Initial',
                         region=region,
                         u3=0.0,
                         fixed=OFF,
                         distributionType=UNIFORM,
                         localCsys=None)

    # Apply a pressure load on the top face
    pressureMagnitude=load
        
    region = assembly.surfaces['topSurf']
    model.Pressure(name='prLoad',
                   createStepName='ApplyLoad',
                   region=region,
                   distributionType=UNIFORM,
                   magnitude=pressureMagnitude,
                   amplitude=UNSET)

def meshInstance(myPtBlInstance,myAssembly):
    partInstances = (myPtBlInstance, )
    myAssembly.generateMesh(regions=partInstances)
    # Define element set for checking fully-plastic behavior when necessary
    xFaceSet=myAssembly.sets['xFace']
    xFaceElementSet=myAssembly.Set(name='xFaceElements',elements=xFaceSet.elements)
    xFaceNodeSet=myAssembly.Set(name='xFaceNodes',elements=xFaceSet.nodes) # may not be needed
    topSurfSet=myAssembly.surfaces['topSurf']
    topSurfNodeSet=myAssembly.Set(name='topSurfNodes',nodes=topSurfSet.nodes) # may not be needed

def requestHistoryOutput(myModel,material):
    myModel.historyOutputRequests.changeKey(fromName='H-Output-1',
        toName='JInt')
    myModel.historyOutputRequests['JInt'].setValues(contourIntegral='Crack',
        numberOfContours=6)
    if (material['type']=='elastic'):
        myModel.HistoryOutputRequest(name='StrInt',
                                     createStepName='ApplyLoad',
                                     contourIntegral='Crack',
                                     numberOfContours=6,
                                     contourType=K_FACTORS)
        myModel.HistoryOutputRequest(name='TStr',
                                     createStepName='ApplyLoad',
                                     contourIntegral='Crack',
                                     numberOfContours=6,
                                     contourType=T_STRESS)

def createJob(modelName):
    myJob = mdb.Job(name=modelName,
                    model=modelName,
                    numCpus=4,
                    numDomains=4,
                    description='Contour integral analysis')

def writeInput(modelName):
    mdb.jobs[modelName].writeInput()

def submitJob(modelName):
    mdb.jobs[modelName].submit(datacheckJob=True)
    mdb.jobs[modelName].waitForCompletion()

def openResults(modelName):
    odbName = "%s.odb" % (modelName)
    odb = session.openOdb(odbName)
    return odb

def getReactionForces(odb):
    frame = odb.steps['ApplyLoad'].frames[-1]
    rfField = frame.fieldOutputs['RF']
    xFaceNodes = odb.rootAssembly.nodeSets['XFACENODES']
    rfSubField = rfField.getSubset(region=xFaceNodes)
    rf1, rf2, rf3 = 0, 0, 0
    for value in rfSubField.values:
        rf1 = rf1+value.data[0]
        rf2 = rf2+value.data[1]
        rf3 = rf3+value.data[2]
    return (rf1, rf2, rf3)

def getJTable(odb):
    region = odb.steps['ApplyLoad'].historyRegions['ElementSet  PIBATCH']
    jList = []
    nodeSetLabel = 'CRACKLINE'
    crackNodes=odb.rootAssembly.nodeSets[nodeSetLabel].nodes[0]
    for i in range(1,len(crackNodes)+1): # positions along crack
        jTempRow = []
        nodeSetLabel = 'JINT_CRACK_J_CRACKLINE-F%d__Contour_%d' % (i, 1)
        crackNode = odb.rootAssembly.nodeSets[nodeSetLabel].nodes[0][0]
        nodeLabel = crackNode.label
        nodeCoords = crackNode.coordinates.tolist()
        jTempRow.append(nodeLabel)
        for coord in nodeCoords:
            jTempRow.append(coord)
        for j in range(1,7): # contours around position
            jLabel = 'J at JINT_CRACK_CRACKLINE-F%d__Contour_%d' % (i, j)
            jTemp = region.historyOutputs[jLabel]
            jTempValue = jTemp.data[-1][1] # value at last time increment
            jTempRow.append(jTempValue)
        jList.append(jTempRow)
    return jList

def makeHTable(table,alpha,epsilon_0,sigma_0,t,sigma,n):
    hTable = []
    for row in table:
        jValues=row[4:]
        h1Values=[]
        hRow=[]
        for Jpl in jValues:
            h1 = Jpl/(alpha*epsilon_0*sigma_0*t*math.pow(sigma/sigma_0,n+1))
            h1Values.append(h1)
        hRow.extend(row[:4])
        hRow.extend(h1Values)
        hTable.append(hRow)
    return hTable

def closeResults(odb):
    visualization.closeOdb(odb)

def McClungModel(modelName,modelGeometry,modelMaterial,modelLoad,modelSeeds):
    myModel = createModel(modelName=modelName)
    myViewport = createViewport(modelName=modelName)
    myBlock = createBaseFeature(model=myModel,geometry=modelGeometry)
    createCrackLinePartition(block=myBlock,
                             model=myModel,
                             geometry=modelGeometry)
    myInnerTube, myOuterTube = createCrackRegion(model=myModel,
                                                 viewport=myViewport,
                                                 geometry=modelGeometry)
    myPtBlock, myPtBlInstance, myAssembly = createAssembly(model=myModel,
                                                           block=myBlock,
                                                           geometry=modelGeometry,
                                                           viewport=myViewport,
                                                           innertube=myInnerTube,
                                                           outertube=myOuterTube)
    assignMaterialProperties(viewport=myViewport,
                             model=myModel,
                             ptblock=myPtBlock,
                             material=modelMaterial)
    createPartition(ptblinstance=myPtBlInstance,
                    assembly=myAssembly,
                    viewport=myViewport,
                    geometry=modelGeometry)
    
    # Create interaction properties
    createSets(ptblinstance=myPtBlInstance,
               assembly=myAssembly,
               geometry=modelGeometry)
    createContourIntegral(assembly=myAssembly,
                          ptblinstance=myPtBlInstance,
                          geometry=modelGeometry,
                          material=modelMaterial)
    
    # Create a mesh 
    seedEdges(myPtBlInstance=myPtBlInstance,
              myAssembly=myAssembly,
              geometry=modelGeometry,
              seeds=modelSeeds)
    meshControls(myPtBlInstance=myPtBlInstance,
                 myAssembly=myAssembly,
                 geometry=modelGeometry)
    meshInstance(myPtBlInstance=myPtBlInstance,
                 myAssembly=myAssembly)

    # Create load step    
    createLoadStep(model=myModel,
                   material=modelMaterial)
    createBoundaryConditions(model=myModel,
                             assembly=myAssembly,
                             material=modelMaterial,
                             load=modelLoad)

    # Request history output for the crack
    requestHistoryOutput(myModel=myModel,material=modelMaterial)

    # Create the job
    createJob(modelName=modelName)

    # Make sure the assembly is regenerated
    myAssembly.regenerate()
