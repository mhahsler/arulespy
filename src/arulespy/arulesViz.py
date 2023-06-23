"""The arules module provides an interface to R's arules package."""

import rpy2.robjects.packages as packages
from arulespy.arules import arules2py_decor

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

R_arulesViz = packages.importr('arulesViz')

# get the generic for plot
base = packages.importr('base')
plot = arules2py_decor(base.plot)
# we use the decorator so we can set docstrings, otherwise it would only show
# the docstring for the plot generic.
plot.__doc__ = """Visualize Association Rules and Itemsets

plot(x, method = NULL, measure = "support", shading = "lift", limit = NULL, 
    interactive = NULL, engine = "default", data = NULL, control = NULL, ...)
    

For details see https://mhahsler.r-universe.dev/arulesViz/doc/manual.html#plot
"""

inspectDT = R_arulesViz.inspectDT
# gets doc automatically inspectDT.__doc__ = R_arulesViz.inspectDT.__doc__

def ruleExplorer(x, sidebarWidth = 2, graphHeight = '600px'):
     app = R_arulesViz.ruleExplorer(x, sidebarWidth = sidebarWidth, graphHeight = graphHeight)
     print(app)     
ruleExplorer.__doc__ = R_arulesViz.ruleExplorer.__doc__