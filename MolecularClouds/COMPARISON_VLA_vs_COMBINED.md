# Comparison: VLA-Only vs Combined Catalog Results

**Date:** 2026-08-13

## Summary Table

| Metric | VLA-Only | Combined | Difference |
|--------|----------|----------|------------|
| **Input RM Sources** | 206 | 263 | +57 (+27.7%) |
| **Matched to Extinction** | 205 | 260 | +55 (+26.8%) |
| **Potential Reference Points** | 18 | 38 | +20 (+111%) |
| **Selected Reference Points** | 8 | 9 | +1 (+12.5%) |
| **BLOS Measurements** | 197 | 251 | +54 (+27.4%) |

## Reference Point Statistics

| Parameter | VLA-Only | Combined |
|-----------|----------|----------|
| Number of ref points | 8 | 9 |
| Reference extinction | 0.479 | (see combined run) |
| Reference RM (rad/m²) | 40.01 | (see combined run) |
| Reference RM std | 6.78 | (see combined run) |
| Reference RM avg error | 1.27 | (see combined run) |

## Key Findings

### VLA-Only Data (perseus_vla_rm.dat)
**Advantages:**
- Homogeneous dataset from single instrument (VLA)
- Consistent observational parameters
- Direct control over data quality
- 205 sources matched to extinction map
- 197 BLOS measurements with full uncertainty analysis

**Limitations:**
- Fewer reference points available (18 potential → 8 selected)
- Lower spatial coverage
- 54 fewer BLOS measurements compared to combined

### Combined Catalog (perseus_combined.dat)
**Advantages:**
- 57 additional sources (+27.7% increase)
- 20 more potential reference points (111% increase)
- Better spatial coverage across Perseus region
- 54 more BLOS measurements (+27.4%)
- More robust reference RM determination with 9 points

**Considerations:**
- Includes 17 duplicate sources (removed via 10" matching)
- Mixed data from VLA + Taylor catalog sources
- Potential inhomogeneity in observational parameters

## Catalog Files Available

1. **perseus_vla_rm.dat** - Your VLA observations only (206 sources)
2. **perseus_combined.dat** - Combined VLA + Taylor catalog (263 unique sources)
3. **catalog.dat** - Full Taylor et al. 2009 catalog (37,543 sources)

## Current Configuration

**Active catalog:** perseus_vla_rm.dat (VLA-only)

To switch back to combined catalog:
```ini
# In configDirectoryAndNames.ini, change:
rm catalogue = perseus_combined.dat
```

## Recommendations

**Use VLA-only (perseus_vla_rm.dat) if:**
- You need homogeneous, well-characterized data
- Data consistency is critical for your analysis
- You're publishing VLA-specific results

**Use Combined (perseus_combined.dat) if:**
- You want maximum spatial coverage
- More BLOS measurements outweigh inhomogeneity concerns
- You need better reference point statistics
- You're doing exploratory analysis or need comprehensive coverage

## Output Locations

- **VLA-only results:** `FileOutput/Perseus/FinalData/` (current)
- **Combined results:** Overwritten by current VLA-only run

To preserve both runs, rename the output directory after each run or use separate cloud configurations.
