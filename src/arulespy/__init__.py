__version__ = '0.1.0'

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


from .arules import parameters, set, Associations, ItemMatrix, Rules, Itemsets, Transactions, R, a2p, encode, concat, apriori, eclat, discretizeDF, random_transactions                 
from .arulesViz import plot, inspectDT