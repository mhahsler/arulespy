"""The arules module provides an interface to R's arules package."""

from operator import index as integer_index

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as packages
from rpy2.robjects import pandas2ri
from scipy.sparse import csc_matrix

from arulespy import _import_or_install_r_package

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

### import the R arules package
R_arules = _import_or_install_r_package("arules")
methods = packages.importr('methods')
base = packages.importr('base')

### Sparse matrix helper
def ngC_to_csc_matrix(m):
    """Convert an R ``ngCMatrix`` into a SciPy CSC matrix."""
    indices = np.array(m.slots['i'])
    indptr  = np.array(m.slots['p'])
    ## all ones for ngCMatrix
    data = np.array([1]*len(indices))
    return csc_matrix((data, indices, indptr), tuple(m.slots['Dim']))    

### Conversion functions
def arules2py(x):
    """Convert a supported R object into its Python representation.
    
    ``rules``, ``itemsets``, ``transactions``, and ``itemMatrix`` S4 objects
    become their corresponding arulespy classes. R data frames become pandas
    DataFrames, matrices become NumPy arrays, and atomic vectors become lists.
    Objects without a registered conversion are returned unchanged.
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


arules_to_py = arules2py

def arules2py_decor(function):
    """Decorate an R function so its result is passed through ``arules2py``."""
    def wrapper(*args, **kwargs):
        return arules2py(function(*args, **kwargs))
    return wrapper


### arules interface code 
def parameters(x):
    """Create an R named list of mining parameters from a mapping."""
    return ro.ListVector(x)


class ItemMatrix(ro.RS4):
    """Python wrapper for an R arules ``itemMatrix`` object."""
    
    @staticmethod
    def from_list(items, itemLabels):
        """Create an item matrix from item-label sequences.

        Args:
            items: One sequence of item labels per item set.
            itemLabels: Complete ordered collection of valid item labels.
        """
        items = [ro.StrVector(x) for x in items]
        return ItemMatrix(R_arules.encode(items, itemLabels))

    def as_df(self):
        """Return the R data-frame representation as a pandas DataFrame."""
        if type(self) != ro.vectors.DataFrame:
            self  = R_arules.DATAFRAME(self)
        with (ro.default_converter + pandas2ri.converter).context():
            pd_df = ro.conversion.get_conversion().rpy2py(self)
        return pd_df
    
    def as_matrix(self):
        """Return a dense boolean representation as a NumPy array."""
        return np.array(ro.r('function(x) as(x, "matrix")')(self))

    def as_csc_matrix(self):
        """Return the sparse incidence data as a SciPy CSC matrix."""
        return ngC_to_csc_matrix(self.slots['data'])

    def as_dict(self):
        """Return a mapping from zero-based row numbers to item-label lists."""
        l = ro.r('function(x) as(x, "list")')(self)
        l.names = [*range(0, len(l))]
        return dict(zip(l.names, map(list,list(l))))
      
    def as_list(self):
        """Return one list of item labels for each row."""
        return list(self.as_dict().values())  
    
    def as_int_list(self):
        """Return the internal one-based item identifiers for each row."""
        l = ro.r('function(x) LIST(x, decode = FALSE)')(self)
        return [list(x) for x in l]

    def __getitem__(self, key):
        """Return a subset selected with Python indexing semantics.

        Scalar indices return a one-element object of the same arulespy class.
        Slices, integer sequences, and one-dimensional boolean masks return
        subset objects.
        """
        size = len(self)

        if isinstance(key, slice):
            # slice.indices() implements Python's open-ended, negative, and
            # stepped slice semantics and rejects a zero step.
            start, stop, step = key.indices(size)
            r_key = ro.IntVector([i + 1 for i in range(start, stop, step)])
        else:
            try:
                position = integer_index(key)
            except TypeError:
                position = None

            if position is not None:
                if position < 0:
                    position += size
                if position < 0 or position >= size:
                    raise IndexError("arulespy index out of range")
                # Keep a one-element arules object rather than exposing the
                # underlying R S4 representation for scalar selections.
                r_key = ro.IntVector([position + 1])
            else:
                values = np.asarray(key)
                if values.ndim != 1:
                    raise TypeError(
                        "indices must be integers, slices, integer sequences, "
                        "or one-dimensional boolean masks"
                    )

                if np.issubdtype(values.dtype, np.bool_):
                    if len(values) != size:
                        raise IndexError(
                            "boolean index did not match arulespy object length"
                        )
                    r_key = ro.BoolVector(values.tolist())
                else:
                    positions = []
                    for value in values.tolist():
                        try:
                            position = integer_index(value)
                        except TypeError as exc:
                            raise TypeError(
                                "index sequences must contain only integers"
                            ) from exc
                        if position < 0:
                            position += size
                        if position < 0 or position >= size:
                            raise IndexError("arulespy index out of range")
                        positions.append(position + 1)
                    r_key = ro.IntVector(positions)

        # find subset S4 method
        r_subset = methods.selectMethod("[", tuple(self.rclass)[0])

        # make sure to preserve the python class
        class_type = type(self)

        ret = r_subset(self, r_key)
        ret.__class__ = class_type

        return ret
    
    def __len__(self):
        """Return the number of rows represented by this object."""
        return ro.r('function(x) length(x)')(self)[0]
    
    def sort(self, by = "lift", decreasing = True):
        """Return a sorted copy.
        
        Args:
            by: Quality measure used as the sort key.
            decreasing: Sort in descending order when true.
        """
        decreasing  = ro.vectors.BoolVector([decreasing])
        return arules2py(ro.r('function(x, by, decreasing) sort(x, by = by, decreasing = decreasing)')(self, by, decreasing))

    def unique(self):
        """Return a copy with duplicate rows removed."""
        return arules2py(ro.r('function(x) unique(x)')(self))
    
    def sample(self, size = 1, replace = False):
        """Draw rows at random.
        
        Args:
            size: Number of rows to draw.
            replace: Whether a row may be selected more than once.
        """
        replace = ro.vectors.BoolVector([replace])
        return arules2py(ro.r('function(x, size, replace) sample(x, size = size, replace = replace)')(self, size, replace))
    
    def items(self):
        """Return the items represented by this object as an ItemMatrix."""
        return ItemMatrix(ro.r('function(x) items(x)')(self))
    
    def itemFrequency(self, type = "absolute"):
        """Calculate the frequency of each item.
        
        Args:
            type: Either ``"absolute"`` counts or ``"relative"`` frequencies.
        """
        return arules2py(ro.r('function(x, type) itemFrequency(x, type)')(self, type))
    
    def itemInfo(self):
        """Return item metadata as a pandas DataFrame."""
        return arules2py(ro.r('function(x) itemInfo(x)')(self))
    
    def labels(self):
        """Return the formatted label for every row."""
        return arules2py(ro.r('function(x) labels(x)')(self))
    
    def itemLabels(self):
        """Return all item labels in encoding order."""
        return arules2py(ro.r('function(x) itemLabels(x)')(self))

    # Python-style aliases for names inherited from the R API.
    item_frequency = itemFrequency
    item_info = itemInfo
    item_labels = itemLabels
    
    def is_subset(self, x, proper = False, sparse = True):
        """Test whether rows in this object are subsets of rows in ``x``.
        
        Args:
            x: ItemMatrix-compatible object to compare against.
            proper: Exclude equal sets when true.
            sparse: Return a SciPy CSC matrix when true; otherwise a NumPy array.
        """    
        m = ro.r('function(x, y, proper, sparse) is.subset(x, y, proper, sparse)')(self, x, 
                        ro.vectors.BoolVector([proper]), ro.vectors.BoolVector([sparse]))

        if sparse:
            return ngC_to_csc_matrix(m)
        else:
            return np.array(m)  
    
    def is_superset(self, x, proper = False, sparse = True):
        """Test whether rows in this object are supersets of rows in ``x``.
        
        Args:
            x: ItemMatrix-compatible object to compare against.
            proper: Exclude equal sets when true.
            sparse: Return a SciPy CSC matrix when true; otherwise a NumPy array.
        """
        m = ro.r('function(x, y, proper, sparse) is.superset(x, y, proper, sparse)')(self, x, 
                        ro.vectors.BoolVector([proper]), ro.vectors.BoolVector([sparse]))

        if sparse:
            return ngC_to_csc_matrix(m)
        else:
            return np.array(m)     

class Associations(ItemMatrix):
    """Base wrapper shared by association rules and itemsets."""

    def quality(self):
        """Return quality measures as a pandas DataFrame."""
        return arules2py(ro.r('function(x) quality(x)')(self))

    def is_closed(self):
        """Return one closed-itemset indicator per association."""
        return arules2py(ro.r('function(x) is.closed(x)')(self))
    
    def is_maximal(self):
        """Return one maximal-itemset indicator per association."""
        return arules2py(ro.r('function(x) is.maximal(x)')(self))
    
    def is_generator(self):
        """Return one generator indicator per association."""
        return arules2py(ro.r('function(x) is.generator(x)')(self))
    
    def is_redundant(self):
        """Return one redundancy indicator per association rule."""
        return arules2py(ro.r('function(x) is.redundant(x)')(self))
    
    def is_significant(self):
        """Return one significance indicator per association rule."""
        return arules2py(ro.r('function(x) is.significant(x)')(self))
    
    def interestMeasure(self, measure = ["support", "confidence", "lift"], 
                        transactions = None):
        """Calculate additional interest measures.
        
        Args:
            measure: Names of the measures to calculate. See the `measure
                reference <https://mhahsler.github.io/arules/docs/measures>`_.
            transactions: Transactions used by measures that require data.
        """
        if transactions == None:
            transactions = ro.r('NULL')
        return arules2py(ro.r('function(x, measure, transactions) interestMeasure(x, measure, transactions)')
                    (self, measure, transactions))

    def addQuality(self, df):
        """Append quality columns to this object in place.
        
        Args:
            df: DataFrame with one row per association.
        """
        quality = self.quality().reset_index(drop=True)
        additional = df.reset_index(drop=True)
        pd_df = pd.concat([quality, additional], axis=1)
        with (ro.default_converter + pandas2ri.converter).context():
            r_from_pd_df = ro.conversion.get_conversion().py2rpy(pd_df)

        self.slots['quality'] = r_from_pd_df

    # Python-style aliases for names inherited from the R API.
    interest_measure = interestMeasure
    add_quality = addQuality

class Rules(Associations):
    """Python wrapper for an R arules ``rules`` object."""
    
    @staticmethod
    def new(lhs, rhs, quality = None):
        """Create rules from left- and right-hand-side item matrices.

        Args:
            lhs: ItemMatrix containing rule antecedents.
            rhs: ItemMatrix containing rule consequents.
            quality: Optional R data frame containing quality measures.
        """
        if quality == None:
            return Rules(methods.new("rules", lhs=lhs, rhs=rhs))
        else:
            return Rules(methods.new("rules", lhs=lhs, rhs=rhs, quality=quality))
    
    def lhs(self):
        """Return rule antecedents as an ItemMatrix."""
        return ItemMatrix(ro.r('function(x) lhs(x)')(self))
    
    def rhs(self):
        """Return rule consequents as an ItemMatrix."""
        return ItemMatrix(ro.r('function(x) rhs(x)')(self))
    


class Itemsets(Associations):
    """Python wrapper for an R arules ``itemsets`` object."""
    
    @staticmethod
    def new(items, quality = None):
        """Create itemsets from an item matrix and optional quality data."""
        if quality == None:
            return arules2py(methods.new("itemsets", items=items))
        else:
            return arules2py(methods.new("itemsets", items=items, quality=quality))
    
    def items(self):
        """Return the encoded itemsets as an ItemMatrix."""
        return ItemMatrix(ro.r('function(x) items(x)')(self))


class Transactions(ItemMatrix):
    """Python wrapper for an R arules ``transactions`` object."""
    
    @staticmethod
    def new(items):
        """Create transactions from an ItemMatrix."""
        return Transactions(methods.new("transactions", items))
    
    @staticmethod
    def from_df(x, itemLabels = None):
        """Create transactions from a pandas DataFrame.

        Args:
            x: DataFrame in a format accepted by R's ``transactions()``.
            itemLabels: Optional item labels for matrix-like input.
        """
    
        with (ro.default_converter + ro.pandas2ri.converter).context():
            x_r = ro.conversion.get_conversion().py2rpy(x)
    
        if itemLabels == None:
            return Transactions(R_arules.transactions(x_r))
        else:
            return Transactions(R_arules.transactions(x_r, itemLabels))


# package functions
discretizeDF = arules2py_decor(R_arules.discretizeDF)
discretizeDF.__doc__ = R_arules.discretizeDF.__doc__   
discretize_df = discretizeDF

apriori = arules2py_decor(R_arules.apriori)
apriori.__doc__ = R_arules.apriori.__doc__

eclat = arules2py_decor(R_arules.eclat)
eclat.__doc__ = R_arules.eclat.__doc__

def concat(list):
    """Combine compatible association or transaction objects."""
    
    conc = methods.selectMethod("c", tuple(list[0].rclass)[0])
    return arules2py(conc(*list))
