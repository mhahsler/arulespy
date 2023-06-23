__version__ = '0.1.3'

import rpy2.robjects as ro
import rpy2.robjects.packages as packages
import os

os.makedirs(ro.r('Sys.getenv("R_LIBS_USER")')[0], exist_ok=True)
ro.r('.libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))')

utils = packages.importr('utils')
if not ro.packages.isinstalled('arules'):
    print("Installing R package arules.")
    utils.install_packages('arules', 
                           repos='https://cloud.r-project.org/',
                           lib = ro.r('Sys.getenv("R_LIBS_USER")[1]'))
    

if not ro.packages.isinstalled('arulesViz'):
    print("Installing R package arulesViz (plus dependencies).")
    utils.install_packages('arulesViz', 
                           repos='https://cloud.r-project.org/',
                           lib = ro.r('Sys.getenv("R_LIBS_USER")[1]'))

              
from .arules import R_arules, arules2py, parameters, Associations, ItemMatrix, Rules, Itemsets, Transactions, concat, apriori, eclat, discretizeDF
from .arulesViz import R_arulesViz, plot, inspectDT, ruleExplorer