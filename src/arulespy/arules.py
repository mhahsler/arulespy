"""The arules module provides an interface to R's arules package."""

import pandas as pd
import numpy as np

import rpy2.robjects as ro
import rpy2.robjects.packages as packages
from rpy2.robjects import pandas2ri

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

# install arules if necessary. Note: the system path is probably not writable for the user.
# we try to create the directory so install.packages does not ask


### import the R arules package
R = packages.importr('arules')
methods = packages.importr('methods')
base = packages.importr('base')

### arules interface code 

def parameters(x):
    """define parameters for apriori and eclat"""

    return ro.ListVector(x)

def set(x):
    """define a set of items"""

    return ro.StrVector(x)

class ItemMatrix(ro.RS4):
    """Class for arules itemMatrix object"""
    
    def as_df(self):
        """convert to pandas dataframe"""
        if type(self) != ro.vectors.DataFrame:
            self  = R.DATAFRAME(self)
        with (ro.default_converter + pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(self)
        return pd_df
    
    def as_matrix(self):
        """convert to numpy matrix
        
        Args:
            what: can be "items", "lhs", "rhs"
        """
        return np.array(ro.r('function(x) as(x, "matrix")')(self))

    ### convert arules associations (rules/itemsets) into a dictionary (what can be "items", "lhs", "rhs")
    def as_dict(self):
        """convert to dictionary
        
        Args:
            what can be "items", "lhs", "rhs"
        """

        l = ro.r('function(x) as(x, "list")')(self)
        l.names = [*range(0, len(l))]
        return dict(zip(l.names, map(list,list(l))))
      
    def as_list(self):
        """convert to list"""
        return list(self.as_dict().values())  
    
    @staticmethod
    def from_list(items, itemLabels):
        items = [ro.StrVector(x) for x in items]
        return ItemMatrix(R.encode(items, itemLabels))

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
        """return number of elements in the set"""

        return ro.r('function(x) length(x)')(self)[0]
    
    def sort(self, by = "lift", decreasing = True):
        """sort
        
        Args:
            by: the interest measure from the quality slot
            decreasing: sort decreasingly?
        """
        if decreasing:
            decreasing = "TRUE"
        else:
            decreasing = "FALSE"

        return a2p(ro.r('function(x) sort(x, by = "' + by + '", decreasing = ' + decreasing + ')')(self))

    def unique(self):
        """return unique elements"""
        return a2p(ro.r('function(x) unique(x)')(self))
    
    def sample(self, size = 1):
        """sample from the set
        
        Args:
            size: number of samples
        """
        return a2p(ro.r('function(x) sample(x, size = ' + str(size) + ')')(self))
    
    def items(self):
        """return items"""
        return a2p(ro.r('function(x) items(x)')(self))
    
    def itemFrequency(self, type = "absolute"):
        """return item frequency
        
        Args:
            type: "absolute" or "relative"
        """
        return np.array(a2p(ro.r('function(x, type) itemFrequency(x, type)')(self, type)))
    
    def itemInfo(self):
        """return item info as dataframe"""
        return r2df(ro.r('function(x) itemInfo(x)')(self))
    
    def labels(self):
        """returns a list of labels for the sets"""
        return r2list(ro.r('function(x) labels(x)')(self))
    
    def is_subset(self, x, sparse = False):
        """check if x is a subset of self
        
        Args:
            x: the other set
            sparse: return sparse matrix representation?
        """    
        if sparse:
            sparse = "TRUE"
        else:
            sparse = "FALSE"
        return ro.r('function(x, y, sparse) is.subset(x, y, sparse)')(self, x, sparse)
    
    def is_superset(self, x, sparse = False):
        """check if x is a superset of self
        
        Args:
            x: the other set
            sparse: return sparse matrix representation?
        """
        if sparse:
            sparse = "TRUE"
        else:
            sparse = "FALSE"
        return ro.r('function(x, y, sparse) is.superset(x, y, sparse)')(self, x, sparse)
            

class Associations(ItemMatrix):
    """Superclass for arules associations (rules/itemsets)"""

    def quality(self):
        """return quality measures as dataframe"""
        return r2df(ro.r('function(x) quality(x)')(self))

    def is_closed(self):
        """return closedness as boolean vector"""
        return r2list(ro.r('function(x) is.closed(x)')(self))
    
    def is_maximal(self):
        """return maximality as boolean vector"""
        return r2list(ro.r('function(x) is.maximal(x)')(self))
    
    def is_generator(self):
        """return generator as boolean vector"""
        return r2list(ro.r('function(x) is.generator(x)')(self))
    
    def is_redundant(self):
        """return redundent rules as boolean vector"""
        return r2list(ro.r('function(x) is.redundant(x)')(self))
    
    def is_significant(self):
        """return significant rules as boolean vector"""
        return r2list(ro.r('function(x) is.significant(x)')(self))
    
    def interestMeasure(self, measure = ["support", "confidence", "lift"], 
                        transactions = None):
        """calculate additional interest measures
        
        Args:
            measure: a list of interest measures (see: https://mhahsler.github.io/arules/docs/measures)
            transactions: the transactions to use (optional)
        """
        if transactions == None:
            transactions = ro.r('NULL')
        return r2df(ro.r('function(x, measure, transactions) interestMeasure(x, measure, transactions)')
                    (self, measure, transactions), column_names=measure)

    def addQuality(self, df):
        """add quality measures to the associations.
        
        Args:
            df: a pandas dataframe with the same number of rows as the associations
        """
        pd_df = pd.concat([self.quality(), df], axis=1)
        with (ro.default_converter + pandas2ri.converter).context():
            r_from_pd_df = ro.conversion.get_conversion().py2rpy(pd_df)

        self.slots['quality'] = r_from_pd_df

class Rules(Associations):
    """Class for arules rules object"""
    
    @staticmethod
    def new(lhs, rhs, quality = None):
        
        if quality == None:
            return Rules(methods.new("rules", lhs, rhs))
        else:
            return Rules(methods.new("rules", lhs, rhs, quality))
    
    def lhs(self):
        """return lhs as an itemMatrix"""
        return ItemMatrix(ro.r('function(x) lhs(x)')(self))
    
    def rhs(self):
        """return rhs as an itemMatrix"""
        return ItemMatrix(ro.r('function(x) rhs(x)')(self))

    def as_matrix(self, what = "items"):
        """return lhs/rhs as numpy matrix
        
        Args:
            what: "lhs", "rhs", or "items"
        """
        return ItemMatrix(ro.r('function(x) ' + what + '(x)')(self)).as_matrix()
    
    def as_dict(self, what = "items"):
        """return lhs/rhs as a dictionary
        
        Args:
            what: "lhs", "rhs", or "items"
        """
        return ItemMatrix(ro.r('function(x) ' + what + '(x)')(self)).as_dict()
    


class Itemsets(Associations):
    """Class for arules itemsets object"""
    
    @staticmethod
    def new(items, quality = None):

        if quality == None:
             return a2p(methods.new("itemsets", items))
        else:
            return a2p(methods.new("itemsets", items, quality))

class Transactions(ItemMatrix):
    """Class for arules transactions object"""
    
    @staticmethod
    def new(items):
        return Transactions(methods.new("transactions", items))
    
    def from_df(x, itemLabels = None):
        """convert pandas dataframe into an arules transactions object"""
    
        with (ro.default_converter + ro.pandas2ri.converter).context():
            x_r = ro.conversion.get_conversion().py2rpy(x)
    
        if itemLabels == None:
            return Transactions(R.transactions(x_r))
        else:
            return Transactions(R.transactions(x_r, itemLabels))

### Conversion functions

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

def r2df(x, column_names = None):
    """convert R dataframe to pandas dataframe"""

    with (ro.default_converter + ro.pandas2ri.converter).context():
        pd_df = ro.conversion.get_conversion().rpy2py(x)

    if type(pd_df) != pd.core.frame.DataFrame:
        pd_df = pd.DataFrame(pd_df, columns= column_names)   ### set column name!
    return pd_df   

def r2list(x):  
    return list(x) 

def r2df_decor(function):
    """decorator to convert R dataframes to pandas dataframes"""

    def wrapper(*args, **kwargs):
        return r2df(function(*args, **kwargs))
    return wrapper

def r2list_decor(function):
    """decorator to convert R lists to Python lists"""

    def wrapper(*args, **kwargs):
        return r2list(function(*args, **kwargs))
    return wrapper

def a2p_decor(function):
    """decorator to convert arules S4 objects to python objects"""

    def wrapper(*args, **kwargs):
        return a2p(function(*args, **kwargs))
    return wrapper


apriori = a2p_decor(R.apriori)
apriori.__doc__ = R.apriori.__doc__

eclat = a2p_decor(R.eclat)
eclat.__doc__ = R.eclat.__doc__


### static functions
encode = a2p_decor(R.encode)
encode.__doc__ = R.encode.__doc__

def concat(list):
    conc = methods.selectMethod("c", tuple(list[0].rclass)[0])
    return a2p(conc(*list))

discretizeDF = r2df_decor(R.discretizeDF)
discretizeDF.__doc__ = R.discretizeDF.__doc__   

random_transactions = a2p_decor(R.random_transactions)
random_transactions.__doc__ = R.random_transactions.__doc__

