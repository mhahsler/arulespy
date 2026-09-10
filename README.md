# Python interface to the R package arules

[![PyPI
package](https://img.shields.io/badge/pip%20install-arulespy-brightgreen)](https://pypi.org/project/arulespy/)
[![version
number](https://img.shields.io/pypi/v/arulespy?color=green&label=version)](https://github.com/mhahsler/arulespy/releases)
[![Actions
Status](https://github.com/mhahsler/arulespy/workflows/Test/badge.svg)](https://github.com/mhahsler/arulespy/actions)
[![License](https://img.shields.io/github/license/mhahsler/arulespy)](https://github.com/mhahsler/arulespy/blob/main/LICENSE)

`arulespy` is a Python package available from [PyPI](https://pypi.org/project/arulespy/).
Its `arules` module provides a Python interface to the popular
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

`arulespy` provides Python classes for:

- `Transactions`: transaction data, including conversion from pandas DataFrames
- `Rules`: association rules
- `Itemsets`: itemsets
- `ItemMatrix`: sparse representations of sets of items

These classes support `len()`, integer indexing, negative indexing, integer
sequences, boolean masks, and Python-style slicing.

Python-style snake-case names are available for APIs inherited from R, such as
`item_frequency()`, `item_info()`, `item_labels()`, `interest_measure()`,
`add_quality()`, `arules_to_py()`, `discretize_df()`, `inspect_dt()`, and
`rule_explorer()`. Interactive R HTML widgets can be embedded reliably in
notebooks with `html_widget()`.
The original R-style names remain available for compatibility.

Most arules operations are exposed as methods on these classes, with common R
results converted into pandas, NumPy, or SciPy objects. API documentation is
available through Python's `help()`. See the
[arules reference manual](https://mhahsler.r-universe.dev/arules/doc/manual.html)
for details about the underlying R operations.

For low-level access, import `R_arules` and call translated R function names,
for example `R_arules.random_transactions(...)`. These calls return rpy2
objects. Convert supported R objects into arulespy or standard Python objects
with `arules_to_py()`.

To cite the Python module ‘arulespy’ in publications use:

> Michael Hahsler. ARULESPY: Exploring association rules and frequent itemsets in Python. arXiv:2305.15263 [cs.DB], May 2023. DOI: [10.48550/arXiv.2305.15263](https://doi.org/10.48550/arXiv.2305.15263)


## Installation

`arulespy` supports Python 3.11 through 3.14. It uses `rpy2` and requires
R 4.5 or later with the R package `arules`. The R package `arulesViz` is
optional and is needed only for visualization functions.

Importing `arulespy` by itself does not initialize R or install R packages.
When `arulespy.arules` is first imported, a missing `arules` package is
installed automatically from CRAN. Importing `arulespy.arulesViz` likewise
installs `arulesViz` if needed.

Installing R packages from source can take some time. Conda is recommended for
the compatible Python, R, `arules`, and `rpy2` core environment.

### Recommended: conda

Using conda (for example,
[Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main)) is
recommended because it installs compatible versions of Python, R, `arules`,
and `rpy2` together. Create and activate a dedicated environment:

```sh
conda create --name arulespy --override-channels -c conda-forge python=3.13 r-base=4.5 r-arules "rpy2>=3.6.6" pip
conda activate arulespy
```

Then install `arulespy` from PyPI:

```sh
python -m pip install arulespy
```

The optional `arulesViz` package will be installed automatically when the
visualization interface is first imported. To install it in advance, run:

```sh
Rscript -e 'install.packages("arulesViz", repos="https://cloud.r-project.org")'
```

Do not add `r-arulesViz` to this Python 3.13 Conda environment if the available
Conda build requires R 4.3. That conflicts with the newer R required by current
`rpy2`; installing `arulesViz` from CRAN avoids the incompatible Conda pin.

### Using an existing R installation

Make sure that R 4.5 or later is available on `PATH`, then install the Python
package:

```sh
python -m pip install arulespy
```

The required R packages will be installed automatically when their respective
interfaces are imported. To avoid installation during import, preinstall them
with R:

```sh
Rscript -e 'install.packages(c("arules", "arulesViz"), repos="https://cloud.r-project.org")'
```

### Troubleshooting

If rpy2 cannot find R or its shared library, inspect the configuration with
`python -m rpy2.situation`. From a Python session or notebook, use:

```python
from rpy2 import situation

for row in situation.iter_info():
    print(row)
```

The output should contain `Loading R library from rpy2: OK`.

On Linux, if R is on `PATH` but its shared library cannot be loaded, set the
library path reported by rpy2 before starting Python:

```sh
export LD_LIBRARY_PATH="$(python -m rpy2.situation LD_LIBRARY_PATH):${LD_LIBRARY_PATH}"
```

On Windows, the conda installation above is recommended. For a separate R
installation, make sure R's binary directory is on `PATH` and, if needed, that
`R_HOME` points to the R installation directory. Consult the current
[rpy2 installation documentation](https://rpy2.github.io/doc/latest/html/overview.html)
when diagnosing native installation problems.


## Example

```python
import pandas as pd

from arulespy import Transactions, apriori, parameters

# Define transaction data as a pandas DataFrame.
df = pd.DataFrame(
    [
        [True, True, True],
        [True, False, False],
        [True, True, True],
        [True, False, False],
        [True, True, True],
    ],
    columns=list("ABC"),
)

# Convert the DataFrame to transactions.
transactions = Transactions.from_df(df)

# Mine association rules.
rules = apriori(
    transactions,
    parameter=parameters({"supp": 0.1, "conf": 0.8}),
    control=parameters({"verbose": False}),
)

# Display the rules as a pandas DataFrame.
rules.as_df()
```

| LHS   | RHS | support | confidence | coverage | lift     | count |
|:------|:----|--------:|-----------:|---------:|---------:|------:|
| {}    | {A} | 1.0     | 1.0        | 1.0      | 1.000000 | 5     |
| {B}   | {C} | 0.6     | 1.0        | 0.6      | 1.666667 | 3     |
| {C}   | {B} | 0.6     | 1.0        | 0.6      | 1.666667 | 3     |
| {B}   | {A} | 0.6     | 1.0        | 0.6      | 1.000000 | 3     |
| {C}   | {A} | 0.6     | 1.0        | 0.6      | 1.000000 | 3     |
| {B,C} | {A} | 0.6     | 1.0        | 0.6      | 1.000000 | 3     |
| {A,B} | {C} | 0.6     | 1.0        | 0.6      | 1.666667 | 3     |
| {A,C} | {B} | 0.6     | 1.0        | 0.6      | 1.666667 | 3     |

Complete examples:

- [Using arules](https://mhahsler.github.io/arulespy/examples/arules.html)
- [Using arulesViz](https://mhahsler.github.io/arulespy/examples/arulesViz.html)


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
