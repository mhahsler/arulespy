import pandas as pd
import pytest

from arulespy.arules import Transactions, apriori, eclat, parameters

@pytest.fixture(scope="module")
def transaction_df():
    return pd.DataFrame(
        [
            [True, True, False],
            [True, False, True],
            [False, True, True],
        ],
        columns=list("ABC"),
    )


@pytest.fixture(scope="module")
def transactions(transaction_df):
    return Transactions.from_df(transaction_df)


@pytest.fixture(scope="module")
def itemsets(transactions):
    return eclat(
        transactions,
        parameter=parameters({"supp": 0.3}),
        control=parameters({"verbose": False}),
    )


@pytest.fixture(scope="module")
def rules(transactions):
    return apriori(
        transactions,
        parameter=parameters({"supp": 0.3, "conf": 0.5}),
        control=parameters({"verbose": False}),
    )
