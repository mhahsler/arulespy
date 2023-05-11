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

if __name__ == '__main__':
    unittest.main()
