# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Pull Resources

SRC = "../../CarbonTheory/papers/code/src"
DST = "whitepaper"

# !ls {SRC}

# !ls {DST}

COMMANDS = """
#!/bin/bash
cd "$(dirname "$0")"

"""
for fn in ["CarbonCalculations.ipynb", "CarbonCalculations.py", "taglib.py", "formulalib.py"]:
    cmd = f"cp -v {SRC}/{fn} {DST}/{fn}"
    print (cmd)
    COMMANDS += f"{cmd}\n"

print(COMMANDS)


