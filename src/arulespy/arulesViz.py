"""The arules module provides an interface to R's arules package."""

import rpy2.robjects.packages as packages

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

r = packages.importr('arulesViz')

# get the generic for plot
base = packages.importr('base')
plot = base.plot
#plot.__doc__ = r.plot.__doc__

### FIXME: Not quite sure why I cannot set __doc__ here
inspectDT = r.inspectDT
#inspectDT.__doc__ = r.inspectDT.__doc__


