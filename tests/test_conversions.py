import numpy as np
import pandas as pd
import pytest
import rpy2.robjects as ro
from scipy.sparse import csc_matrix

from arulespy.arules import (
    ItemMatrix,
    Itemsets,
    Transactions,
    arules2py,
    concat,
    parameters,
)


def test_dense_and_sparse_transaction_views(transactions):
    expected = np.array(
        [
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
        ]
    )

    np.testing.assert_array_equal(transactions.as_matrix(), expected)

    sparse = transactions.as_csc_matrix()
    assert isinstance(sparse, csc_matrix)
    np.testing.assert_array_equal(sparse.toarray(), expected)


def test_list_and_dictionary_transaction_views(transactions):
    expected = [["A", "B"], ["A", "C"], ["B", "C"]]

    assert transactions.as_list() == expected
    assert list(transactions.as_dict().values()) == expected
    assert transactions.as_int_list() == [[1, 2], [1, 3], [2, 3]]
    assert transactions.labels() == ["{A,B}", "{A,C}", "{B,C}"]
    assert transactions.itemLabels() == ["A", "B", "C"]


def test_item_metadata_and_frequency(transactions):
    info = transactions.itemInfo()

    assert isinstance(info, pd.DataFrame)
    assert info["labels"].tolist() == ["A", "B", "C"]
    assert transactions.itemFrequency() == [2, 2, 2]
    assert transactions.itemFrequency("relative") == pytest.approx([2 / 3] * 3)


def test_python_style_item_matrix_aliases(transactions):
    assert transactions.item_info().equals(transactions.itemInfo())
    assert transactions.item_labels() == transactions.itemLabels()
    assert transactions.item_frequency() == transactions.itemFrequency()


def test_arules2py_converts_common_r_types():
    assert arules2py(ro.StrVector(["A", "B"])) == ["A", "B"]
    assert arules2py(ro.IntVector([1, 2])) == [1, 2]
    assert arules2py(ro.FloatVector([1.5, 2.5])) == [1.5, 2.5]
    assert arules2py(ro.BoolVector([True, False])) == [True, False]

    matrix = ro.r.matrix(ro.IntVector([1, 2, 3, 4]), nrow=2)
    np.testing.assert_array_equal(arules2py(matrix), np.array([[1, 3], [2, 4]]))

    frame = arules2py(ro.DataFrame({"value": ro.IntVector([1, 2])}))
    assert isinstance(frame, pd.DataFrame)
    assert frame["value"].tolist() == [1, 2]


def test_parameters_preserve_names_and_values():
    result = parameters({"supp": 0.1, "verbose": False})

    assert list(result.names) == ["supp", "verbose"]
    assert result.rx2("supp")[0] == pytest.approx(0.1)
    assert result.rx2("verbose")[0] is False


def test_item_matrix_and_transaction_constructors():
    matrix = ItemMatrix.from_list([["A", "B"], ["C"]], ["A", "B", "C"])

    assert matrix.as_list() == [["A", "B"], ["C"]]
    constructed = Transactions.new(matrix)
    assert isinstance(constructed, Transactions)
    assert constructed.labels() == ["{A,B}", "{C}"]


def test_itemset_constructor():
    matrix = ItemMatrix.from_list([["A", "B"], ["C"]], ["A", "B", "C"])

    constructed = Itemsets.new(matrix)
    assert isinstance(constructed, Itemsets)
    assert constructed.labels() == ["{A,B}", "{C}"]


def test_concat_preserves_type_and_order(transactions):
    combined = concat([transactions[:2], transactions[2:]])

    assert isinstance(combined, Transactions)
    assert combined.labels() == transactions.labels()
