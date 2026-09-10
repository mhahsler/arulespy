import unittest

import pandas as pd

from arulespy.arules import ItemMatrix, Transactions, apriori, eclat, parameters

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

        labels = rules.labels()
        self.assertEqual(len(rules[:]), len(rules))
        self.assertEqual(len(rules[:0]), 0)
        self.assertEqual(rules[-1].labels(), [labels[-1]])
        self.assertEqual(rules[::-1].labels(), list(reversed(labels)))
        self.assertEqual(rules[[0, -1]].labels(), [labels[0], labels[-1]])

        mask = [False] * len(rules)
        mask[0] = True
        mask[-1] = True
        self.assertEqual(rules[mask].labels(), [labels[0], labels[-1]])

        with self.assertRaises(IndexError):
            rules[len(rules)]
        with self.assertRaises(IndexError):
            rules[-len(rules) - 1]
        with self.assertRaises(IndexError):
            rules[[0, len(rules)]]
        with self.assertRaises(IndexError):
            rules[[True, False]]
        with self.assertRaises(TypeError):
            rules[1.5]
        with self.assertRaises(TypeError):
            rules[[0, 1.5]]
        with self.assertRaises(ValueError):
            rules[::0]

        itemsets = eclat(
            trans,
            parameter=parameters({"supp": 0.1}),
            control=parameters({"verbose": False}),
        )
        items = itemsets.items()
        self.assertIsInstance(items, ItemMatrix)
        self.assertEqual(len(items), len(itemsets))

    def test_readme_example(self):
        from arulespy import Transactions, apriori, parameters

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
        transactions = Transactions.from_df(df)
        rules = apriori(
            transactions,
            parameter=parameters({"supp": 0.1, "conf": 0.8}),
            control=parameters({"verbose": False}),
        )
        result = rules.as_df()

        self.assertEqual(len(result), 8)
        self.assertEqual(
            list(result.columns),
            ["LHS", "RHS", "support", "confidence", "coverage", "lift", "count"],
        )
        self.assertEqual(result["count"].tolist(), [5, 3, 3, 3, 3, 3, 3, 3])


if __name__ == '__main__':
    unittest.main()
