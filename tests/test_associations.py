import numpy as np
import pandas as pd
from scipy.sparse import csc_matrix

from arulespy.arules import ItemMatrix, Itemsets, Rules


def test_itemset_accessors_and_predicates(itemsets):
    items = itemsets.items()

    assert isinstance(itemsets, Itemsets)
    assert isinstance(items, ItemMatrix)
    assert items.labels() == itemsets.labels()
    assert len(itemsets.is_closed()) == len(itemsets)
    assert len(itemsets.is_maximal()) == len(itemsets)
    assert len(itemsets.is_generator()) == len(itemsets)


def test_rule_accessors_and_quality(rules):
    quality = rules.quality()

    assert isinstance(rules, Rules)
    assert len(rules.lhs()) == len(rules)
    assert len(rules.rhs()) == len(rules)
    assert isinstance(quality, pd.DataFrame)
    assert {"support", "confidence", "coverage", "lift", "count"} <= set(
        quality.columns
    )


def test_interest_measures(rules, transactions):
    support = rules.interestMeasure(["support"], transactions)

    assert len(support) == len(rules)
    np.testing.assert_allclose(support, rules.quality()["support"])


def test_add_quality_appends_by_row_position(rules):
    rules_copy = rules[:]
    custom = pd.DataFrame({"custom": np.arange(len(rules_copy))})

    rules_copy.addQuality(custom)

    assert rules_copy.quality()["custom"].tolist() == custom["custom"].tolist()


def test_python_style_association_aliases(rules, transactions):
    assert rules.interest_measure(["support"], transactions) == (
        rules.interestMeasure(["support"], transactions)
    )

    rules_copy = rules[:]
    custom = pd.DataFrame({"custom": np.arange(len(rules_copy))})
    rules_copy.add_quality(custom)
    assert rules_copy.quality()["custom"].tolist() == custom["custom"].tolist()


def test_subset_relations_return_dense_or_sparse_matrices(transactions):
    dense = transactions.is_subset(transactions, sparse=False)
    sparse = transactions.is_subset(transactions)

    np.testing.assert_array_equal(dense, np.eye(len(transactions), dtype=int))
    assert isinstance(sparse, csc_matrix)
    np.testing.assert_array_equal(sparse.toarray(), dense)


def test_superset_relations_return_dense_or_sparse_matrices(transactions):
    dense = transactions.is_superset(transactions, sparse=False)
    sparse = transactions.is_superset(transactions)

    np.testing.assert_array_equal(dense, np.eye(len(transactions), dtype=int))
    assert isinstance(sparse, csc_matrix)
    np.testing.assert_array_equal(sparse.toarray(), dense)


def test_rule_constructor(rules):
    constructed = Rules.new(rules.lhs(), rules.rhs())

    assert isinstance(constructed, Rules)
    assert constructed.labels() == rules.labels()
