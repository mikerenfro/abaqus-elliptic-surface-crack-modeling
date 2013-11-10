from abaqus import *
from abaqusConstants import *
from caeModules import *
import testUtils
testUtils.setBackwardCompatibility()
import part, material, section, assembly, step, interaction
import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
import locale, sys # for pretty printing table

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

# From http://ginstrom.com/scribbles/2007/09/04/pretty-printing-a-table-in-python/
def format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""
    try:
        #inum = int(num)
        return locale.format("%.*f", num, True)
    except (ValueError, TypeError):
        return str(num)

def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])

def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    col_paddings = []
    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))
    for row in table:
        # left col
        #print >> out, row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        #for i in range(1, len(row)):
        for i in range(len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out

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

def createCrackRegion(model,viewport,geometry):
    c = geometry['c']
    a = geometry['a']
    W = geometry['W']
    t = geometry['t']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']
    
    # Create a shell tube for the inner partition (around the crack tip)
    # First create the sweep path
    mySketch1 = model.Sketch(name='sweepPath', sheetSize=50.0)
    g1 = mySketch1.geometry
    mySketch1.setPrimaryObject(option=STANDALONE)
    mySketch1.EllipseByCenterPerimeter(center=(0.0,     0.0),
                                       axisPoint1=(c,   0.0),
                                       axisPoint2=(0.0, -a))
    mySketch1.Line(point1=(0.0, 0.0),
                   point2=(0.0, -t))
    mySketch1.Line(point1=(0.0, 0.0),
                   point2=(W,   0.0))
    mySketch1.autoTrimCurve(curve=g1[3],
                            parameter1=0.5)
    mySketch1.delete(objectList=(g1[5], g1[7])) # remove lines
    mySketch1.unsetPrimaryObject()
    # Create a square and sweep it along the curve created above
    mySketch2 = model.Sketch(name='innerSquareProfile',
                             sheetSize=50.0,
                             transform=(0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0, 0.0, 0, -1.0, 0.0))
    g2 = mySketch2.geometry
    mySketch2.setPrimaryObject(option=SUPERIMPOSE)
    mySketch2.ObliqueConstructionLine(point1=(-2*innerRadius, 0.0),
                                      point2=(2*innerRadius, 0.0))
    mySketch2.ObliqueConstructionLine(point1=(0.0, -2*innerRadius),
                                      point2=(0.0, 2*innerRadius))
    mySketch2.Line(point1=(-innerRadius, -innerRadius),
                   point2=(-innerRadius, innerRadius))
    mySketch2.Line(point1=(-innerRadius, innerRadius),
                   point2=(innerRadius, innerRadius))
    mySketch2.Line(point1=(innerRadius, innerRadius),
                   point2=(innerRadius, -innerRadius))
    mySketch2.Line(point1=(innerRadius, -innerRadius),
                   point2=(-innerRadius, -innerRadius))
    myInnerTube = model.Part(name='innerTube',
                             dimensionality=THREE_D,
                             type=DEFORMABLE_BODY)
    myInnerTube.BaseShellSweep(sketch=mySketch2,
                               path=mySketch1)
    mySketch2.unsetPrimaryObject()
    viewport.setValues(displayedObject=myInnerTube)
    del model.sketches['innerSquareProfile']

    # Create a shell tube for the outer partition (around the inner tube)
    # For outer partition the sweep path is same as inner partition
    mySketch2 = model.Sketch(name='outerSquareProfile',
                             sheetSize=50.0,
                             transform=(0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0, 0.0, 0, -1.0, 0.0))
    g3 = mySketch2.geometry
    mySketch2.setPrimaryObject(option=SUPERIMPOSE)
    mySketch2.ObliqueConstructionLine(point1=(-outerRadius, 0.0),
                                      point2=(outerRadius, 0.0))
    mySketch2.ObliqueConstructionLine(point1=(0.0, -outerRadius),
                                      point2=(0.0, outerRadius))
    mySketch2.Line(point1=(-outerRadius, -outerRadius),
                   point2=(-outerRadius, outerRadius))
    mySketch2.Line(point1=(-outerRadius, outerRadius),
                   point2=(0, 0))
    mySketch2.Line(point1=(0, 0),
                   point2=(-outerRadius, -outerRadius))
    mySketch2.Line(point1=(-outerRadius, outerRadius),
                   point2=(outerRadius, outerRadius))
    mySketch2.Line(point1=(outerRadius, outerRadius),
                   point2=(outerRadius, -outerRadius))
    mySketch2.Line(point1=(outerRadius, -outerRadius),
                   point2=(0, 0))
    mySketch2.Line(point1=(0, 0),
                   point2=(outerRadius, outerRadius))
    mySketch2.Line(point1=(outerRadius, -outerRadius),
                   point2=(-outerRadius, -outerRadius))
    myOuterTube = model.Part(name='outerTube',
                             dimensionality=THREE_D,
                             type=DEFORMABLE_BODY)
    myOuterTube.BaseShellSweep(sketch=mySketch2,
                               path=mySketch1)
    mySketch2.unsetPrimaryObject()
    viewport.setValues(displayedObject=myOuterTube)
    del model.sketches['outerSquareProfile']
    del model.sketches['sweepPath']
    return (myInnerTube, myOuterTube)

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

def createPartition(ptblinstance,assembly,viewport,geometry):
    # Create a partition to make the entire part meshable
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    outerRadius = geometry['outerRadius']
    sPath = ptblinstance.edges.findAt((0, H/2, t))
    c1 = ptblinstance.cells
    theta = math.pi/4
    # centerline of crack
    pickedEdges = findNear(instance=ptblinstance,
                           coordinates=(
                               (c*math.cos(theta), 0, t-a*math.sin(theta)),
                               )
                           )
    assembly.PartitionCellBySweepEdge(sweepPath=sPath, cells=c1,
                                      edges=pickedEdges)
    # outer tube inside boundary
    sPath = ptblinstance.edges.findAt((0, H/2, t))
    c1 = ptblinstance.cells
    pickedEdges = findNear(instance=ptblinstance,
                           coordinates=(
                               ((c-outerRadius)*math.cos(theta), 0, t-(a-outerRadius)*math.sin(theta)),
                               )
                           )
    assembly.PartitionCellBySweepEdge(sweepPath=sPath, cells=c1,
                                      edges=pickedEdges)
    # outer tube outside boundary
    pickedEdges = findNear(instance=ptblinstance,
                           coordinates=(
                               ((c+outerRadius)*math.cos(theta), 0, t-(a+outerRadius)*math.sin(theta)),
                               )
                           )
    sPath = ptblinstance.edges.findAt((0, H/2, t))
    c1 = ptblinstance.cells
    assembly.PartitionCellBySweepEdge(sweepPath=sPath, cells=c1,
                                      edges=pickedEdges)
    viewport.setValues(displayedObject=assembly)

    # upper and lower parts of block
    c1 = ptblinstance.cells
    pickedFace = findNear(items='faces',
                          instance=ptblinstance,
                          coordinates=(
                              ((c+outerRadius/2)*math.cos(theta), outerRadius, t-(a+outerRadius/2)*math.sin(theta)),
                              )
                          )
    assembly.PartitionCellByExtendFace(cells=c1,
                                       extendFace=pickedFace[0])
                                        
def createSets(ptblinstance,assembly,geometry):
    # Create a set for the top surface
    W = geometry['W']
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']
    surf = ptblinstance.faces
    surf1 = ptblinstance.faces.findAt((W/2, H, (t-a)/2))
    surf2 = ptblinstance.faces.findAt((c/2, H, t-(a/2)))
    surfAll = (surf[surf1.index:(surf1.index+1)]
               + surf[surf2.index:(surf2.index+1)])
    assembly.Surface(side1Faces=surfAll, name='topSurf')

    # Create a set for Y face (along x=0 plane)
    # 6 faces: two large ones outside the outer tube, two small ones
    # in the outer tube, and two tiny ones in the inner tube
    faces1 = (ptblinstance.faces.findAt(((0, H/2,           (t-a)/2),),
                                        ((0, H/2,           t-(a/2)),),
                                        ((0, outerRadius/2, (t-a)-(outerRadius/2)),),
                                        ((0, outerRadius/2, (t-a)+(outerRadius/2)),),
                                        ((0, innerRadius/2, (t-a)-(innerRadius/2)),),
                                        ((0, innerRadius/2, (t-a)+(innerRadius/2)),),))
    assembly.Set(faces=faces1, name='yFace')

    # Create a set for the X face (along y=0 plane)
    # 3 faces: one large one away from the crack front, one small face of
    # the outer tube region, and one tiny face of the inner tube region
    faces1 = (ptblinstance.faces.findAt(((c+(W-c)/2,   0, t/2),),
                                        ((outerRadius, 0, (t-a)-outerRadius/2),),
                                        ((innerRadius, 0, (t-a)-innerRadius/2),)))
    xFaceSet=assembly.Set(faces=faces1, name='xFace')

    # Create a set for the vertex to be fixed in Z
    # Should this be at 0,0,0 instead? Model appeared to work as-is.
    v1 = ptblinstance.vertices.findAt(((0.,0.,t),),)
    assembly.Set(vertices=v1, name='pt')

    # Create a set for the crack line
    edges = ptblinstance.edges
    theta = math.pi/4
    edges1 = findNear(instance=ptblinstance,
                      coordinates=(
                          (c*math.cos(theta), 0, t-a*math.sin(theta)),
                          )
                      )
    edges1 = edges[edges1[0].index:(edges1[0].index+1)]
    assembly.Set(edges=edges1, name='crackLine')

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

def createJob(modelName):
    myJob = mdb.Job(name=modelName,
                    model=modelName,
                    numCpus=4,
                    numDomains=4,
                    description='Contour integral analysis')

def writeInput(modelName):
    mdb.jobs[modelName].writeInput()

def submitJob(modelName):
    mdb.jobs[modelName].submit()
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
