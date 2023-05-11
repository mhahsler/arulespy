# Python interface to the R package arules

[![PyPI
package](https://img.shields.io/badge/pip%20install-arulespy-brightgreen)](https://pypi.org/project/arulespy/)
[![version
number](https://img.shields.io/pypi/v/arulespy?color=green&label=version)](https://github.com/mhahsler/arulespy/releases)
[![Actions
Status](https://github.com/mhahsler/arulespy/workflows/Test/badge.svg)](https://github.com/mhahsler/arulespy/actions)
[![License](https://img.shields.io/github/license/mhahsler/arulespy)](https://github.com/mhahsler/arulespy/blob/main/LICENSE)

This package provides an easy to install Python interface to the R
package arules for association rule mining. It provides Python classes
for

-   `Transactions`
-   `Rules`
-   `Itemsets`
-   `ItemMatrix`

with Phyton style slicing and `len`. Most arules functions are
interfaced with conversion from the R data structures to Python. These
are: ‘addComplement’, ‘apriori’, ‘discretizeDF’, ‘eclat’, ‘info’,
‘interestMeasure’, ‘is_closed’, ‘is_generator’, ‘is_maximal’,
‘is_redundant’, ‘is_significant’, ‘is_subset’, ‘is_superset’,
‘itemFrequency’, ‘items’, ‘labels’, ‘lhs’, ‘parameters’, ‘quality’,
‘random_transactions’, ‘rhs’, ‘sort’, ‘transactions’.

arules functions can also be directly called using
`arules.r.<arules R function>()`. The result will be a `rpy2` data type.
Transactions, itemsets and rules can manually be converted to Python
classes using `a2p()`.

Usage examples can be found [here](howto.html).
