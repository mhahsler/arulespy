# <img src="arulespy.svg" align="right" height="139" /> Python interface to the R package arules

[![PyPI
package](https://img.shields.io/badge/pip%20install-arulespy-brightgreen)](https://pypi.org/project/arulespy/)
[![version
number](https://img.shields.io/pypi/v/arulespy?color=green&label=version)](https://github.com/mhahsler/arulespy/releases)
[![Actions
Status](https://github.com/mhahsler/arulespy/workflows/Test/badge.svg)](https://github.com/mhahsler/arulespy/actions)
[![License](https://img.shields.io/github/license/mhahsler/arulespy)](https://github.com/mhahsler/arulespy/blob/main/LICENSE)

The `arules` module in `arulespy` provides an easy to install Python interface to the 
[R package arules](https://github.com/mhahsler/arules) for association rule mining built 
with [`rpy2`](https://pypi.org/project/rpy2/). 

The R arules package implements a comprehensive
infrastructure for representing, manipulating and analyzing transaction data and patterns using frequent itemsets and association rules. 
The package also provides a wide range of interest measures and mining algorithms including the code of Christian Borgelt’s popular 
and efficient C implementations of the association mining algorithms Apriori and Eclat,
and optimized C/C++ code for 
mining and manipulating association rules using sparse matrix representation. 

The `arulesViz` module provides `plot()` for visualizing association rules using
the [R package arulesViz](https://github.com/mhahsler/arulesViz).

`arulespy` provides Python classes
for

-   `Transactions`: Convert pandas dataframes into transaction data
-   `Rules`: Association rules
-   `Itemsets`: Itemsets

with Phyton-style slicing and `len()`. 

Most arules functions are
interfaced with conversion from the R data structures to Python.
Documentation is avaialible in Python via `help()`. Detailed online documentation
for the R package is available [here](https://mhahsler.r-universe.dev/arules/doc/manual.html). 

Low-level `arules` functions can also be directly used in the form 
`arules.r.<arules R function>()`. The result will be a `rpy2` data type.
Transactions, itemsets and rules can manually be converted to Python
classes using the helper function `a2p()`.

## Installation

`arulespy` is based on the python package `rpy2` which requires a R installation.

1. Install R from https://www.r-project.org/
2. Install `arulespy` which will automatically install `rpy2` and `pandas`.
    ``` sh
    pip install arulespy
    ```
3. Optional: Set the environment variable `R_LIBS` to decide where R packages are stored. If not set then 
  R will determine a suitable location.

Note: `libcurl` needs to be installed on Linux-based systems.

## Example

``` python
from arulespy import arules

import pandas as pd

df = pd.DataFrame (
    [
        [True,True, True],
        [True, False,False],
        [True, True, True],
        [True, False, False],
        [True, True, True]
    ],
    columns=list ('ABC')) 

# convert dataframe to transactions
trans = arules.transactions(df)

# mine association rules
rules = arules.apriori(trans,
                    parameter = arules.parameters({"supp": 0.1, "conf": 0.8}), 
                    control = arules.parameters({"verbose": False}))  

# display the rules
rules.as_df()
```

```
	LHS	    RHS     support	confidence	coverage	lift	count
1	{}      {A}	    1.0     1.0	        1.0	        1.000000	5
2	{B}     {C}	    0.6	    1.0	        0.6	        1.666667	3
3	{C}     {B}	    0.6	    1.0	        0.6	        1.666667	3
4	{B}     {A}	    0.6	    1.0	        0.6	        1.000000	3
5	{C}     {A}	    0.6	    1.0	        0.6	        1.000000	3
6	{B,C}   {A}	    0.6	    1.0	        0.6	        1.000000	3
7	{A,B}   {C}	    0.6	    1.0	        0.6	        1.666667	3
8	{A,C}   {B}	    0.6	    1.0	        0.6	        1.666667	3
```

Complete examples:
  * [Using arules](https://mhahsler.github.io/arulespy/examples/arules.html)
  * [Using arulesViz](https://mhahsler.github.io/arulespy/examples/arulesViz.html)


## References

- Michael Hahsler, Sudheer Chelluboina, Kurt Hornik, and Christian
  Buchta. [The arules R-package ecosystem: Analyzing interesting
  patterns from large transaction
  datasets.](https://jmlr.csail.mit.edu/papers/v12/hahsler11a.html)
  *Journal of Machine Learning Research,* 12:1977-1981, 2011.
- Michael Hahsler, Bettina Grün and Kurt Hornik. [arules - A
  Computational Environment for Mining Association Rules and Frequent
  Item Sets.](https://dx.doi.org/10.18637/jss.v014.i15) *Journal of
  Statistical Software,* 14(15), 2005.
- Hahsler, Michael. [A Probabilistic Comparison of Commonly Used
  Interest Measures for Association
  Rules](https://mhahsler.github.io/arules/docs/measures), 2015, URL:
  <https://mhahsler.github.io/arules/docs/measures>.
- Michael Hahsler. [An R Companion for Introduction to Data Mining:
  Chapter
  5](https://mhahsler.github.io/Introduction_to_Data_Mining_R_Examples/book/association-analysis-basic-concepts-and-algorithms.html),
  2021, URL:
  <https://mhahsler.github.io/Introduction_to_Data_Mining_R_Examples/book/>

