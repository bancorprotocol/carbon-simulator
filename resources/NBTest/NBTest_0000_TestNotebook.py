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

import pandas as pd

# # NBTest Test Notebook
#
# The naming convention of a test notebook is 
#
#     NBTest_<testid>_<comment>.ipynb
#     
# and the associated python file (generated by JupyText) is
#     
#     NBTest_<testid>_<comment>.py
#     
# Here, `testid` is any alphanumeric test id, eg `027`, `9.17`, or `backend.023`. `comment` is any text that indicates what this text is about.
#
# The structure of the test notebook is as follows
#
# - A Heading 1 title (ie a line starting with `# # <Heading1>`) that describes the test
# - the preamble with common non-test code, in particular imports
# - the test section (starting at the first Heading 2 title, ie `# ## <Heading2>`
#
# The test section is converted into individual test functions, with the heading indicating its name; for example the code below would be converted into
#
#     def help_segment_1():
#         assert True
#     
#     def help_segment_2():
#         assert False

# ## Segment 1

assert True

# ## Segment 2

assert True

# ## Segment 3 [NOTEST]

# This segment will not be used to create a test (the function will still be generated, but it will be prefixed with `notest` rather than `test`)

assert False


