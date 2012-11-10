def findNear(instance,coordinates,searchTolerance=0.002,items='edges'):
    # Find edges or areas near a set of coordinates -- often (possibly
    # always) a good substitute for instance.edges.findAt() or
    # instance.areas.findAt()
    if items=='edges':
        getClosestItems = instance.edges.getClosest(coordinates=coordinates)
    elif items=='areas':
        getClosestItems = instance.areas.getClosest(coordinates=coordinates)

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
    # Create a circle and sweep it along the curve created above
    mySketch2 = model.Sketch(name='innerCircleProfile',
                             sheetSize=50.0,
                             transform=(0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0, 0.0, 0, -1.0, 0.0))
    g2 = mySketch2.geometry
    mySketch2.setPrimaryObject(option=SUPERIMPOSE)
    mySketch2.ObliqueConstructionLine(point1=(-2*innerRadius, 0.0),
                                      point2=(2*innerRadius, 0.0))
    mySketch2.ObliqueConstructionLine(point1=(0.0, -2*innerRadius),
                                      point2=(0.0, 2*innerRadius))
    mySketch2.CircleByCenterPerimeter(center=(0.0, 0.0),
                                      point1=(innerRadius, 0.0))
    myInnerTube = model.Part(name='innerTube',
                             dimensionality=THREE_D,
                             type=DEFORMABLE_BODY)
    myInnerTube.BaseShellSweep(sketch=mySketch2,
                               path=mySketch1)
    mySketch2.unsetPrimaryObject()
    viewport.setValues(displayedObject=myInnerTube)
    del model.sketches['innerCircleProfile']

    # Create a shell tube for the outer partition (around the inner tube)
    # For outer partition the sweep path is same as inner partition
    mySketch2 = model.Sketch(name='outerCircleProfile',
                             sheetSize=50.0,
                             transform=(0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0, 0.0, 0, -1.0, 0.0))
    g3 = mySketch2.geometry
    mySketch2.setPrimaryObject(option=SUPERIMPOSE)
    mySketch2.ObliqueConstructionLine(point1=(-outerRadius, 0.0),
                                      point2=(outerRadius, 0.0))
    mySketch2.ObliqueConstructionLine(point1=(0.0, -outerRadius),
                                      point2=(0.0, outerRadius))
    mySketch2.CircleByCenterPerimeter(center=(0.0, 0.0),
                                      point1=(outerRadius, 0.0))
    myOuterTube = model.Part(name='outerTube',
                             dimensionality=THREE_D,
                             type=DEFORMABLE_BODY)
    myOuterTube.BaseShellSweep(sketch=mySketch2,
                               path=mySketch1)
    mySketch2.unsetPrimaryObject()
    viewport.setValues(displayedObject=myOuterTube)
    del model.sketches['outerCircleProfile']
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

def createPartition(ptblinstance,assembly,viewport,geometry):
    # Create a partition to make the entire part meshable
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    sPath = ptblinstance.edges.findAt((0, H/2, t))
    c1 = ptblinstance.cells
    theta = math.pi/4
    pickedEdges = findNear(instance=ptblinstance,
                           coordinates=(
                               (c*math.cos(theta), 0, t-a*math.sin(theta)),
                               )
                           )
    assembly.PartitionCellBySweepEdge(sweepPath=sPath, cells=c1,
                                      edges=pickedEdges)
    viewport.setValues(displayedObject=assembly)

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

def seedEdges(myAssembly,myPtBlInstance,geometry):
    # Seed all the edges (will generally have problems finding anything involving x=c with findAt,
    # since it looks like there's a floating-point difference in the script and what gets
    # written to the input file. Converted to findNear(), which uses getClosest().
    W = geometry['W']
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']

    theta = math.pi/4 # Used for angle calculations (e.g., midway along a curve)

    # Model 1, 22068 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 1, 50392 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 1, 135199 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 1, 274631 elements: size=0.05, deviationFactor=0.02, minSizeFactor=0.02, constraint=FREE
    # Model 2, 3134 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 2, 16308 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 2, 31768 elements: size=0.05, deviationFactor=0.02, minSizeFactor=0.02, constraint=FREE
    # Model 3, 1487 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 3, 6196 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 4, 15412 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 4, 28000 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 4, 90040 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    # Model 5, 12424 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.02, constraint=FREE
    myAssembly.seedPartInstance(regions=(myPtBlInstance,),
                                size=0.2,
                                deviationFactor=0.05,
                                minSizeFactor=0.02,
                                constraint=FREE)

    ### Critical seeds begin
    # Inner and outer crack tube curves, parallel curve on top surface
    # Five edges on y=0 plane, along curves near crack front. Additional curves just above bottom surface.
    # One extra curve on y=H, identical to crack front.
    centerX = c*math.cos(theta)
    smallInnerX = (c-innerRadius)*math.cos(theta)
    smallOuterX = (c+innerRadius)*math.cos(theta)
    largeInnerX = (c-outerRadius)*math.cos(theta)
    largeOuterX = (c+outerRadius)*math.cos(theta)
    centerZ = t-a*math.sin(theta)
    smallInnerZ = t-(a-innerRadius)*math.sin(theta)
    smallOuterZ = t-(a+innerRadius)*math.sin(theta)
    largeInnerZ = t-(a-outerRadius)*math.sin(theta)
    largeOuterZ = t-(a+outerRadius)*math.sin(theta)
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (centerX,     0,           centerZ),
                                (smallInnerX, 0,           smallInnerZ),
                                (smallOuterX, 0,           smallOuterZ),
                                (largeInnerX, 0,           largeInnerZ),
                                (largeOuterX, 0,           largeOuterZ),
                                (centerX,     innerRadius, centerZ),
                                (centerX,     outerRadius, centerZ),
                                (centerX,     H,           centerZ),
                                )
                            )
    # Model 1, 22068 elements: size=0.06, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    # Model 1, 50392 elements: size=0.06, deviationFactor=0.04, minSizeFactor=0.025, constraint=FINER
    # Model 1, 135199 elements: size=0.06, deviationFactor=0.02, minSizeFactor=0.025, constraint=FINER
    # Model 1, 274631 elements: size=0.05, deviationFactor=0.02, minSizeFactor=0.02, constraint=FREE
    # Model 2, 3134 elements: size=0.06, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    # Model 2, 16308 elements: size=0.06, deviationFactor=0.02, minSizeFactor=0.025, constraint=FINER
    # Model 2, 31768 elements: size=0.05, deviationFactor=0.02, minSizeFactor=0.025, constraint=FINER
    # Model 3, 1487 elements: size=0.06, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    # Model 3, 6196 elements: size=0.06, deviationFactor=0.02, minSizeFactor=0.025, constraint=FINER
    # Model 4, 15412 elements: size=0.2, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    # Model 4, 28000 elements: size=0.1, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    # Model 4, 90040 elements: size=0.06, deviationFactor=0.04, minSizeFactor=0.025, constraint=FINER
    # Model 5, 12424 elements: size=0.06, deviationFactor=0.05, minSizeFactor=0.025, constraint=FINER
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                              size=0.06,
                              deviationFactor=0.05,
                              minSizeFactor=0.025,
                              constraint=FINER)

    # Six radial edges of inner tube at free and symmetry surface
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (c,               innerRadius/2, t),
                                (c-innerRadius/2, 0,             t),
                                (c+innerRadius/2, 0,             t),
                                (0,               0,             (t-a)-(innerRadius/2)),
                                (0,               0,             (t-a)+(innerRadius/2)),
                                (0,               innerRadius/2, (t-a)),
                                )
                            )
    myAssembly.seedEdgeByNumber(edges=pickedEdges1,
                                number=1,
                                constraint=FIXED)
    
    # Four edges around perimeter of outer and inner tubes at free
    # and symmetry surfaces (8 edges total)
    outerX = outerRadius*math.cos(theta)
    outerY = outerRadius*math.sin(theta)
    innerX = innerRadius*math.cos(theta)
    innerY = innerRadius*math.sin(theta)
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (c+outerX, outerY, t), # cracked face
                                (c-outerX, outerY, t),
                                (c+innerX, innerY, t),
                                (c-innerX, innerY, t),
                                (0,        outerX, (t-a)+outerY), # symmetry face
                                (0,        outerX, (t-a)-outerY),
                                (0,        innerX, (t-a)+innerY),
                                (0,        innerX, (t-a)-innerY),
                                )
                            )
    # Model 1, 22068 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 1, 50392 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 1, 135199 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 1, 274631 elements: size=outerRadius/2, devationFactor=0.02, constraint=FINER
    # Model 2, 3134 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 2, 16308 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 2, 31768 elements: size=outerRadius/2, devationFactor=0.02, constraint=FINER
    # Model 3, 1487 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 3, 6196 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 4, 15412 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 4, 28000 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 4, 90040 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    # Model 5, 12424 elements: size=outerRadius/2, devationFactor=0.05, constraint=FINER
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                size=outerRadius/2,
                                deviationFactor=0.05,
                                constraint=FINER)
    
    # Six radial edges of outer tube at free and symmetry surfaces -- divide between end1Edges
    # and end2Edges depending on which end of the line has normal coordinate of 1
    # (trial and error, unless you query the endpoints of each line)
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (0,                                           0,                                         (t-a)+(innerRadius+(outerRadius-innerRadius)/2)),
                                (c-(innerRadius+(outerRadius-innerRadius)/2), 0,                                         t),
                                (c,                                           (innerRadius+(outerRadius-innerRadius)/2), t),
                                )
                            )
    pickedEdges2 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (0,                                           0,                                         (t-a)-(innerRadius+(outerRadius-innerRadius)/2)),
                                (0,                                           (innerRadius+(outerRadius-innerRadius)/2), (t-a)),
                                (c+(innerRadius+(outerRadius-innerRadius)/2), 0,                                         t),
                                )
                            )
    # Model 1, 22068 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 1, 50392 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 1, 135199 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 1, 274631 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 2, 3134 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 2, 16308 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 2, 31768 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 3, 1487 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 3, 6196 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 4, 15412 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 4, 28000 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 4, 90040 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    # Model 5, 12424 elements: minSize=innerRadius, maxSize=innerRadius*3, constraint=FREE
    myAssembly.seedEdgeByBias(end1Edges=pickedEdges1,
                              end2Edges=pickedEdges2,
                              minSize=innerRadius,
                              maxSize=innerRadius*3,
                              constraint=FREE)

    # Model 1, 22068 elements: N/A (just use default instance seeds)
    # Model 1, 50392 elements: size=0.07, constraint=FINER
    # Model 1, 135199 elements: size=0.05, constraint=FINER
    # Model 1, 274631 elements: size=0.04, constraint=FINER
    # Model 2, 3134 elements: size=0.1, constraint=FINER
    # Model 2, 16308 elements: size=0.05, constraint=FINER
    # Model 2, 31768 elements: size=0.04, constraint=FINER
    # Model 3, 1487 elements: size=0.1, constraint=FINER
    # Model 3, 6196 elements: size=0.05, constraint=FINER
    # Model 4, 15412 elements: N/A (just use default instance seeds)
    # Model 4, 28000 elements: N/A (just use default instance seeds)
    # Model 4, 90040 elements: N/A (just use default instance seeds)
    # Model 5, 12424 elements: N/A (just use default instance seeds)
    pickedEdges1 = findNear(instance=myPtBlInstance,
                        coordinates=(
                            (0, 0, t-a/2),
                            (0, H, t-a/2),
                            )
                        )
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                size=0.1,
                                constraint=FINER)
    # Model 1, 22068 elements: N/A (just use default instance seeds)
    # Model 1, 50392 elements: size=0.07, constraint=FINER
    # Model 1, 135199 elements: size=0.05, constraint=FINER
    # Model 1, 274631 elements: size=0.04, constraint=FINER
    # Model 2, 3134 elements: size=0.1, constraint=FINER
    # Model 2, 16308 elements: size=0.05, constraint=FINER
    # Model 2, 31768 elements: size=0.04, constraint=FINER
    # Model 3, 1487 elements: size=0.1, constraint=FINER
    # Model 3, 6196 elements: size=0.05, constraint=FINER
    # Model 4, 15412 elements: N/A (just use default instance seeds)
    # Model 4, 28000 elements: N/A (just use default instance seeds)
    # Model 4, 90040 elements: size=0.1, constraint=FINER
    # Model 5, 12424 elements: size=0.1, constraint=FINER
    # Horizontal edges
    pickedEdges1 = findNear(instance=myPtBlInstance,
                        coordinates=(
                            (W/2,     0, 0),
                            ((W-c)/2, 0, t),
                            (W/2,     H, 0),
                            ((W-c)/2, H, t),
                            )
                        )
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                size=0.1,
                                constraint=FINER)

    # Model 1, 22068 elements: N/A (just use default instance seeds)
    # Model 1, 50392 elements: size=0.07, constraint=FINER
    # Model 1, 135199 elements: size=0.05, constraint=FINER
    # Model 1, 274631 elements: size=0.04, constraint=FINER
    # Model 2, 3134 elements: size=0.1, constraint=FINER
    # Model 2, 16308 elements: size=0.05, constraint=FINER
    # Model 2, 31768 elements: size=0.04, constraint=FINER
    # Model 3, 1487 elements: size=0.1, constraint=FINER
    # Model 3, 6196 elements: size=0.05, constraint=FINER
    # Model 4, 15412 elements: N/A (just use default instance seeds)
    # Model 4, 28000 elements: N/A (just use default instance seeds)
    # Model 4, 90040 elements: size=0.1, constraint=FINER
    # Model 5, 12424 elements: size=0.1, constraint=FINER
    # Horizontal edges
    pickedEdges1 = findNear(instance=myPtBlInstance,
                        coordinates=(
                            (0, 0, (t-a)/2),
                            (W, 0, t/2),
                            (0, H, (t-a)/2),
                            (W, H, t/2),
                            )
                        )
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                size=0.1,
                                constraint=FINER)

    # Model 1, 22068 elements: N/A (just use default instance seeds)
    # Model 1, 50392 elements: size=0.07, constraint=FINER
    # Model 1, 135199 elements: size=0.05, constraint=FINER
    # Model 1, 274631 elements size=0.04, constraint=FINER
    # Model 2, 3134 elements: size=0.1, constraint=FINER
    # Model 2, 16308 elements: size=0.05, constraint=FINER
    # Model 2, 31768 elements: size=0.04, constraint=FINER
    # Model 3, 1487 elements: size=0.1, constraint=FINER
    # Model 3, 6196 elements: size=0.05, constraint=FINER
    # Model 4, 15412 elements: N/A (just use default instance seeds)
    # Model 4, 28000 elements: N/A (just use default instance seeds)
    # Model 4, 90040 elements: N/A (just use default instance seeds)
    # Model 5, 12424 elements: N/A (just use default instance seeds)
    # Vertical edges
    pickedEdges1 = findNear(instance=myPtBlInstance,
                        coordinates=(
                            (0, H/2, 0),
                            (W, H/2, 0),
                            (0, H/2, t),
                            (W, H/2, t),
                            (0, H/2, t-a),
                            (c, H/2, t),
                            )
                        )
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                size=0.1,
                                constraint=FINER)

def meshControls(myPtBlInstance,myAssembly,geometry):
    c = geometry['c']
    t = geometry['t']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']
    # Assign meshing controls to the respective cells

    cells = myPtBlInstance.cells.findAt(
        ((c+(innerRadius/2), 0, t),),
        ((c-(innerRadius/2), 0, t),),
        )

    myAssembly.setMeshControls(regions=cells,
                               elemShape=WEDGE,
                               technique=SWEEP)

    cells = myPtBlInstance.cells.findAt(
        ((c+(innerRadius/2)+(outerRadius-innerRadius)/2, 0, t),),
        ((c-(innerRadius/2)-(outerRadius-innerRadius)/2, 0, t),),
        )
    myAssembly.setMeshControls(regions=cells,
                               elemShape=HEX,
                               technique=STRUCTURED)

    # All the remaining cells will be meshed with hex elements using
    # structured meshing. This is also the default

    elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    cells1 = myPtBlInstance.cells
    pickedRegions =(cells1, )
    myAssembly.setElementType(regions=pickedRegions,
                              elemTypes=(elemType1, elemType2, elemType3))
        
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

def McClungModel(modelName,modelGeometry,modelMaterial,modelLoad):
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
              geometry=modelGeometry)
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
    #print "modelName = %s" % (modelName)
    createJob(modelName=modelName)

    # Make sure the assembly is regenerated
    myAssembly.regenerate()

### Global variables and main function
### TODO: examine possibility of sizing elements near crack front in terms of actual
###       length, and not divisions along a length

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
    testUtils.setBackwardCompatibility()
    import part, material, section, assembly, step, interaction
    import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
    import inpReader
    
    import math
    #from renfro_crack_functions import *
    import locale, sys # for pretty printing table
    locale.setlocale(locale.LC_NUMERIC, "")
    
    modelList = [
        {'t': 1.00, 'a': 0.20, 'c': 1.00, 'W':  4.00, 'H':  4.00}, # 1, 2012/10/22, passed
        {'t': 1.00, 'a': 0.20, 'c': 0.33, 'W':  1.33, 'H':  1.33}, # 2, 2012/10/22, passed
        {'t': 1.00, 'a': 0.20, 'c': 0.20, 'W':  0.80, 'H':  0.80}, # 3, 2012/10/22, passed
        {'t': 1.00, 'a': 0.50, 'c': 2.50, 'W': 10.00, 'H': 10.00}, # 4, 2012/10/22, passed
        {'t': 1.00, 'a': 0.50, 'c': 0.83, 'W':  3.33, 'H':  3.33}, # 5, 2012/10/22, passed
        {'t': 1.00, 'a': 0.50, 'c': 0.50, 'W':  2.00, 'H':  2.00}, # 6, 2012/10/22, passed
        {'t': 1.00, 'a': 0.80, 'c': 4.00, 'W': 16.00, 'H': 16.00}, # 7, 2012/10/22, passed
        {'t': 1.00, 'a': 0.80, 'c': 1.33, 'W':  5.33, 'H':  5.33}, # 8, 2012/10/22, passed
        {'t': 1.00, 'a': 0.80, 'c': 0.80, 'W':  3.20, 'H':  3.20}, # 9, 2012/10/22, passed
        ]
    modelBaseName = 'McClung'

    E = 30e6   # psi
    nu = 0.3
    referenceStress = 40e3 # psi
    alpha = 0.5


##    for modelIndex in range(0, len(modelList)):
    runJob=True
    for modelIndex in [ 2 ]:
        Mdb() # uncomment to wipe out existing database and start new
        McClungNumber=modelIndex+1
        caeName="%s-%d" % (modelBaseName, McClungNumber)
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

        # Run elastic model
        modelMaterial = { 'type': 'elastic', 'E': E, 'nu': nu }
        modelName = "%s-%d-elastic" % (modelBaseName, McClungNumber)
        modelLoad = -10e3
        McClungModel(modelName=modelName,
                     modelGeometry=modelGeometry,
                     modelMaterial=modelMaterial,
                     modelLoad=modelLoad)
        if runJob==True:
            # Run job
            submitJob(modelName=modelName)
            del mdb.models['Model-1']
            mdb.saveAs(pathName=caeName)

        # Run deformation plasticity models
        crackArea = (math.pi/4)*a*c
        crackLength = (math.pi/4)*(3*(a+c)-math.sqrt((3*a+c)*(a+3*c)))
        areaRatio = crackArea/(W*t)
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
                         modelLoad=modelLoad)
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
                elementCount=len(mdb.models[modelName].rootAssembly.allSets['myPtBlock-1.All'].elements)
                modelOutName="h1_%s-%d-elements.out" % (modelName, elementCount)
                outFile=open(modelOutName,'w')
                pprint_table(out=outFile,table=hTable)
                outFile.close()
                del mdb.models['Model-1']
                mdb.saveAs(pathName=caeName)
