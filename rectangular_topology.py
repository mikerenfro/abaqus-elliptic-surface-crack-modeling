from generic_crack_functions import *

def meshControls(myPtBlInstance,myAssembly,geometry):
    c = geometry['c']
    a = geometry['a']
    t = geometry['t']
    H = geometry['H']
    W = geometry['W']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']
    theta = math.pi/3
    # Assign meshing controls to the respective cells

    # Inner crack tubes
    cells = myPtBlInstance.cells.findAt(
        ((c+(innerRadius/2),                  0,                              t),),
        ((c-(innerRadius/2),                  0,                              t),),
        ((c+(innerRadius/2)*math.cos(theta), (innerRadius/2)*math.sin(theta), t),),
        ((c-(innerRadius/2)*math.cos(theta), (innerRadius/2)*math.sin(theta), t),),
        )
    myAssembly.setMeshControls(regions=cells,
                               elemShape=WEDGE,
                               technique=SWEEP)

    # Outer crack tubes
    cells = myPtBlInstance.cells.findAt(
        ((c+innerRadius+(outerRadius-innerRadius)/2, 0,                                       t),),
        ((c-innerRadius-(outerRadius-innerRadius)/2, 0,                                       t),),
        ((c+innerRadius+(outerRadius-innerRadius)/4, innerRadius+(outerRadius-innerRadius)/2, t),),
        ((c-innerRadius-(outerRadius-innerRadius)/4, innerRadius+(outerRadius-innerRadius)/2, t),),
        )
##    myAssembly.setMeshControls(regions=cells,
##                               elemShape=HEX,
##                               technique=SWEEP)
    myAssembly.setMeshControls(regions=cells,
                               elemShape=HEX,
                               technique=STRUCTURED)

    # Cells outside crack tubes
    sweptCellList = [
        {'cellCoord': (0,H/2,0), 'pathCoord': (0,H/2,0) }, # upper rectangular prisms
        {'cellCoord': (0,H/2,t), 'pathCoord': (0,H/2,t) },
        {'cellCoord': (W,H/2,t), 'pathCoord': (W,H/2,t) },
        {'cellCoord': (W,H/2,0), 'pathCoord': (W,H/2,0) }, # upper quarter-elliptical region
        {'cellCoord': (0,H/2,t-a-1.5*outerRadius), 'pathCoord': None}, # upper region between outer ellipse and rectangular prisms -- only one sweep direction possible
        {'cellCoord': (0,outerRadius/2,0), 'pathCoord': (0,outerRadius/2,0) }, # lower rectangular prisms
        {'cellCoord': (0,outerRadius/2,t), 'pathCoord': (0,outerRadius/2,t) },
        {'cellCoord': (W,outerRadius/2,t), 'pathCoord': (W,outerRadius/2,t) },
        {'cellCoord': (W,outerRadius/2,0), 'pathCoord': (W,outerRadius/2,0) }, # lower quarter-elliptical region
        {'cellCoord': (0,outerRadius/2,t-a-1.5*outerRadius), 'pathCoord': None}, # lower region between outer ellipse and rectangular prisms -- only one sweep direction possible
        {'cellCoord': (c-outerRadius/2,H,t), 'pathCoord': (c-outerRadius,H/2,t) }, # upper inner elliptical annulus
        {'cellCoord': (c+outerRadius/2,H,t), 'pathCoord': (c+outerRadius,H/2,t) }, # upper outer elliptical annulus
        ]
    for cellPath in sweptCellList:
        cellCoord = cellPath['cellCoord']
        cells = myPtBlInstance.cells.findAt(
            (cellCoord,),
            )
        myAssembly.setMeshControls(regions=cells,
                                   technique=SWEEP,
                                   algorithm=ADVANCING_FRONT)
        pathCoord = cellPath['pathCoord']
        if not pathCoord==None:
            sweepPath = myPtBlInstance.edges.findAt(
                (pathCoord,),
                )
            myAssembly.setSweepPath(region=cells[0],
                                    edge=sweepPath[0],
                                    sense=FORWARD)

    # All the remaining cells will be meshed with hex elements using
    # structured meshing. This is also the default

    elemType1 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    cells1 = myPtBlInstance.cells
    pickedRegions =(cells1, )
    myAssembly.setElementType(regions=pickedRegions,
                              elemTypes=(elemType1, elemType2, elemType3))

def seedEdges(myAssembly,myPtBlInstance,geometry,seeds):
    ### New idea (2012/12/04): bias edge seeds by crack geometry: use ratio of curvature values
    ### (a*c)/c and (c*c)/a, and set edges by a number of points. Should make it easier to handle
    ### making consistently finer meshes along the crack front (e.g., 10 elements with ratio of 10:1,
    ### 20 elements with ratio 10:1, etc.). Since curvature ratios may be excessive (125:1 for
    ### a/c=0.2, it should be maxed at 10:1.
    
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

    if not math.isnan(seeds['default']['size']):
        myAssembly.seedPartInstance(regions=(myPtBlInstance,),
                                    size=seeds['default']['size'],
                                    deviationFactor=seeds['default']['deviationFactor'],
                                    minSizeFactor=seeds['default']['minSizeFactor'],
                                    constraint=seeds['default']['constraint'])

    ### Critical seeds begin
    # Ten radial edges of inner tube at free and symmetry surface
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (c,               innerRadius/2, t),
                                (c-innerRadius/2, 0,             t),
                                (c+innerRadius/2, 0,             t),
                                (c-(innerRadius/2)*math.cos(theta), (innerRadius/2)*math.sin(theta),             t),
                                (c+(innerRadius/2)*math.cos(theta), (innerRadius/2)*math.sin(theta),             t),
                                (0,               0,             (t-a)-(innerRadius/2)),
                                (0,               0,             (t-a)+(innerRadius/2)),
                                (0,               innerRadius/2, (t-a)),
                                (0,               (innerRadius/2)*math.sin(theta), (t-a)+(innerRadius/2)*math.cos(theta)),
                                (0,               (innerRadius/2)*math.sin(theta), (t-a)-(innerRadius/2)*math.cos(theta)),
                                )
                            )
    myAssembly.seedEdgeByNumber(edges=pickedEdges1,
                                number=1,
                                constraint=FIXED)
    # Inner and outer crack tube curves, parallel curve on top surface
    # Five edges on y=0 plane, along curves near crack front. Two additional curves just above bottom surface.
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
    if 'size' in seeds['ellipses']:
        pickedEdges1 = findNear(instance=myPtBlInstance,
                                coordinates=(
                                    (centerX,     0,           centerZ), # on crack plane
                                    (smallInnerX, 0,           smallInnerZ),
                                    (smallOuterX, 0,           smallOuterZ),
                                    (largeInnerX, 0,           largeInnerZ),
                                    (largeOuterX, 0,           largeOuterZ),
                                    (smallInnerX, innerRadius, smallInnerZ), # at top of smaller square
                                    (centerX,     innerRadius, centerZ),
                                    (smallOuterX, innerRadius, smallOuterZ),
                                    (largeInnerX, outerRadius, largeInnerZ), # at top of larger square
                                    (centerX,     outerRadius, centerZ),
                                    (largeOuterX, outerRadius, largeOuterZ),
                                    (largeInnerX, H,           largeInnerZ), # at top of block
                                    (centerX,     H,           centerZ),
                                    (largeOuterX, H,           largeOuterZ),
                                    (0,           H,           t-(a/2)),     # cracked depth
                                    (c/2,         H,           t),           # cracked width
                                    (c/2,         H,           0),           # opposite of cracked width
                                    (c+(t-a),     H,           t-(c/2)),     # parallel to cracked depth
                                    )
                                )
        if not math.isnan(seeds['ellipses']['size']):
            myAssembly.seedEdgeBySize(edges=pickedEdges1,
                                      size=seeds['ellipses']['size'],
                                      deviationFactor=seeds['ellipses']['deviationFactor'],
                                      minSizeFactor=seeds['ellipses']['minSizeFactor'],
                                      constraint=seeds['ellipses']['constraint'])
    elif 'number' in seeds['ellipses']:
        pickedEdges1 = findNear(instance=myPtBlInstance,
                                coordinates=(
                                    #(c/2,         H,           0), # parallel to crack width, on top surface
                                    #(c/2,         H,           t-(a+2*outerRadius)), # intersection of depth partition and top surface
                                    (largeOuterX, H,           largeOuterZ), # projection of large tube on top surface
                                    (centerX,     H,           centerZ), # projection of crack front on top surface
                                    (smallInnerX, 0,           smallInnerZ), # inner edge of small tube on crack plane
                                    (largeInnerX, 0,           largeInnerZ), # inner edge of large tube on crack plane
                                    #(c/2,         outerRadius, t), # intersection of height partition with cracked free surface
                                    #(c/2,         0,           t), # intersection of cracked area with cracked free surface
                                    )
                                )
        pickedEdges2 = findNear(instance=myPtBlInstance,
                                coordinates=(
                                    #(c/2,         0,           0), # projection of crack width on uncracked face
                                    #(c/2,         outerRadius, 0), # intersection of height partition with uncracked face
                                    #(c/2,         0,           t-(a+2*outerRadius)), # intersection of depth partition and crack plane
                                    #(c/2,         outerRadius, t-(a+2*outerRadius)), # intersection of height and depth partitions
                                    (largeOuterX, 0,           largeOuterZ), # outer radius of large tube on crack plane
                                    (largeOuterX, outerRadius, largeOuterZ), # outer radius of large tube above crack plane
                                    (smallOuterX, 0,           smallOuterZ), # outer radius of small tube on crack plane
                                    (smallOuterX, innerRadius, smallOuterZ), # outer radius of small tube above crack plane
                                    (centerX,     0,           centerZ), # crack front
                                    (centerX,     innerRadius, centerZ), # crack front projected to small tube
                                    (centerX,     outerRadius, centerZ), # crack front projected to large tube
                                    (smallInnerX, innerRadius, smallInnerZ), # inner radius of small tube above crack plane
                                    (largeInnerX, outerRadius, largeInnerZ), # inner radius of large tube above crack plane
                                    (largeInnerX, H,           largeInnerZ), # inner radius of large tube on top surface
                                    )
                                )
##        ratio = min(seeds['ellipses']['number'], math.pow(c/a,3)) # math.pow(c/a,3) is ratio of max and min curvatures of an ellipse
##        ratio = min(10, math.pow(c/a,3))
        ratio = 1
        myAssembly.seedEdgeByBias(end1Edges=pickedEdges1,
                                  end2Edges=pickedEdges2,
                                  number=seeds['ellipses']['number'],
                                  biasMethod=SINGLE,
                                  ratio=ratio,
                                  constraint=seeds['ellipses']['constraint'])
        
##        pickedEdges1 = findNear(instance=myPtBlInstance,
##                                coordinates=(
##                                    (c+2*outerRadius, 0,           t-a/2),
##                                    (c+2*outerRadius, outerRadius, t-a/2),
##                                    (c+2*outerRadius, H,           t-a/2),
##                                    )
##                                )
##        myAssembly.seedEdgeByNumber(edges=pickedEdges1,
##                                    number=seeds['ellipses']['number'],
##                                    constraint=FREE)

    # Eight edges around perimeter of outer and inner tubes at free
    # and symmetry surfaces (16 edges total)
    outerX = outerRadius
    outerY = outerRadius
    innerX = innerRadius
    innerY = innerRadius
    pickedEdges1 = findNear(instance=myPtBlInstance,
                            coordinates=(
                                (c+outerX,   outerY/2, t), # cracked face
                                (c-outerX,   outerY/2, t),
                                (c+innerX,   innerY/2, t),
                                (c-innerX,   innerY/2, t),
                                (c+outerX/2, outerY,   t), # cracked face
                                (c-outerX/2, outerY,   t),
                                (c+innerX/2, innerY,   t),
                                (c-innerX/2, innerY,   t),
                                (0,          outerX,   (t-a)+outerY/2), # symmetry face
                                (0,          outerX,   (t-a)-outerY/2),
                                (0,          innerX,   (t-a)+innerY/2),
                                (0,          innerX,   (t-a)-innerY/2),
                                (0,          outerX/2, (t-a)+outerY), # symmetry face
                                (0,          outerX/2, (t-a)-outerY),
                                (0,          innerX/2, (t-a)+innerY),
                                (0,          innerX/2, (t-a)-innerY),
                                )
                            )
    myAssembly.seedEdgeBySize(edges=pickedEdges1,
                              size=outerRadius/3,
                              deviationFactor=0.05,
                              constraint=FINER)
    
    # Ten radial edges of outer tube at free and symmetry surfaces -- divide between end1Edges
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
    myAssembly.seedEdgeByBias(end1Edges=pickedEdges1,
                              end2Edges=pickedEdges2,
                              minSize=innerRadius,
                              maxSize=innerRadius*1, # or *2, possibly.
                              constraint=FINER)
    # Two edges along the crack depth
##    pickedEdges1 = findNear(instance=myPtBlInstance,
##                        coordinates=(
##                            (0, 0, t-a/2),
##                            (0, H, t-a/2),
##                            )
##                        )
##    if not math.isnan(seeds['crackDepth']['size']):
##        myAssembly.seedEdgeBySize(edges=pickedEdges1,
##                                    size=seeds['crackDepth']['size'],
##                                    constraint=seeds['crackDepth']['constraint'])

    # Horizontal edges along uncracked width direction
##    pickedEdges1 = findNear(instance=myPtBlInstance,
##                        coordinates=(
##                            (W/2,     0, 0),
##                            ((W-c)/2, 0, t),
##                            (W/2,     H, 0),
##                            ((W-c)/2, H, t),
##                            )
##                        )
##    if not math.isnan(seeds['uncrackedWidth']['size']):
##        myAssembly.seedEdgeBySize(edges=pickedEdges1,
##                                    size=seeds['uncrackedWidth']['size'],
##                                    constraint=seeds['uncrackedWidth']['constraint'])

    # Horizontal edges along uncracked depth direction
##    pickedEdges1 = findNear(instance=myPtBlInstance,
##                        coordinates=(
##                            (0, 0, (t-a)/2),
##                            (W, 0, t/2),
##                            (0, H, (t-a)/2),
##                            (W, H, t/2),
##                            )
##                        )
##    if not math.isnan(seeds['uncrackedDepth']['size']):
##        myAssembly.seedEdgeBySize(edges=pickedEdges1,
##                                    size=seeds['uncrackedDepth']['size'],
##                                    constraint=seeds['uncrackedDepth']['constraint'])

    # Vertical edges
##    pickedEdges1 = findNear(instance=myPtBlInstance,
##                        coordinates=(
##                            (0, H/2, 0),
##                            (W, H/2, 0),
##                            (0, H/2, t),
##                            (W, H/2, t),
##                            (0, H/2, t-a),
##                            (0, H/2, t-a+outerRadius),
##                            (0, H/2, t-a-outerRadius),
##                            (c, H/2, t),
##                            (c-outerRadius, H/2, t),
##                            (c+outerRadius, H/2, t),
##                            )
##                        )
##    if 'size' in seeds['height']:
##        if not math.isnan(seeds['height']['size']):
##            myAssembly.seedEdgeBySize(edges=pickedEdges1,
##                                      size=seeds['height']['size'],
##                                      constraint=seeds['height']['constraint'])
##    elif 'number' in seeds['height']:
##
##        myAssembly.seedEdgeByNumber(edges=pickedEdges1,
##                                    number=seeds['height']['number'],
##                                    constraint=seeds['height']['constraint'])

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
    mySketch2 = model.Sketch(name='innerProfile',
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
    del model.sketches['innerProfile']

    # Create a shell tube for the outer partition (around the inner tube)
    # For outer partition the sweep path is same as inner partition
    mySketch2 = model.Sketch(name='outerProfile',
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
    del model.sketches['outerProfile']
    del model.sketches['sweepPath']
    return (myInnerTube, myOuterTube)

def createPartition(ptblinstance,assembly,viewport,geometry):
    # Create a partition to make the entire part meshable
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    W = geometry['W']
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

    # horizontal split near crack width
    offset = min([c+(t-a), c+2*outerRadius])
    datum = assembly.DatumPlaneByPrincipalPlane(offset=offset, principalPlane=YZPLANE)
    datumId = datum.id
    c1 = ptblinstance.cells
    assembly.PartitionCellByDatumPlane(cells=c1,datumPlane=assembly.datums[datum.id])

    # horizontal split near crack depth (unless crack is very deep)
    offset = t-(a+2*outerRadius)
    if offset>(0.2*t):
        datum = assembly.DatumPlaneByPrincipalPlane(offset=offset, principalPlane=XYPLANE)
        datumId = datum.id
        c1 = ptblinstance.cells
        assembly.PartitionCellByDatumPlane(cells=c1,datumPlane=assembly.datums[datum.id])

def createSets(ptblinstance,assembly,geometry):
    # Create a set for the top surface
    W = geometry['W']
    H = geometry['H']
    t = geometry['t']
    a = geometry['a']
    c = geometry['c']
    innerRadius = geometry['innerRadius']
    outerRadius = geometry['outerRadius']
    theta = math.pi/4
    surf = ptblinstance.faces
    surf1 = ptblinstance.faces.findAt((W/2, H, (t-a)/2))
    surf2 = ptblinstance.faces.findAt((c/2, H, t-(a/2)))
    surf3 = ptblinstance.faces.findAt(((c-innerRadius/2)*math.cos(theta), H, t-(a-innerRadius/2)*math.sin(theta)))
    surf4 = ptblinstance.faces.findAt(((c+innerRadius/2)*math.cos(theta), H, t-(a+innerRadius/2)*math.sin(theta)))
    surfAll = (surf[surf1.index:(surf1.index+1)]
               + surf[surf2.index:(surf2.index+1)]
               + surf[surf3.index:(surf3.index+1)]
               + surf[surf4.index:(surf4.index+1)])
    assembly.Surface(side1Faces=surfAll, name='topSurf')

    # Create a set for Y face (along x=0 plane)
    # 14 faces: four tall ones above the outer tube, four small ones
    # in the outer tube, four tiny ones in the inner tube, and two
    # wide ones on either side of the outer tube
    faces1 = (ptblinstance.faces.findAt(((0, H/2,           (t-a)/2),), # tall faces
                                        ((0, H/2,           t-(a/2)),),
                                        ((0, H/2,           (t-a)+(outerRadius/2)),),
                                        ((0, H/2,           (t-a)-(outerRadius/2)),),
                                        ((0, outerRadius/2, (t-a-outerRadius)/2),), # wide faces
                                        ((0, outerRadius/2, (t-(a-outerRadius)/2)),),
                                        ((0, outerRadius/2, (t-a)-(outerRadius/4)),), # small faces
                                        ((0, outerRadius/2, (t-a)+(outerRadius/4)),),
                                        ((0, outerRadius/4, (t-a)-(outerRadius/2)),),
                                        ((0, outerRadius/4, (t-a)+(outerRadius/2)),),
                                        ((0, innerRadius/2, (t-a)+(innerRadius/4)),), # tiny faces
                                        ((0, innerRadius/2, (t-a)-(innerRadius/4)),),
                                        ((0, innerRadius/4, (t-a)+(innerRadius/2)),),
                                        ((0, innerRadius/4, (t-a)-(innerRadius/2)),),))
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
