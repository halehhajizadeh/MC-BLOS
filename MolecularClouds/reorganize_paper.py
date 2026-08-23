#!/usr/bin/env python3
"""
Reorganize the paper to place tables and figures near where they're referenced
"""

# This script will help reorganize the LaTeX file
# We need to:
# 1. Extract all table and figure environments
# 2. Identify where they're first referenced in the text
# 3. Insert them right after those references

import re

# Read the file
with open('paper_perseus_magnetic_field.tex', 'r') as f:
    content = f.read()

# Split into sections
# For now, let's just print the structure
sections = re.findall(r'\\(sub)?section\{([^}]+)\}', content)
for sec in sections[:20]:
    print(f"  {sec[0]}section: {sec[1]}")

# Find all table and figure references
refs = re.findall(r'\\ref\{(tab|fig):[^}]+\}', content)
print(f"\nFound {len(set(refs))} unique table/figure references")
