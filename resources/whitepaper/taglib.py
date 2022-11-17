"""
Simple Tag management

:VERSION HISTORY:

- v0.9: basic functionality

:copyright:     (c) Copyright Stefan LOESCH / topaze.blue 2022; ALL RIGHTS RESERVED
:canonicurl:    https://github.com/topazeblue/TopazePublishing/blob/main/code/src/taglib.py
"""
__VERSION__ = "0.9"
__DATE__ = "13/Oct/2022"


class Tags():
    """
    a simple API for tags*
    
    :tagset:    a set of tags*
    
    *a tag is a lowercase string
    """
    def __init__(s, tagset=None):
        if tagset is None: tagset = set()
        s._tagset = tagset
    
    SEPARATOR = ","
    
    @classmethod
    def fromstr(cls, tagstr=None):
        """
        create a tag object from a string
        
        :tagstr:    the (comma separated) string of tags (None is empty)
        """
        if tagstr is None: return cls()
        result = tagstr.split(cls.SEPARATOR)
        result = (cls.normalize(t) for t in result)
        return cls(set(result))
    
    @property
    def str(s):
        """
        returns the tags as str
        """
        return s.SEPARATOR.join(s._tagset)
    
    def addstr(s, tagstr):
        """
        adds a single tag or a set of tags (from string)
        
        :tagstr:   string of tags to add
        :returns:  self (for chaining)
        """
        addtags = s.fromstr(tagstr)
        return s.add(addtags)
    
    def add(s, tags):
        """
        adds a single tag or a set of tags
        
        :tags:     tags to add (as Tag object)
        :returns:  self (for chaining)
        """
        s._tagset = s._tagset.union(tags._tagset)
        return s
    
    def has(s, tag):
        """
        checks whether a single tag is in the tag object
        
        :tag:    the tag to check for
        """
        tag = s.normalize(tag)
        return tag in s._tagset
        
    @staticmethod
    def normalize(tag):
        """
        normalize a tag
        
        :tag:   the non-normalized tag
        :returns:   the normalized tag
        """
        normtag = tag.strip().lower()
        return normtag
        
    def __repr__(s):
        return f"{s.__class__.__name__}({s._tagset})"
    
    def __str__(s):
        return s.str