__version__ = '0.1.4'

import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
import os

os.makedirs(ro.r('Sys.getenv("R_LIBS_USER")')[0], exist_ok=True)
ro.r('.libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))')

# just make sure the env is set. R makes up the R_LIBS_USER environment variable if it doesn't exist
ro.r('Sys.setenv("R_LIBS_USER" = Sys.getenv("R_LIBS_USER")[1])')

# TODO: on Linux, library() complains about an empty directory /usr/local/lib/R/site-library’ contains no packages
# To disable warnings globally is bad. rpy2 should use installed.packages() instead of library() to check if a package is installed.
ro.r('options(warn=-1)')

utils = rpackages.importr('utils')

packnames = ('arules', 'arulesViz')
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    print("Installing missing R packages. This may take some time.")
    utils.install_packages(StrVector(names_to_install), quiet = True)


from .arules import R_arules, arules2py, parameters, Associations, ItemMatrix, Rules, Itemsets, Transactions, concat, apriori, eclat, discretizeDF
from .arulesViz import R_arulesViz, plot, inspectDT, ruleExplorer

### Enable warnings again
ro.r('options(warn=0)')