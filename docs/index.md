# arulespy

`arulespy` is a Python interface to the [R package arules](https://github.com/mhahsler/arules) for mining frequent itemsets and association rules. It provides `Transactions`, `Rules`, `Itemsets`, and `ItemMatrix` classes, as well as visualization through the optional [arulesViz](https://github.com/mhahsler/arulesViz) package.

## Install

The package supports Python 3.11 through 3.14 and requires R 4.5 or later. A conda environment provides compatible Python, R, and `rpy2` versions:

```sh
conda create --name arulespy -c conda-forge python=3.13 r-base r-arules rpy2 pip
conda activate arulespy
python -m pip install arulespy
```

See the [README](https://github.com/mhahsler/arulespy#installation) for other installation methods and troubleshooting.

## Get started

```python
import pandas as pd
from arulespy import Transactions, apriori, parameters

data = pd.DataFrame(
    [[True, True, True], [True, False, False], [True, True, True]],
    columns=list("ABC"),
)
transactions = Transactions.from_df(data)
rules = apriori(
    transactions,
    parameter=parameters({"supp": 0.1, "conf": 0.8}),
    control=parameters({"verbose": False}),
)
print(rules.as_df())
```

See the [examples](examples.md) for complete notebooks and their exported HTML versions. Python's `help()` provides API documentation; the [arules reference manual](https://mhahsler.r-universe.dev/arules/doc/manual.html) describes the underlying R operations.
