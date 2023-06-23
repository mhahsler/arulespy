"""The arules module provides an interface to R's arules package."""

import pandas as pd
import numpy as np
from scipy.sparse import csc_matrix

import rpy2.robjects as ro
import rpy2.robjects.packages as packages
from rpy2.robjects import pandas2ri

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

# install arules if necessary. Note: the system path is probably not writable for the user.
# we try to create the directory so install.packages does not ask

### import the R arules package
R_arules = packages.importr('arules')
methods = packages.importr('methods')
base = packages.importr('base')

### Sparse matrix helper
def ngC_to_csc_matrix(m):
    """convert a ngCMatrix to a scipy csc_matrix"""
    indices = np.array(m.slots['i'])
    indptr  = np.array(m.slots['p'])
    ## all ones for ngCMatrix
    data = np.array([1]*len(indices))
    return csc_matrix((data, indices, indptr), tuple(m.slots['Dim']))    

### Conversion functions
def arules2py(x):
    """convert arules S4 object to python object
    
    Conversion rules:
    - rules: Python Rules object
    - itemsets: Python Itemsets object
    - transactions: Python Transactions object
    - itemMatrix: Python ItemMatrix object
    - data.frame: pandas dataframe
    - character: string list
    - integer: int list
    - numeric: float list
    - logical: bool list
    - matrix: numpy array
    """

    if x.rclass[0] == "rules":
        return Rules(x)
    elif x.rclass[0] == "itemsets":
        return Itemsets(x)
    elif x.rclass[0] == "transactions":
        return Transactions(x)
    elif x.rclass[0] == "itemMatrix":
        return ItemMatrix(x)
    elif x.rclass[0] == "data.frame":
        colnames = list(x.colnames)
        with (ro.default_converter + ro.pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(x)

        if type(pd_df) != pd.core.frame.DataFrame:
            pd_df = pd.DataFrame(pd_df, columns= colnames)   ### set column name!
        return pd_df   
    elif x.rclass[0] in ["character", "integer", "numeric", "logical"]:
        return list(x)
    elif x.rclass[0] == "matrix":
        return np.array(x)

    else:
        return x

def arules2py_decor(function):
    """decorator to convert arules S4 objects to python objects"""
    def wrapper(*args, **kwargs):
        return arules2py(function(*args, **kwargs))
    return wrapper


### arules interface code 
def parameters(x):
    """define parameters for apriori and eclat"""
    return ro.ListVector(x)


class ItemMatrix(ro.RS4):
    """Class for arules itemMatrix object"""
    
    @staticmethod
    def from_list(items, itemLabels):
        """convert list of lists into an arules itemMatrix object"""
        items = [ro.StrVector(x) for x in items]
        return ItemMatrix(R_arules.encode(items, itemLabels))

    def as_df(self):
        """convert to pandas dataframe"""
        if type(self) != ro.vectors.DataFrame:
            self  = R_arules.DATAFRAME(self)
        with (ro.default_converter + pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(self)
        return pd_df
    
    def as_matrix(self):
        """convert to numpy matrix"""
        return np.array(ro.r('function(x) as(x, "matrix")')(self))

    def as_csc_matrix(self):
        """convert to scipy sparse matrix"""
        return ngC_to_csc_matrix(self.slots['data'])

    def as_dict(self):
        """convert to dictionary"""
        l = ro.r('function(x) as(x, "list")')(self)
        l.names = [*range(0, len(l))]
        return dict(zip(l.names, map(list,list(l))))
      
    def as_list(self):
        """convert to list"""
        return list(self.as_dict().values())  
    
    def as_int_list(self):
        """convert to int list"""
        l = ro.r('function(x) LIST(x, decode = FALSE)')(self)
        return [list(x) for x in l]

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
        decreasing  = ro.vectors.BoolVector([decreasing])
        return arules2py(ro.r('function(x, by, decreasing) sort(x, by = by, decreasing = decreasing)')(self, by, decreasing))

    def unique(self):
        """return unique elements"""
        return arules2py(ro.r('function(x) unique(x)')(self))
    
    def sample(self, size = 1, replace = False):
        """sample from the set
        
        Args:
            size: number of samples
        """
        replace = ro.vectors.BoolVector([replace])
        return arules2py(ro.r('function(x, size, replace) sample(x, size = size, replace = replace)')(self, size, replace))
    
    def items(self):
        """return items"""
        return ItemMatrix(ro.r('function(x) items(x)')(self))
    
    def itemFrequency(self, type = "absolute"):
        """return item frequency
        
        Args:
            type: "absolute" or "relative"
        """
        return arules2py(ro.r('function(x, type) itemFrequency(x, type)')(self, type))
    
    def itemInfo(self):
        """return item info as dataframe"""
        return arules2py(ro.r('function(x) itemInfo(x)')(self))
    
    def labels(self):
        """returns a list of labels for the sets"""
        return arules2py(ro.r('function(x) labels(x)')(self))
    
    def itemLabels(self):
        """returns a list of labels for the sets"""
        return arules2py(ro.r('function(x) itemLabels(x)')(self))
    
    def is_subset(self, x, proper = False, sparse = True):
        """check if x is a subset of self
        
        Args:
            x: the other set
            proper: proper subset?
            sparse: return sparse matrix representation as a scipy.sparse.csc_matrix?
        """    
        m = ro.r('function(x, y, proper, sparse) is.subset(x, y, proper, sparse)')(self, x, 
                        ro.vectors.BoolVector([proper]), ro.vectors.BoolVector([sparse]))

        if sparse:
            return ngC_to_csc_matrix(m)
        else:
            return np.array(m)  
    
    def is_superset(self, x, proper = False, sparse = True):
        """check if x is a superset of self
        
        Args:
            x: the other set
            proper: proper superset?
            sparse: return sparse matrix representation as a scipy.sparse.csc_matrix?
        """
        m = ro.r('function(x, y, proper, sparse) is.superset(x, y, proper, sparse)')(self, x, 
                        ro.vectors.BoolVector([proper]), ro.vectors.BoolVector([sparse]))

        if sparse:
            return ngC_to_csc_matrix(m)
        else:
            return np.array(m)     

class Associations(ItemMatrix):
    """Superclass for arules associations (rules/itemsets)"""

    def quality(self):
        """return quality measures as dataframe"""
        return arules2py(ro.r('function(x) quality(x)')(self))

    def is_closed(self):
        """return closedness as boolean vector"""
        return arules2py(ro.r('function(x) is.closed(x)')(self))
    
    def is_maximal(self):
        """return maximality as boolean vector"""
        return arules2py(ro.r('function(x) is.maximal(x)')(self))
    
    def is_generator(self):
        """return generator as boolean vector"""
        return arules2py(ro.r('function(x) is.generator(x)')(self))
    
    def is_redundant(self):
        """return redundent rules as boolean vector"""
        return arules2py(ro.r('function(x) is.redundant(x)')(self))
    
    def is_significant(self):
        """return significant rules as boolean vector"""
        return arules2py(ro.r('function(x) is.significant(x)')(self))
    
    def interestMeasure(self, measure = ["support", "confidence", "lift"], 
                        transactions = None):
        """calculate additional interest measures
        
        Args:
            measure: a list of interest measures (see: https://mhahsler.github.io/arules/docs/measures)
            transactions: the transactions to use (optional)
        """
        if transactions == None:
            transactions = ro.r('NULL')
        return arules2py(ro.r('function(x, measure, transactions) interestMeasure(x, measure, transactions)')
                    (self, measure, transactions))

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
    


class Itemsets(Associations):
    """Class for arules itemsets object"""
    
    @staticmethod
    def new(items, quality = None):

        if quality == None:
            return arules2py(methods.new("itemsets", items))
        else:
            return arules2py(methods.new("itemsets", items, quality))
    
    def items(self):
        """return items as an itemMatrix"""
        return ItemMatrix(ro.r('function(x) lhs(x)')(self))


class Transactions(ItemMatrix):
    """Class for arules transactions object"""
    
    @staticmethod
    def new(items):
        return Transactions(methods.new("transactions", items))
    
    @staticmethod
    def from_df(x, itemLabels = None):
        """convert pandas dataframe into an arules transactions object"""
    
        with (ro.default_converter + ro.pandas2ri.converter).context():
            x_r = ro.conversion.get_conversion().py2rpy(x)
    
        if itemLabels == None:
            return Transactions(R_arules.transactions(x_r))
        else:
            return Transactions(R_arules.transactions(x_r, itemLabels))


# package functions
discretizeDF = arules2py_decor(R_arules.discretizeDF)
discretizeDF.__doc__ = R_arules.discretizeDF.__doc__   

apriori = arules2py_decor(R_arules.apriori)
apriori.__doc__ = R_arules.apriori.__doc__

eclat = arules2py_decor(R_arules.eclat)
eclat.__doc__ = R_arules.eclat.__doc__

def concat(list):
    """Combining Association and Transaction Objects"""
    
    conc = methods.selectMethod("c", tuple(list[0].rclass)[0])
    return arules2py(conc(*list))