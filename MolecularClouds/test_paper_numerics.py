"""Focused regression tests for scientific corrections (run from MolecularClouds)."""
import unittest
import numpy as np
import pandas as pd
from LocalLibraries.CalculateB import electronColumnDensity
from LocalLibraries import config
from LocalLibraries.Uncertainty import align_fields, combine_uncertainties


class NumericalChecks(unittest.TestCase):
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
