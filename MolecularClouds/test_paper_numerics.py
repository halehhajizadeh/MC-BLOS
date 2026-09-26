"""Focused regression tests for scientific corrections (run from MolecularClouds)."""
import unittest
import numpy as np
import pandas as pd
from LocalLibraries.CalculateB import electronColumnDensity
from LocalLibraries import config
from LocalLibraries.Uncertainty import align_fields, combine_uncertainties
from LocalLibraries.PaperDiagnostics import field_difference_steps, mean_contrast, proximity_groups


class NumericalChecks(unittest.TestCase):
    def test_reference_removal_uses_source_ids_not_dataframe_index(self):
        from LocalLibraries.MatchedRMExtinctionFunctions import rmMatchingPts
        data = pd.DataFrame({'ID#': [8, 121, 205], 'value': [1, 2, 3]})
        references = pd.DataFrame({'ID#': [121, 205]})
        result = rmMatchingPts(data, references)
        self.assertEqual(result['ID#'].tolist(), [8])
        self.assertEqual(result['value'].tolist(), [1])

    def test_literature_attribution_closes_across_sign_change(self):
        ne, a, b, c = field_difference_steps(-8.3, -39.4, -196., 34.92, 31.55, .25)
        self.assertGreater(ne, 0)
        self.assertAlmostEqual(-196 + a + b + c, (34.92-31.55)/(.812*.25))

    def test_regional_rm_contrast_cancels_scalar_reference(self):
        x = np.array([12., 18., -2., 6.])
        north = [True, True, False, False]
        self.assertAlmostEqual(mean_contrast(x, north), mean_contrast(x-31.6, north))

    def test_proximity_groups_include_transitive_neighbours(self):
        sep = np.array([[0,1,2,9],[1,0,1,8],[2,1,0,7],[9,8,7,0]])
        np.testing.assert_array_equal(proximity_groups(sep), [0,0,0,1])

    def column(self, av, abundance, layer, depth):
        return electronColumnDensity(av, abundance, [layer], [2*depth])[0]/config.VExtinct_2_Hcol

    def test_constant_abundance_integrates_to_depth(self):
        for depth, layer in [(0,0),(.25,0),(1,0),(1.5,1),(2,1),(2.5,2),(3,2)]:
            self.assertAlmostEqual(self.column([1,2,3],[4,4,4],layer,depth),4*depth)

    def test_boundary_abundance_interpolation(self):
        # Existing full-layer rectangular quadrature, linearly interpolated
        # abundance for the partial second layer: 1*4 + .5*3 = 5.5.
        self.assertAlmostEqual(self.column([1,2],[4,2],1,1.5),5.5)

    def test_outside_grid_is_nan(self):
        self.assertTrue(np.isnan(self.column([1,2],[4,2],np.nan,3)))

    def test_sensitivity_permutation_and_extra_rows(self):
        base=pd.DataFrame({'ID#':[7,2]})
        other=pd.DataFrame({'ID#':[2,99,7],'Magnetic_Field(uG)':[20,990,70]})
        np.testing.assert_array_equal(align_fields(base,other),[70,20])

    def test_missing_or_duplicate_sources_fail(self):
        base=pd.DataFrame({'ID#':[7,2]})
        for ids in [[7],[7,7,2]]:
            with self.assertRaises(ValueError):
                align_fields(base,pd.DataFrame({'ID#':ids,'Magnetic_Field(uG)':np.ones(len(ids))}))

    def test_zero_cloud_extinction_remains_unbounded(self):
        base=pd.DataFrame({'ID#':[1],'Ra(deg)':[0],'Dec(deg)':[0],'Extinction':[1],
          'Magnetic_Field(uG)':[10.],'TotalRMScaledErrWithStDev':[1.],
          'Electron_Column_pc_cm3':[1.],'BField_of_Min_Extinction':[np.inf],
          'BField_of_Max_Extinction':[5.]})
        r=combine_uncertainties(base,base,base,base,base)
        self.assertTrue(np.isinf(r.TotalUpperBUncertainty.iloc[0]))
        self.assertTrue(r.UnboundedExtinctionSensitivity.iloc[0])

if __name__=='__main__':
    unittest.main()
