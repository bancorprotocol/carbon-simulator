"""
Manage SymPy formulas and convert them into LaTeX, Desmos etc

:VERSION HISTORY:

- v1.0: basic functionality (creation and access; filter)
- v1.1: added alias and __reps__/__str__; allow chaining
- v1.2: added some fields (title); introduced namespaces
- v1.3: added more fields (isvariable, mainkey, tags)
- v1.4: namespace funcs, more accessors
- v2.0: changing the equation tag (breaking interface change)
- v2.1: allowing combination of two Formulas objects
- v2.2: __getitem__, to_desmos, eval, date & version

:copyright:     (c) Copyright Stefan LOESCH / topaze.blue 2022; ALL RIGHTS RESERVED
:canonicurl:    https://github.com/topazeblue/TopazePublishing/blob/main/code/src/formulalib.py
"""
__VERSION__ = "2.2"
__DATE__ = "20/Nov/2022"

import re as _re
from collections import namedtuple as _namedtuple
from sympy import latex as _latex, Eq as _Eq

try:
    from .taglib import Tags
except:
    from taglib import Tags

_itemnt = _namedtuple("itemnt", "item, title, comment, mainkey, isvariable, tags")
"""
:item:        the actual formula or equation (a SymPy object)
:title:       the item title
:comment:     a comment or explanation related to the item
:mainkey:     the main key for this item (the same across all aliases)
:isvariable:  bool, True means it is a variable, False means it is formula or equation
:tags:        a Tags object
"""

class Formulas():
    """
    container object for SymPy formulas and equations; also a text filter*
    
    :fdict:             the formula dictionary (key -> sympy formula or equation)
    :defaultns:         the default name space (default: None)
    :version:           the version number of this formula object (useful when imported)
    :date:              ditto version date
    :raiseonerror:      if True (default), reading a non-existent key raises an error; False returns None
    
    This object provides a thin interface layer for accessing the formula data (including comments
    that describe the formula). It also allows for regex replacements where a specific pattern is
    replace with the latex content of a formula.

    *a text filter is a function that modifies a text, `f(txt) -> txt`; in this case the filter
    replaces equation tags (typicall in md files) with its latex representation; the filter is
    implemented via the `filter` function, and more importantly via __call__
    """
    def __init__(s, raiseonerror=True, defaultns=None, version=None, date=None):
        s._fdict = dict()
        s.raiseonerror = raiseonerror
        s.defaultns = None
        s.version = version
        s.date = date
    
    def setdefaultns(s, ns=None):
        """
        sets the default namespace

        :ns:    the namespace to set (or None to remove)
        :returns:    the previous default namespace
        """
        oldns = s.defaultns
        s.defaultns = ns
        return oldns

    def add(s, key, item, title=None, comment=None, tagstr=None, ns=None, isvariable=False, aliases=None):
        """
        add (or replace) an item to (in) the formula container
        
        :key:           the key under which the item will be placed (replaces existing content)
        :item:          a sympy object (formula or equation)
        :title:         a title for the equation / formula
        :comment:       a comment explaining the equation / formula
        :tagstr:        a comma separated string of tags
        :ns:            namespace*
        :isvariable:    if True (default is False) this formula contains a single variale
        :aliases:       an iterable of aliases (calls alias for each of them)
        :returns:       the equation

        *if a namespace is provided, then a the namespace together with a period is prepended
        to the key value; many functions are at this stage namespace agnostic, so the fully 
        qualified key must generally be used
        """
        tags = Tags.fromstr(tagstr)
        if ns is None: 
            ns = s.defaultns
        if ns:
            key = f"{ns}.{key}"
        isvariable = True if isvariable else False # force to bool
        
        s._fdict[key] = _itemnt(item, title, comment, key, isvariable, tags)
            # NOTE: _itemnt = _namedtuple("itemnt", "item, title, comment, mainkey, isvariable, tags")
        if not aliases is None:
            for alias in aliases:
                s.alias(alias, key, ns)
        return item

    def addvar(s, key, item, title=None, comment=None, tagstr=None, ns=None):
        """
        alias for add with isvariable=True
        """
        return s.add(key, item, title, comment, tagstr, ns, isvariable=True, aliases=None)
        
    def alias(s, aliaskey, key, ns=None):
        """
        adds an alias (ie an alternative name) for an existing formula / equation

        :aliaskey:      the new key to be added as alias
        :key:           the existing key (must exist, otherwise an error is raised)
        :ns:            namespace*
        :returns:       self (for chaining)

        *the namespace, if provided, is used for the key as well as for the namespace; in order
        to create cross namespace aliases, use a fully qualified key
        """
        if not ns is None:
            aliaskey = f"{ns}.{aliaskey}"
            key = f"{ns}.{key}"
        s._fdict[aliaskey] = s._fdict[key]
        return s._fdict[key].item
    
    def isalias(s, key):
        """
        returns True, iff the key is the primary key and not an alias
        """
        item = s.getfullitem(key, raiseonerror=False)
        if item is None: return None
        return key != item.mainkey

    def addfrom(s, formulas, ns=None):
        """
        add all items from the other formula object to this one

        :formulas:      the other formula object
        :ns:            the namespace applied to the added items*
        :returns:       self (for chaining)

        *namespace handling simply consists of prepending the namespace string with a period
        to the key to all non-namespaced keys; keys that are already namespaced are not touched

        NOTE: the conflict handling here is very poor, or rather non existant, in that keys that
        are used twice will be overwritten (unless they live in separate namespaces of course).


        """
        newitems = formulas.getall()
        if ns: ns = f"{ns}."
        for key,item in newitems.items():
            if ns:
                if len(key.split(".")) == 1:
                    key = ns+key
            s._fdict[key] = item
        return s

    def keys(s, vars=None, ns=None):
        """
        returns all available keys

        :vars:     if True, returns only variable; if False only formulas/equations; if None (default), both 
        """
        result = ((k,v) for k,v in s._fdict.items())
        if not vars is None:
            result = ((k,v) for k,v in result if v.isvariable == vars)
        if not ns is None:
            result = ((k,v) for k,v in result if s.ns(k)==ns)
        return tuple(k for k,_ in result)
    
    @classmethod
    def nskey(cls, key):
        """
        returns the namespace & key of a given key

        :returns:       tuple (namespace, key); empty namespace is ""
        """
        splitkey = key.split(".")
        if len(splitkey) == 1: return "", splitkey[0]
        return splitkey

    @classmethod
    def ns(cls, key):
        """
        returns the namespace of a given key

        :returns:       namespace; empty namespace is ""
        """
        return cls.nskey(key)[0]

    def getfullitem(s, key, raiseonerror=None):
        """
        gets the full item at a specific key
        
        :key:             the key for which the item is to be returned
        :raiseonerror:    if True, raises if key does not exist; if None, uses object default
        :returns:         the itemtuple (item, comment)
        """
        if raiseonerror is None: 
            raiseonerror = s.raiseonerror
        if raiseonerror:
            return s._fdict[key]
        else:
            return s._fdict.get(key)

    def getall(s, keylist=None, raiseonerror=None):
        """
        gets a dict k -> full item of the full items
        
        :keylist:         list of keys for the items to be returned (if None: entire dict)
        :raiseonerror:    if True, raises if key does not exist; if None, ignor
        """
        if keylist is None:
            keylist = s.keys()
        result = {k:s.getfullitem(k, raiseonerror=raiseonerror) for k in keylist}
        return result

    def getitem(s, key, raiseonerror=None):
        """
        gets the item at a specific key
        
        :key:             the key for which the item is to be returned
        :raiseonerror:    if True, raises if key does not exist; if None, uses object default
        :returns:         the item only
        """
        fullitem = s.getfullitem(key, raiseonerror)
        if fullitem is None: return None
        return fullitem.item

    def get(s, key, onerr=None):
        """
        gets the item at a specific key
        
        :key:             the key for which the item is to be returned
        :onerr:           return on error (like dict.get)
        :returns:         the item only
        """
        try:
            return s.getitem(key, raiseonerror=True)
        except:
            return onerr

    def getcomment(s, key, raiseonerror=None):
        """
        gets the comment associated with a specific key
        
        :key:             the key for which the item is to be returned
        :raiseonerror:    if True, raises if key does not exist; if None, uses object default
        :returns:         the comment only (not the item)
        """
        fullitem = s.getfullitem(key, raiseonerror)
        if fullitem is None: return None
        return fullitem.comment  

    def gettitle(s, key, raiseonerror=None):
        """
        gets the title associated with a specific key
        
        :key:             the key for which the item is to be returned
        :raiseonerror:    if True, raises if key does not exist; if None, uses object default
        :returns:         the title only (not the item)
        """
        fullitem = s.getfullitem(key, raiseonerror)
        if fullitem is None: return None
        return fullitem.title    

    def hastag(s, key, tag):
        """
        whether the item associate with a key has a specific tag
        
        :key:             the key for which the item is to be returned
        :tag:             the tag to be tested
        :returns:         True if it has the tag, False if not, None if error
        """
        fullitem = s.getfullitem(key, raiseonerror=False)
        if fullitem is None: return None
        return fullitem.tags.has(tag)    
    
    def getlatex(s, key, raiseonerror=None):
        """
        let getitem, but return the latex representation of the item
        """
        item = s.getitem(key, raiseonerror)
        if item is None: return None
        return _latex(item)
    
    def to_desmos(s, key_or_eq):
        """
        converts a equation into a format (relatively) suitable for import into desmos (ymmv...)
        
        :returns:   the formula as string; equations are returned as tuple lhs, rhs
        """
        if isinstance(key_or_eq, str):
            eq = s.getitem(key_or_eq, raiseonerror=True)
        else:
            eq = key_or_eq
        if isinstance(eq, _Eq):
            lhs = s.to_desmos(eq.lhs)
            rhs = s.to_desmos(eq.rhs)
            return (lhs, rhs)
        
        dstr = str(eq)
        dstr = dstr.replace("**", "^")
        dstr = dstr.replace("*", " ")
        dstr = dstr.replace("/", " / ")
        dstr = dstr.replace("(", " (")
        dstr = dstr.replace(")", ") ")
        return dstr

    @staticmethod
    def eval(funclist, arg):
        """
        helper function: apply the funcs in `funclist` successively to arg

        USAGE

            # shortcut
            e = Formulas.eval

            # set up some substitution rules for SymPy Equations
            ey   = lambda eq: eq.subs(y0, y0_val).subs(y, y_val)
            ex   = lambda eq: eq.subs(x0, x0_val).subs(x, x_val)
            eall = [ex, ey]

            # apply the transformations to SymPy objects
            e(eall, PminYE)
            e(eall, PminE)
            e(eall, PmaxE)

        """
        for f in funclist:
            arg = f(arg)
        return arg


    PATTERN = "\$\$=([A-Za-z0-9_\.]+)=\$\$"
    #PATTERN = "<!--EQ=([A-Za-z0-9_\.]+)-->"
    
    def filter(s, text, pattern=None):
        """
        text filter*: replaces the formulas in the text with the latex from the object (__call__ is an alias)
        
        :text:      the text (markdown or latex) within which the replacement is executed
        :pattern:   the regex pattern used for replacement (if none, uses s.PATTERN)
        :returns:   the text with replacements executed

        NOTE: a filter is a function `f(txt) -> txt`
        """
        if pattern is None: pattern = s.PATTERN
        return _re.sub(pattern, s._replacefunc, text)
        
    def _replacefunc(s, m):
        """
        the actual replacement function that is provided to re.sub
        
        :m:    the match object; eg use m.group(1) to get the first match group
        """
        keyval = m.group(1)
        latexf = s.getlatex(keyval, raiseonerror=False)
        if latexf is None:
            #return f"<!--EQ!=ERROR[{keyval}]-->"
            return f"$$!=ERROR[{keyval}]=$$"
        return f"$$\n{latexf}\n$$"

    def __call__(s, text, pattern=None):
        """
        alias for filter
        """
        return s.filter(text, pattern)

    def __str__(s):
        return f"{s.__class__.__name__}(keys={list(s.keys())})"

    def __repr__(s):
        return s.__str__()

    def __getitem__(s, key):
        return s.get(key)

