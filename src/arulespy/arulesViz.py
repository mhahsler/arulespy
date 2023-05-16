"""The arules module provides an interface to R's arules package."""

import pandas as pd
import numpy as np

import rpy2.robjects as ro
import rpy2.robjects.packages as packages
from rpy2.robjects import pandas2ri

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()




# install arules if necessary. Note: the system path is probably not writable for the user.
ro.r('dir.create(Sys.getenv("R_LIBS_USER")[1], showWarnings = FALSE, recursive = TRUE)')

utils = packages.importr('utils')
if not ro.packages.isinstalled('arulesViz'):
    print("Installing R package arulesViz.")
    utils.install_packages('arulesViz', 
                           repos='https://cloud.r-project.org/',
                           lib = ro.r('Sys.getenv("R_LIBS_USER")[1]'))

r = packages.importr('arulesViz')

# get the generic for plot
base = packages.importr('base')
plot = base.plot
#plot.__doc__ = r.plot.__doc__

inspectDT = r.inspectDT
#inspectDT.__doc__ = r.inspectDT.__doc__


