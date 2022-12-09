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

from fls import *
import sys
import os
import re
from collections import namedtuple
__VERSION__ = "1.0"
__DATE__ = "9/Dec/2022"

# # Convert NBTest
#
# Converts files `NBTest_9999_Comment.py -> test_9999_Comment.py` suitable for `pytest`

print(f"NBTestConvert v{__VERSION__} {__DATE__}")

# ## Get script path and set paths

sys.argv[0].rsplit("/", maxsplit=1)

sys.argv[0].rsplit("/", maxsplit=1)[-1]

if sys.argv[0].rsplit("/", maxsplit=1)[-1]=="ipykernel_launcher.py":
    JUPYTER = True
    SCRIPTPATH = os.getcwd()
else:
    JUPYTER = False
    SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))

SRCPATH = os.path.join(SCRIPTPATH, "")
TRGPATH = os.path.join(SCRIPTPATH, "../../Carbon/tests/nbtest")

print("JUPYTER", JUPYTER)
print("SCRIPTPATH", SCRIPTPATH)
print("SRCPATH", SRCPATH)
print("TRGPATH", TRGPATH)
print("---")

# ## Generate the list of files

rawlist = os.listdir(SRCPATH)
rawlist.sort()
#rawlist

# +
dr_nt = namedtuple("datarecord_nt", "tid, comment, fn, outfn")
def filterfn(fn):
    """
    takes fn and returns either filelist_nt or None 
    """
    nxsplit = fn.rsplit(".", maxsplit=1)
    if len(nxsplit) < 2: return None
    if not(nxsplit[1].lower()=="py"): return None
    fnsplit = nxsplit[0].split("_")
    if not len(fnsplit) in [2,3]: return None
    if not fnsplit[0] == "NBTest": return None
    tid = fnsplit[1]
    try:
        comment = fnsplit[2]
    except IndexError:
        comment = ""
    outfn = f"test_{tid}_{comment}.py"
    return dr_nt(tid=tid, comment=comment, fn=fn, outfn=outfn)

assert filterfn("README") is None
assert filterfn("NBTest_0000_Bla.ipynb") is None
assert filterfn("NBTest_0000.py")
assert filterfn("Test_0000_Bla.py") is None
assert filterfn("NBTest_1.10.4_Bla.py").tid == "1.10.4"
assert filterfn("NBTest_1.py").comment == ""
filterfn("NBTest_0000_Bla.py")
# -

fnlst = (filterfn(fn) for fn in rawlist)
fnlst = tuple(r for r in fnlst if not r is None)
fnlst


# ## Process files

# +
def funcn(title):
    """convert a title into a function name"""
    funcn = title.lower()
    funcn = funcn.replace(" ", "_")
    funcn = "test_"+funcn
    return funcn

assert funcn("Title") == "test_title"
assert funcn("Advanced Testing") == "test_advanced_testing"
#funcn("Asserting that the radius computes correctly")
# -

def process_code(code, dr, srcpath=None, trgpath=None):
    """
    processes notebook code
    
    :code:    the code to be processed
    :dr:  the associated data record (datarecord_nt)
    :srcpath:   source path (info only)
    :trgpath:   target path (info only)
    """
    lines = code.splitlines()
    outlines = [
                 "# "+"-"*60,
                f"# Auto generated test file `{dr.outfn}`",
                 "# "+"-"*60,
                f"# source file   = {dr.fn}"
    ]
    if srcpath and srcpath != ".":
        outlines += [
                f"# source path   = {srcpath}"
        ]
    if trgpath and trgpath != ".":
        outlines += [
                f"# target path   = {srcpath}"
        ]
    outlines += [
        
                f"# test id       = {dr.tid}",
                f"# test comment  = {dr.comment}",
                 "# "+"-"*60,
                "","",
    ]
    is_precode = True
    for l in lines:
        if l[:4] == "# # ":
            print(f"""Processing "{l[4:]}" ({r.fn})""")
            outlines += [""]
        elif l[:5] == "# ## ":
            title = l[5:].strip()
            fcn = funcn(title)
            print(f"  creating function `{fcn}()` from section {title}")
            outlines += [
                 "",
                 "# "+"-"*60,
                f"# Test      {r.tid}",
                f"# File      {r.outfn}",
                f"# Segment   {title}",
                 "# "+"-"*60,
                f"def {fcn}():",
                 "# "+"-"*60,
            ]
            is_precode = False
        else:
            if is_precode:
                if l[:2] != "# ":
                    outlines += [l]
            else:
                outlines += ["    "+l]
    outcode = "\n".join(outlines)
    return outcode


for r in fnlst:
    code = fload(r.fn, SRCPATH, quiet=True)
    testcode = process_code(code, r, SRCPATH, TRGPATH)
    fsave(testcode, r.outfn, TRGPATH, quiet=True)
    #print(testcode)
    print(f"  saving generated test to {r.outfn}")


