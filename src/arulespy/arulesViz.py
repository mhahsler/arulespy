"""The arules module provides an interface to R's arules package."""

import pandas as pd
import numpy as np

import rpy2.robjects as ro
import rpy2.robjects.packages as packages
from rpy2.robjects import pandas2ri

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

# install arules if necessary. Note: the system path is probably not writable for the user.
install_pkg = ro.r('''
    function(pkg, repos = "https://cloud.r-project.org/", lib = Sys.getenv("R_LIBS_USER")) {
        if (!requireNamespace(pkg, quietly = TRUE)) {
            cat("Installing R package arules.")
            # create the personal library directory if it doesn't exist
            dir.create(lib,  showWarnings = FALSE, recursive = TRUE)
    
            install.packages(pkg, repos = repos, lib = lib)
        }
    }
''')
     
install_pkg("arulesViz")

### import the R arules package
r = packages.importr('arulesViz', lib_loc=ro.r("Sys.getenv('R_LIBS_USER')")[0])

# get the generic for plot
base = packages.importr('base')
plot = base.plot
#plot.__doc__ = r.plot.__doc__

inspectDT = r.inspectDT
#inspectDT.__doc__ = r.inspectDT.__doc__


