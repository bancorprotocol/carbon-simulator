"""
Carbon helper module -- check version requirements are met

    require_version()
"""
import re as _re
from .. import __version__

class VersionRequirementNotMetError(RuntimeError): pass

def split_version_str(vstr):
    """splits version mumber string into tuple (int, int, int, ...)"""
    m = _re.match("^([0-9\.]*)", vstr.strip())
    if m is None:
        raise ValueError("Invalid version number string", vstr)
    vlst = [int(x) for x in m.group(0).split(".")]
    return vlst

def require_version(required, actual=None, raiseonfail=True):
    """
    checks whether required version is smaller or equal actual version
    
    :required:    the required version, eg "1.2.1"
    :actual:      the actual version, eg "1.3-beta2"
    :returns:     True if requirements are met, False else*
    
    *note: "1.3-beta1" MEETS the requirement "1.3"!
    """
    if actual is None: actual = __version__

    rl, al = split_version_str(required), split_version_str(actual)
    #print(f"required={rl}, actual={al}")

    result = _require_version(rl,al)
    if not raiseonfail:
        return result
    if not result:
        raise VersionRequirementNotMetError(f"Version requirements not met (required = {rl}, actual = {al})", required, actual)

def _require_version(rl, al):
    """
    checks whether required version is smaller or equal actual version
    
    :rl:        the required version eg (1,2,1)
    :al:        the actual version, eg (1,3)
    :returns:   True if requirements are met, False else*
    """
    for r,a in zip(rl, al):
        #print(f"r={r}, a={a}")
        if r > a:
            return False
        elif r < a:
            return True
    return len(al) >= len(rl)
    