"""
Carbon helper module - sundry helpers
"""
__VERSION__ = "1.0"
__DATE__ = "23/01/2023"

import os as _os

def listdir(path, ext=None):
    """
    get a sorted directory listing, filtered by extension; removes extension
    
    :path:     the path of the directory to be listed
    :ext:      the extension (eg ".pickle")
    :returns:  sorted list of filenames, ext removed
    """
    if ext is None:
        flist = _os.listdir(path)
    else:
        ext = ext.lower()
        l = len(ext)
        flist = [fn[:-l] for fn in _os.listdir(path) if fn[-l:].lower() == ext]
    flist.sort()
    return flist