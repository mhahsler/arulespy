"""The arules module provides an interface to R's arules package."""

import rpy2.robjects.packages as packages

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

R_arulesViz = packages.importr('arulesViz')

# get the generic for plot
base = packages.importr('base')
plot = base.plot
#plot.__doc__ = R_arulesViz.plot.__doc__

### FIXME: Not quite sure why I cannot set __doc__ here
inspectDT = R_arulesViz.inspectDT
#inspectDT.__doc__ = R_arulesViz.inspectDT.__doc__

def ruleExplorer(x, sidebarWidth = 2, graphHeight = '600px'):
     app = R_arulesViz.ruleExplorer(x, sidebarWidth = sidebarWidth, graphHeight = graphHeight)
     print(app)     
#ruleExplorer.__doc__ = R_arulesViz.ruleExplorer.__doc__