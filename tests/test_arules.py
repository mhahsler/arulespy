import unittest

import pandas as pd
from arulespy import arules


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
        
        trans = arules.transactions(df)
        self.assertEqual(len(trans), 10)

        self.assertEqual(len(arules.unique(trans)), 5)

        rules = arules.apriori(trans,
                    parameter = arules.parameters({"supp": 0.1, "conf": 0.8}), 
                    control = arules.parameters({"verbose": False})) 
        self.assertEqual(len(rules), 6)

        self.assertEqual(len(rules[1:4]), 3)

        self.assertEqual(type(rules.as_df()), pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
