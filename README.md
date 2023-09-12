# Python interface to the R package arules

[![PyPI
package](https://img.shields.io/badge/pip%20install-arulespy-brightgreen)](https://pypi.org/project/arulespy/)
[![version
number](https://img.shields.io/pypi/v/arulespy?color=green&label=version)](https://github.com/mhahsler/arulespy/releases)
[![Actions
Status](https://github.com/mhahsler/arulespy/workflows/Test/badge.svg)](https://github.com/mhahsler/arulespy/actions)
[![License](https://img.shields.io/github/license/mhahsler/arulespy)](https://github.com/mhahsler/arulespy/blob/main/LICENSE)

`arulespy` is a Python module available from [PyPI](https://pypi.org/project/arulespy/).
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
-   `ItemMatrix`: sparse matrix representation of sets of items.

with Phyton-style slicing and `len()`. 

Most arules functions are
interfaced as methods for the four classes with conversion from the R data structures to Python.
Documentation is avaialible in Python via `help()`. Detailed online documentation
for the R package is available [here](https://mhahsler.r-universe.dev/arules/doc/manual.html). 

Low-level `arules` functions can also be directly used in the form 
`R.<arules R function>()`. The result will be a `rpy2` data type.
Transactions, itemsets and rules can manually be converted to Python
classes using the helper function `a2p()`.

To cite the Python module ‘arulespy’ in publications use:

> Michael Hahsler. ARULESPY: Exploring association rules and frequent itemsets in Python. arXiv:2305.15263 [cs.DB], May 2023. DOI: [10.48550/arXiv.2305.15263](https://doi.org/10.48550/arXiv.2305.15263)


## Installation

`arulespy` is based on the python package `rpy2` which requires an R installation. Here are the installation steps:

1. Install the latest version of R (>4.0) from https://www.r-project.org/

2. Install required libraries on your OS:
   - libcurl is needed by R package [curl](https://cran.r-project.org/web/packages/curl/index.html).
      - Ubuntu: `sudo apt-get install libcurl4-openssl-dev`
      - MacOS: `brew install curl`
      - Windows: no installation necessary, but read the Windows section below.

3. Install `arulespy` which will automatically install `rpy2` and `pandas`.
    ``` sh
    pip install arulespy
    ```

4. Optional: Set the environment variable `R_LIBS_USER` to decide where R packages are stored 
    (see [libPaths()](https://stat.ethz.ch/R-manual/R-devel/library/base/html/libPaths.html) for details). If not set then R will determine a suitable location.

5. Optional: `arulespy` will install the needed R packages when it is imported for the first time.
    This may take a while. R packages can also be preinstalled. Start R and run 
    `install.packages(c("arules", "arulesViz"))`


The most likely issue is that `rpy2` does not find R or R's shared library. 
This will lead the python kernel to die or exit without explanation when the package `arulespy` is imported.
Check `python -m rpy2.situation` to see if R and R's libraries are found.
If you use iPython notebooks then you can include the following code block in your notebook to check:
```python
from rpy2 import situation

for row in situation.iter_info():
    print(row)
```

The output should include a line saying `Loading R library from rpy2: OK`.

### Note for Windows users
 `rpy2` currently does not fully support Windows and the installation is somewhat tricky. I was able to use it with the following setup:

* Windows 10
* rpy2 version 3.5.14
* Python version 3.10.12
* R version 4.3.1

I use the following code to set the needed environment variables needed by Windows 
before I import from `arulespy`
```python
from rpy2 import situation
import os

r_home = situation.r_home_from_registry()
r_bin = r_home + '\\bin\\x64\\'
os.environ['R_HOME'] = r_home
os.environ['PATH'] =  r_bin + ";" + os.environ['PATH']
os.add_dll_directory(r_bin)

for row in situation.iter_info():
    print(row)
```

The output should include a line saying `Loading R library from rpy2: OK`

More information on installing `rpy2` can be found [here](https://pypi.org/project/rpy2/).


## Example

```python
from arulespy.arules import Transactions, apriori, parameters
import pandas as pd

# define the data as a pandas dataframe
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
trans = transactions.from_df(df)

# mine association rules
rules = apriori(trans,
                    parameter = parameters({"supp": 0.1, "conf": 0.8}), 
                    control = parameters({"verbose": False}))  

# display the rules as a pandas dataframe
rules.as_df()
```

|    | LHS   | RHS   |   support |   confidence |   coverage |   lift |   count |
|---:|:------|:------|----------:|-------------:|-----------:|-------:|--------:|
|  1 | {}    | {A}   |       0.8 |          0.8 |        1   |   1    |       8 |
|  2 | {}    | {C}   |       0.8 |          0.8 |        1   |   1    |       8 |
|  3 | {B}   | {A}   |       0.4 |          0.8 |        0.5 |   1    |       4 |
|  4 | {B}   | {C}   |       0.5 |          1   |        0.5 |   1.25 |       5 |
|  5 | {A,B} | {C}   |       0.4 |          1   |        0.4 |   1.25 |       4 |
|  6 | {B,C} | {A}   |       0.4 |          0.8 |        0.5 |   1    |       4 |

Complete examples:
  * [Using arules](https://mhahsler.github.io/arulespy/examples/arules.html)
  * [Using arulesViz](https://mhahsler.github.io/arulespy/examples/arulesViz.html)


## References

- Michael Hahsler. [ARULESPY: Exploring association rules and frequent itemsets in 
  Python.](http://dx.doi.org/10.48550/arXiv.2305.15263) arXiv:2305.15263 [cs.DB], May 2023. 
  DOI: 10.48550/arXiv.2305.15263
- Michael Hahsler, Sudheer Chelluboina, Kurt Hornik, and Christian
  Buchta. [The arules R-package ecosystem: Analyzing interesting
  patterns from large transaction
  datasets.](https://jmlr.csail.mit.edu/papers/v12/hahsler11a.html)
  *Journal of Machine Learning Research,* 12:1977-1981, 2011.
- Michael Hahsler, Bettina Grün and Kurt Hornik. [arules - A
  Computational Environment for Mining Association Rules and Frequent
  Item Sets.](https://dx.doi.org/10.18637/jss.v014.i15) *Journal of
  Statistical Software,* 14(15), 2005. DOI: 10.18637/jss.v014.i15
- Hahsler, Michael. [A Probabilistic Comparison of Commonly Used
  Interest Measures for Association
  Rules](https://mhahsler.github.io/arules/docs/measures), 2015, URL:
  <https://mhahsler.github.io/arules/docs/measures>.
- Michael Hahsler. [An R Companion for Introduction to Data Mining:
  Chapter
  5](https://mhahsler.github.io/Introduction_to_Data_Mining_R_Examples/book/association-analysis-basic-concepts-and-algorithms.html),
  2021, URL:
  <https://mhahsler.github.io/Introduction_to_Data_Mining_R_Examples/book/>

