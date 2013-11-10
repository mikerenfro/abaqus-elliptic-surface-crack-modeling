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
    from renfro_crack_functions import *
    #from mcclung_models_seeds import *
    import locale, sys # for pretty printing table
    locale.setlocale(locale.LC_NUMERIC, "")
    import os, shutil # for creating folders and moving files

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

    nan = float('nan')
    seeds=[
        [ # Model 1
    ##        { # 8056 elements -- failed
    ##          'default': { 'size': 0.14, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
    ##          'ellipses': { 'size': 0.14, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
    ##          'crackDepth': {'size': nan},
    ##          'uncrackedWidth': {'size': nan},
    ##          'uncrackedDepth': {'size': nan},
    ##          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
    ##        }, 
    ##        { # 14640 elements -- failed
    ##          'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
    ##          'ellipses': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
    ##          'crackDepth': {'size': nan},
    ##          'uncrackedWidth': {'size': nan},
    ##          'uncrackedDepth': {'size': nan},
    ##          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
    ##        }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': { 'size': nan },
              'uncrackedWidth': { 'size': nan },
              'uncrackedDepth': { 'size': nan },
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.14, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': { 'size': nan },
              'uncrackedWidth': { 'size': nan },
              'uncrackedDepth': { 'size': nan },
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan },
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan },
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 21972 elements
              'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
    ##        { # 86465 elements -- failed
    ##          'default': { 'size': 0.05, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
    ##          'ellipses': { 'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
    ##          'crackDepth': {'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
    ##          'uncrackedWidth': {'size': nan},
    ##          'uncrackedDepth': {'size': nan},
    ##          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
    ##        }, 
         ],
        [ # Model 2
            { # 1707 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 4020 elements
              'default': { 'size': 0.08, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.08, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 8796 elements
              'default': { 'size': 0.08, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 14808 elements
              'default': { 'size': 0.07, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.02, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 3
            { # 1188 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 3150 elements
              'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 5880 elements
              'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.03, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 9000 elements
              'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.02, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 4
            { # X elements -- failed
              'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
##              'ellipses': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'ellipses': { 'number': 40, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': { 'number': 20, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
##              'ellipses': { 'size': 0.20, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'ellipses': { 'number': 20, 'constraint': FIXED },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
##              'ellipses': { 'size': 0.14, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'ellipses': { 'number': 20, 'constraint': FIXED },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 43000 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.10, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # X elements -- failed
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
##              'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'ellipses': { 'number': 20, 'constraint': FIXED },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            },
            { # X elements -- failed
              'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
##              'ellipses': { 'size': 0.05, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'ellipses': { 'number': 20, 'constraint': FIXED },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 

         ],
         [ # Model 5
            { # 5513 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 9649 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 25046 elements
              'default': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 6
            { # 3717 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 6226 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 12452 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 7
            { # 48624 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 75528 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.14, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 118224 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 8
            { # 7526 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 15452 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 35912 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.05, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
         [ # Model 9
            { # 4044 elements
              'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 8141 elements
              'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.1, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
            { # 11721 elements
              'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
              'ellipses': { 'size': 0.08, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
              'crackDepth': {'size': nan},
              'uncrackedWidth': {'size': nan},
              'uncrackedDepth': {'size': nan},
              'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
            }, 
         ],
        ]

    
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
    for modelIndex in [ 3 ]:
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
        for seedIndex in [ 0 ]:
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
