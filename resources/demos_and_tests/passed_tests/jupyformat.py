"""
basic formatting for jupyter notebooks

USAGE

    from jupyformat import *
    je("-lorem\n-ipsum")       # outputs lorem ipsum as red bulleted list
"""

from IPython.display import HTML
from markdown import markdown
from math import sqrt  # that's a hack; I need it in the sheets I am too lazy to import

########################################################################
## In-Book Messages

def je(md=""):
    """
    returns the markdown md rendered as red text with an error message
    """
    html = markdown(f"**ERROR**\n\n{md}")
    html = f"<div style='color:red; font-size: 150%'>{html}</div>"
    return HTML(html)

def jw(md=""):
    """
    returns the markdown md rendered as orange text with a warning message
    """
    html = markdown(f"**WARNING**\n\n{md}")
    html = f"<div style='color:orange; font-size: 150%'>{html}</div>"
    return HTML(html)

def ji(md=""):
    """
    returns the markdown md rendered as blue text with an info message
    """
    html = markdown(f"**INFO**\n\n{md}")
    html = f"<div style='color:green; font-size: 150%'>{html}</div>"
    return HTML(html)

########################################################################
## Head-of-book messages

def jp(md=""):
    """
    returns the markdown md rendered as green text with a "passed" message
    """
    html = markdown(f"**This notebook passed verification.**\n\n{md}")
    html = f"<div style='color:green; font-size: 120%'>{html}</div>"
    return HTML(html)

def jpw(md=""):
    """
    returns the markdown md rendered as orange text with a "passed but warnings" message
    """
    if md is None:
        md = "(see orange warning messages below for details)"
    html = markdown(f"**This notebook passed verification with WARNINGS.**\n\n{md}")
    html = f"<div style='color:orange; font-size: 120%'>{html}</div>"
    return HTML(html)

def jf(md=None):
    """
    returns the markdown md rendered as red text with a "failed" message
    """
    if md is None:
        md = "(see red error messages below for details)"
    html = markdown(f"**This notebook FAILED verification.**\n\n{md}")
    html = f"<div style='color:red; font-size: 120%'>{html}</div>"
    return HTML(html)

def jv(md=None):
    """
    returns the markdown md rendered as grey text with a "in process of verification" message
    """
    if md is None:
        md = ""
    html = markdown(f"**This notebook is in the process of verification.**\n\n{md}")
    html = f"<div style='color:grey; font-size: 120%'>{html}</div>"
    return HTML(html)


