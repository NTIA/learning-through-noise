import unittest
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd

from infer_votes import infer_file_votes, infer_votes


class InferVotesTest(unittest.TestCase):
    def test_example_votes_produce_valid_inferred_distributions(self):
        csv_file = Path(__file__).with_name("example_votes.csv")
        df = pd.read_csv(csv_file)

        inferred = infer_file_votes(
            Namespace(
                csv_file=str(csv_file),
                mean_col="MOS",
                var_col="MOS_Var",
                n_votes_col="n_votes",
                seed=0,
            )
        )

        vote_pattern_dict = {}
        for row, votes in zip(df.itertuples(index=False), inferred):
            expected = np.array([getattr(row, f"V{i}") for i in range(1, 11)])
            _, candidates, _, vote_pattern_dict = infer_votes(
                row.MOS,
                row.MOS_Var,
                row.n_votes,
                vote_pattern_dict=vote_pattern_dict,
                seed=0,
            )

            # Ambiguous MOS/variance pairs may have multiple valid solutions.
            self.assertTrue(
                any(
                    np.array_equal(np.sort(candidate), np.sort(expected))
                    for candidate in candidates
                )
            )
            self.assertEqual(len(votes), row.n_votes)
            self.assertAlmostEqual(np.mean(votes), row.MOS)
            self.assertAlmostEqual(np.var(votes, ddof=1), row.MOS_Var)


if __name__ == "__main__":
    unittest.main()
