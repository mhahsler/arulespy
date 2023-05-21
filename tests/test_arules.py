import unittest

import pandas as pd

from arulespy.arules import Transactions, apriori, parameters

class TestArules(unittest.TestCase):

    def test_transactions(self):       
        df = pd.DataFrame (
            [
                [True,True, True],
                [True, False,False],
                [True, True, True],
                [True, False, False],
                [True, True, True],
                [True, False, True],
                [True, True, True],
                [False, False, True],
                [False, True, True],
                [True, False, True],
            ],
        columns=list ('ABC')) 
        
        trans = Transactions.from_df(df)
        self.assertEqual(len(trans), 10)

        self.assertEqual(len(trans.unique()), 5)

        rules = apriori(trans,
                    parameter = parameters({"supp": 0.1, "conf": 0.8}), 
                    control = parameters({"verbose": False})) 
        self.assertEqual(len(rules), 6)

        self.assertEqual(len(rules[1:4]), 3)

        self.assertEqual(type(rules.as_df()), pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
