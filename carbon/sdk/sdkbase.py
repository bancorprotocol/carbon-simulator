import requests
from math import log10, floor
from dataclasses import dataclass
from . import __VERSION__, __DATE__

class SDKBase:
    """
    base class for SDK access via http

    :url:           RPC URL
    :token:         API token
    :apibase:       API base path
    :syncdefault:   if True, by default call the sync endpoint
    :raiseonerror:  if True, serious errors raise an exception
    :disclaimer:    if True, print a disclaimer on instantiation
    :verbose:       if True, print messages when connecting
    :Tokens:        Token container object for token lookup
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    URL = None              # to be set in derived class
    TOKEN = None            # to be set in derived class
    APIBASE = None          # to be set in derived class
    SYNCDEFAULT = True      # if True, by default call the sync endpoint
    RAISEONERROR = True     # if True, serious errors raise an exception
    DISCLAIMER = True       # if True, print a disclaimer on instantiation
    VERBOSE = True          # if True, print messages when connecting
    
    def __init__(self, url=None, token=None, apibase=None, syncdefault=None, 
                        raiseonerror=None, disclaimer=None, verbose=None, Tokens=None):
        if url is None: url = self.URL
        self.url = url
        if token is None: token = self.TOKEN
        self.token = token
        if apibase is None: apibase = self.APIBASE
        self.apibase = apibase
        if syncdefault is None: syncdefault = self.SYNCDEFAULT
        self.syncdefault = syncdefault
        if raiseonerror is None: raiseonerror = self.RAISEONERROR
        self.raiseonerror = raiseonerror
        if disclaimer is None: disclaimer = self.DISCLAIMER
        self.disclaimer = disclaimer
        if verbose is None: verbose = self.VERBOSE
        self.verbose = verbose
        self.Tokens = Tokens
        if self.disclaimer:
            print(self.DISCLAIMERTEXT)
        
    POST = "post"
    GET  = "get"

    DISCLAIMERTEXT = """
    ================================================================
    WARNING: DO NOT USE IN PRODUCTION

    This is a demo and testing wrapper for the Carbon SDK. YOU MUST 
    NOT USE THIS SDK, OR ITS ASSOCIATED NODEJS CODE IN PRODUCTION 
    WHEN FUNDS ARE AT RISK. See the disclaimer on the Carbon SDK 
    NodeJS server for more information.
    ================================================================
    """

    class CarbonSDKValueError(ValueError): pass
    
    def _assertTokensProvided(self):
        """raise an exception if Tokens not in SDK; returns Tokens"""
        if self.Tokens is None:
            raise self.CarbonSDKValueError("Tokens not provided in constructor to SDK", self)
        return self.Tokens
    
    @dataclass
    class ErrorResponse():
        """
        dummy class for error responses from the SDK [returns 900 status code]
        """
        error: str

        @property
        def status_code(self):
            return 900
        
        def json(self):
            return {"status_code": self.status_code, "error": self.error}


    def req0(self, path, params=None, method=None):
        """
        execute a GET or POST request to the API server

        :path:      the full path of the call (everything after the server URL)
        :params:    the params transmitted to the API (POST only)
        :method:    self.GET or self.POST (default GET with no params, POST with)
        """
        if method is None: 
            method = self.GET if params is None else self.POST
            #print ("[req0] method is None, setting to", method, params)
        if params is None: params = dict()
        if method == self.GET and params:
            raise self.CarbonSDKValueError("Must not provide params for GET request", params, method)

        url = self.join(self.URL, path)
        if self.verbose:
            print(f"[req0] method={method}, url={url}, params={params}")
        if method == self.GET:
            try:
                return requests.get(url, headers={"token": self.token})
            except Exception as e:
                return self.ErrorResponse(error=str(e))
            
        elif method == self.POST:
            try:
                return requests.post(url, headers={"token": self.token}, json=params)
            except Exception as e:
                return self.ErrorResponse(error=str(e))
        else:
            raise self.CarbonSDKValueError("Unknown method", method)
    
    def req(self, ep, params=None, method=None):
        """
        execute a GET or POST request to the actual API

        :ep:        API endpoint, including the sync/async prefix (eg 'scall/plus')
        :params:    params transmitted to the API (POST only)
        :method:    self.GET or self.POST
        """
        return self.req0(self.join(self.apibase, ep), params, method)
    
    class APICallError(RuntimeError): pass
    class AsyncAPICallError(ValueError): pass

    def call(self, ep, params=None, method=None, sync=None):
        """
        execute a GET or POST request to the (sync or async) call API 

        :ep:        API endpoint, with the sync/async prefix (eg 'plus')
        :params:    params transmitted to the API (POST only)
        :method:    self.GET or self.POST
        :sync:      whether to call sync or async
        """
        #print("\n\n[call]", ep, params, method, sync)
        url = self.join(self.callapi0(sync), ep)
        if sync: 
            #print("\n\n[call] calling req", ep, params, method, sync)
            retval = self.req(url, params, method)
            #print("\n\n[call] req returned", retval)
            return retval
        try:
            r = self.req(url, params, method)
            rj = r.json()
        except:
            raise self.APICallError("Error calling API", r)

        if not rj.get("success"):
            if self.raiseonerror:
                raise self.AsyncAPICallError("posts", ep, params, rj)
            return False
        return rj["reqid"]

    def callapi0(self, sync=None):
        """returns "s" if  sync, else "as" """ 
        if sync is None: sync = self.syncdefault
        return "scall" if sync else "ascall"
    
    @staticmethod
    def join(url, path):
        """joins a URL (or path fragment and a path, ensuring exactly one slash in-between"""
        if url[-1] == "/": url = url[:-1]
        if path[0] == "/": path = path[1:]
        return f"{url}/{path}"
    
    @staticmethod
    def c2s(camelCaseString):
        """converts camelCaseString to snake_case_string"""
        return ''.join(['_' + i.lower() if i.isupper() else i for i in camelCaseString]).lstrip('_')
    
    @staticmethod
    def s2c(snakeCaseString):
        """converts snake_case_string to camelCaseString"""
        f = snakeCaseString.split('_')
        return ''.join([f[0]]+[i.title() for i in f[1:]])
    
    @staticmethod
    def roundsd(x, nsd=6):
        """
        rounds the value to significant decimals (returns x unmodified if not a number or zero)
        
        :x:      the value to be rounded
        :nsd:    number of significant decimals
        """
        try:
            magnitude = floor(log10(x))
        except:
            return x
        if magnitude <= nsd:
            return round(x,nsd-magnitude-1)
        else:
            shift = 10**(magnitude-nsd)
            return shift*round(x/shift,0)
  
    @staticmethod
    def bn2int(item):
        """
        converts BigNumber dict to int (if item is a BND; else returns item)

        :returns: int(item) if bn BigNumber dict, else item
        """
        #print("[bn2int]", item)
        if not isinstance(item, dict): return item
        if not item.get("type") == 'BigNumber': return item
        #print("[bn2int] isBn", item)
        return int(item["hex"], 16) 
        
    @classmethod
    def bn2intd(cls, dct):
        """
        converts dict with bignumber entries converted to int entries; other items remain
        """
        #print("[bn2intd]", dct)
        return {k:cls.bn2int(v) for (k,v) in dct.items()}

    @staticmethod
    def int2str(item):
        """
        converts all instances of int to str (if item is int; else returns item)
        """
        if isinstance(item, int): return str(item)
        return item

    @classmethod
    def int2strd(cls, dct):
        """
        converts all instances of int to str in dict; other items remain
        """
        return {k:cls.int2str(v) for (k,v) in dct.items()}

    @staticmethod
    def int2bn(i):
        """
        converts int (or float) to bignumber dict
        """
        return {"type": "BigNumber", 'hex': hex(int(i))}
    
    @staticmethod
    def str2floatd(dct):
        """
        converts all instances of str to float in dict; other items remain
        """
        return {k:float(v) if isinstance(v,str) else v for (k,v) in dct.items()}
