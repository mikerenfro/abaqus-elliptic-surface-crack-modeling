from abaqusConstants import *

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
        { # 14784 elements -- failed
          'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
          'ellipses': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
          'crackDepth': {'size': nan},
          'uncrackedWidth': {'size': nan},
          'uncrackedDepth': {'size': nan},
          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
        }, 
        { # 20535 elements -- failed
          'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
          'ellipses': { 'size': 0.20, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FINER },
          'crackDepth': {'size': nan},
          'uncrackedWidth': {'size': nan},
          'uncrackedDepth': {'size': nan},
          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
        }, 
        { # 24458 elements -- failed
          'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
          'ellipses': { 'size': 0.14, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
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
        { # 69096 elements -- failed
          'default': { 'size': 0.2, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
          'ellipses': { 'size': 0.05, 'deviationFactor': 0.02, 'minSizeFactor': 0.025, 'constraint': FINER },
          'crackDepth': {'size': nan},
          'uncrackedWidth': {'size': nan},
          'uncrackedDepth': {'size': nan},
          'height': {'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.025, 'constraint': FREE }
        },
        { # 96753 elements -- failed
          'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
          'ellipses': { 'size': 0.05, 'deviationFactor': 0.03, 'minSizeFactor': 0.025, 'constraint': FINER },
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

