#!/bin/bash
# Generate all figures for Paper 2

echo "Generating all paper figures..."

python create_stability_trend_figure.py
python create_reference_classification_figure.py
python create_paper_rm_map.py
python create_paper_blos_map.py
python create_blos_vs_av_figure.py
python create_density_sensitivity_boxplot.py
python create_temperature_sensitivity_boxplot.py

echo ""
echo "All figures generated in figures/ directory:"
ls -lh figures/*.png figures/*.pdf

echo ""
echo "Figures ready for paper:"
echo "  - figures/rm_map.png/pdf"
echo "  - figures/reference_classification.png/pdf"
echo "  - figures/stability_trend.png/pdf"
echo "  - figures/blos_map.png/pdf"
echo "  - figures/BLOS_vs_Av.png/pdf"
echo "  - figures/BDensitySensitivity.png/pdf"
echo "  - figures/BTemperatureSensitivity.png/pdf"
