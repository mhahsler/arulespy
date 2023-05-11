import unittest

import pandas as pd
import arules


class TestSimple(unittest.TestCase):

    def test_add(self):
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
