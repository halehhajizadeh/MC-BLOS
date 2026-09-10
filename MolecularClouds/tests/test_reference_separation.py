import unittest

import pandas as pd

from LocalLibraries.RefJudgeLib import separateReferencePoints, selectSeparatedReferencePoints


class ReferenceSeparationTests(unittest.TestCase):
    def points(self, ra, dec, extinction=None, errors=None):
        n = len(ra)
        return pd.DataFrame({'ID#': list(range(n)), 'Ra(deg)': ra, 'Dec(deg)': dec,
                             'Extinction_Value': extinction if extinction is not None else [1.] * n,
                             'RM_Err(rad/m2)': errors if errors is not None else [1.] * n})

    def test_same_position_prefers_extinction_then_rm_error(self):
        data = self.points([54.] * 3 + [55.], [30.] * 4,
                           [0.7, 0.6, 0.6, 0.8], [0.1, 2., 1., 1.])
        kept, rejected = separateReferencePoints(data, 1.2)
        self.assertEqual(list(kept['ID#']), [2, 3])
        self.assertEqual(set(rejected['ID#']), {0, 1})
        self.assertEqual(len(data), 4)

    def test_ra_wrap_and_high_declination(self):
        data = self.points([359.999, 0.001, 90., 90.1], [0., 0., 89., 89.])
        kept, rejected = separateReferencePoints(data, 1.2)
        self.assertEqual(list(kept['ID#']), [0, 2])
        self.assertEqual(list(rejected['ID#']), [1, 3])

    def test_chain_keeps_separated_endpoints(self):
        kept, _ = separateReferencePoints(self.points([0., .015, .03], [0.] * 3), 1.2)
        self.assertEqual(list(kept['ID#']), [0, 2])

    def test_disabled_empty_and_invalid(self):
        data = self.points([0., 0.], [0., 0.])
        kept, rejected = separateReferencePoints(data, 0.)
        self.assertEqual(len(kept), 2)
        self.assertTrue(rejected.empty)
        self.assertTrue(separateReferencePoints(data.iloc[:0], 1.2)[0].empty)
        for value in [-1., float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                separateReferencePoints(data, value)

    def test_selection_backfills_to_requested_count(self):
        data = self.points([0., 0.01, 0.02, 1., 2.], [0.] * 5,
                           [0.1, 0.2, 0.3, 0.4, 0.5])
        selected = selectSeparatedReferencePoints(data, 3, 1.2)
        self.assertEqual(len(selected), 3)
        self.assertEqual(list(selected['ID#']), [0, 2, 3])


if __name__ == '__main__':
    unittest.main()
