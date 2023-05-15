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
     
install_pkg("arules")

     
### import the R arules package
r = packages.importr('arules', lib_loc=ro.r("Sys.getenv('R_LIBS_USER')")[0])
methods = packages.importr('methods')

def parameters(x):
    """"define parameters for apriori and eclat"""
    return ro.ListVector(x)

### define mirror classes for arules S4 classes
class ItemMatrix(ro.RS4):
    """Class for arules itemMatrix object"""
    def as_df(self):
        if type(self) != ro.vectors.DataFrame:
            self  = r.DATAFRAME(self)
        with (ro.default_converter + pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(self)
        return pd_df
    
    ### convert arules associations (rules/itemsets) into a binary numpy matrix (what can be "items", "lhs", "rhs")
    def as_matrix(self):
        return np.array(ro.r('function(x) as(x, "matrix")')(self))

    ### convert arules associations (rules/itemsets) into a dictionary (what can be "items", "lhs", "rhs")
    def as_dict(self):
        l = ro.r('function(x) as(x, "list")')(self)
        l.names = [*range(0, len(l))]
        return dict(zip(l.names, map(list,list(l))))

    ### make subset work on arules S4 classes        
    def __getitem__(self, key):
        # prepare subset selection
        if isinstance(key, slice):
            key = list(range(key.stop)[key])  
        
        key = np.array(key)
        
        # Python to R indexing
        if key.dtype == 'bool':
            key = ro.BoolVector(key)
        else:
            key = key + 1
            key = ro.IntVector(key)

        # find subset S4 method
        r_subset = methods.selectMethod("[", tuple(self.rclass)[0])

        # make sure to preserve the python class
        class_type = type(self)

        ret =  r_subset(self, key)
        ret.__class__ = class_type

        return ret
    
    def __len__(self):
        return ro.r('function(x) length(x)')(self)[0]

class Rules(ItemMatrix):
    """Class for arules rules object"""
    def as_matrix(self, what = "items"):
        return ItemMatrix(ro.r('function(x) ' + what + '(x)')(self)).as_matrix()
    def as_dict(self, what = "items"):
        return ItemMatrix(ro.r('function(x) ' + what + '(x)')(self)).as_dict()

class Itemsets(ItemMatrix):
    """Class for arules itemsets object"""
    pass

class Transactions(ItemMatrix):
    """Class for arules transactions object"""
    pass


def transactions(x):
    """convert python data into an arules transactions object"""
    
    with (ro.default_converter + ro.pandas2ri.converter).context():
        x_r = ro.conversion.get_conversion().py2rpy(x)
    
    return Transactions(r.transactions(x_r))
    

def a2p(x):
    """convert arules S4 object to python object"""
    if x.rclass[0] == "rules":
        return Rules(x)
    elif x.rclass[0] == "itemsets":
        return Itemsets(x)
    elif x.rclass[0] == "transactions":
        return Transactions(x)
    elif x.rclass[0] == "itemMatrix":
        return ItemMatrix(x)
    else:
        return x


### decorators to convert R objects to python objects
def a2p_decor(function):
    def wrapper(*args, **kwargs):
        return a2p(function(*args, **kwargs))
    return wrapper

def r2df_decor(function):
    def wrapper(*args, **kwargs):
        df = function(*args, **kwargs)
        with (ro.default_converter + ro.pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(df)
        return pd_df
    return wrapper

def r2l_decor(function):
    def wrapper(*args, **kwargs):
        l = function(*args, **kwargs)
        return list(l)
    return wrapper


apriori = a2p_decor(r.apriori)
apriori.__doc__ = r.apriori.__doc__

eclat = a2p_decor(r.eclat)
eclat.__doc__ = r.eclat.__doc__

addComplement = a2p_decor(r.addComplement)
addComplement.__doc__ = r.addComplement.__doc__

sort = a2p_decor(r.sort)
sort.__doc__ = r.sort.__doc__

sample = a2p_decor(r.sample)
sample.__doc__ = r.sample.__doc__

unique = a2p_decor(r.unique)
unique.__doc__ = r.unique.__doc__

itemFrequency = r2l_decor(r.itemFrequency)
itemFrequency.__doc__ = r.itemFrequency.__doc__

items = a2p_decor(r.items)
items.__doc__ = r.items.__doc__

lhs = a2p_decor(r.lhs)
lhs.__doc__ = r.lhs.__doc__

rhs = a2p_decor(r.rhs)
rhs.__doc__ = r.rhs.__doc__

quality = r2df_decor(r.quality)
quality.__doc__ = r.quality.__doc__ 

def addQuality(x, df):
    """add quality measures to a rules or itemsets object"""
    pd_df = pd.concat([quality(x), df], axis=1)
    with (ro.default_converter + pandas2ri.converter).context():
        r_from_pd_df = ro.conversion.get_conversion().py2rpy(pd_df)

    x.slots['quality'] = r_from_pd_df

info = r2df_decor(r.info)
info.__doc__ = r.info.__doc__   

itemInfo = r2df_decor(r.itemInfo)
itemInfo.__doc__ = r.itemInfo.__doc__

interestMeasure = r2df_decor(r.interestMeasure)
interestMeasure.__doc__ = r.interestMeasure.__doc__

discretizeDF = r2df_decor(r.discretizeDF)
discretizeDF.__doc__ = r.discretizeDF.__doc__   

is_closed = r2l_decor(r.is_closed)
is_closed.__doc__ = r.is_closed.__doc__   

is_maximal = r2l_decor(r.is_maximal)
is_maximal.__doc__ = r.is_maximal.__doc__

is_generator = r2l_decor(r.is_generator)
is_generator.__doc__ = r.is_generator.__doc__

is_redundant = r2l_decor(r.is_redundant)
is_redundant.__doc__ = r.is_redundant.__doc__   

is_significant = r2l_decor(r.is_significant)
is_significant.__doc__ = r.is_significant.__doc__   

is_superset = r.is_superset

is_subset = r.is_subset

labels = r2l_decor(r.labels)
#labels.__doc__ = r.labels.__doc__   

random_transactions = a2p_decor(r.random_transactions)
random_transactions.__doc__ = r.random_transactions.__doc__

