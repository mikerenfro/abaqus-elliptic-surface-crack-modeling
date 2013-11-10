from abaqusConstants import *
import math
nan = float('nan')
seeds=[
        [ # Model 1
            { # 2934 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 6286 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 27203 elements ( 40 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 148636 elements ( 80 along crack front)
                'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 2
            { # 3055 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 6630 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 22248 elements ( 40 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 57503 elements ( 80 along crack front)
                'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 3
            { # 2788 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 6894 elements ( 20 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 15630 elements ( 40 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 45968 elements ( 80 along crack front)
                'default': { 'size': 0.15, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 4
            { # 7799 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 15897 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 35405 elements ( 40 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 106943 elements ( 80 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 5
            { # 6222 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 13857 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 33600 elements ( 40 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 87324 elements ( 80 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 6
            { # 5999 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 15300 elements ( 20 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 34370 elements ( 40 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 88770 elements ( 80 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 7
            { # 14505 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 26210 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 55990 elements ( 40 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 134800 elements ( 80 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 8
            { # 5028 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 10680 elements ( 20 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 28549 elements ( 40 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 83839 elements ( 80 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
        [ # Model 9
            { # 3876 elements (10 along crack front)
                'default': { 'size': 0.5, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 10, 'constraint': FINER },
            },
            { # 12030 elements ( 20 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 20, 'constraint': FINER },
            },
            { # 31785 elements ( 40 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 40, 'constraint': FINER },
            },
            { # 74880 elements ( 80 along crack front)
                'default': { 'size': 0.25, 'deviationFactor': 0.05, 'minSizeFactor': 0.02, 'constraint': FREE },
                'ellipses': { 'number': 80, 'constraint': FINER },
            },
        ],
    ]
