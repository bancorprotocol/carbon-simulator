"""
Carbon helper module -- solidity tests
"""
__VERSION__ = "1.0"
__DATE__ = "11/Feb/2023"

from math import sqrt as _sqrt, ceil as _ceil, log2 as _log2

class SolTestBase():
    """
    testing the solidity curve implementation

    :print_lvl:         the minimum level to be printed (default: LVL_WARN)
    :raise_lvl:         the minimum level where to raise (default: LVL_NEVER)
    :store_lvl:         the minimum level where to store (default: LVL_NEVER)
    :print_context:     whether or not to print the context provided
    :**kwargs:          all go into the `self.context` dict

    *use constants LVL_LOG, LVL_WARN, LVL_ERR, LVL_NEVER 
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    
    def __init__(self, print_lvl=None, raise_lvl=None, store_lvl=None, print_context=False, **kwargs):
        if print_lvl is None: print_lvl = self.PRINT_LVL_DEFAULT
        if raise_lvl is None: raise_lvl = self.RAISE_LVL_DEFAULT
        if store_lvl is None: store_lvl = self.STORE_LVL_DEFAULT
        self.print_lvl      = print_lvl
        self.raise_lvl      = raise_lvl
        self.store_lvl      = store_lvl
        self.print_context  = print_context
        self.context        = kwargs
        
    class OutOfBoundsError(Exception): pass
    class OverflowError(OutOfBoundsError): pass
    class UnderflowError(OutOfBoundsError): pass

    class OutOfBoundsWarning(Exception): pass
    class OverflowWarning(OutOfBoundsWarning): pass
    class UnderflowWarning(OutOfBoundsWarning): pass

    UINT256MAX = 1<<256
    UINT256MAX1 = UINT256MAX-1

    @staticmethod
    def bindig(num):
        """binary digits for num >0 [_ceil(_log2(num+1))]"""
        return _ceil(_log2(num+1))
    
    LVL_LOG     = 0
    LVL_WARN    = 1
    LVL_ERR     = 2
    LVL_NEVER   = 9

    PRINT_LVL_DEFAULT = LVL_WARN
    RAISE_LVL_DEFAULT = LVL_NEVER
    STORE_LVL_DEFAULT = LVL_NEVER
    

    LEVELS = {
        LVL_LOG:    "LOG",
        LVL_WARN:   "WARNING",
        LVL_ERR:    "ERROR", 
    }

    _EXCEPTIONS = {
        True: {
            LVL_WARN: OverflowWarning,
            LVL_ERR: OverflowError,
        },
        False: {
            LVL_WARN: UnderflowWarning,
            LVL_ERR: UnderflowError,
        }
    }
    @classmethod
    def _logmsg(cls, level, isoverflow, label, msg):
        """
        composes and error or warning message
        """
        we = cls.LEVELS[level]
        if level == cls.LVL_LOG: uo = "OK"
        else: uo = "OVERFLOW" if isoverflow else "UNDERFLOW"
        return f"[{we}:{uo}:{label.upper()}] {msg}"

    def store_f(self, level, isoverflow, label, msg, context):
        """stores the event"""
        if level < self.store_lvl: return
        raise NotImplementedError("store_f not implemented yet")

    def raise_f(self, level, isoverflow, label, msg=None, context=None):
        """raises the appropriate exception on errors and warnings"""
        if level < self.raise_lvl: return
        exception = self._EXCEPTIONS[isoverflow][level]
        logmsg = self._logmsg(level, isoverflow, label, msg)
        raise exception(logmsg, self.context, context)
        
    def print_f(self, level, isoverflow, label, msg=None, context=None):
        """prints the appropriate message"""
        if level < self.print_lvl: return
        logmsg = self._logmsg(level, isoverflow, label, msg)
        if self.print_context:
            print(logmsg, self.context, context)
        else:
            print (logmsg)

    def print_raise_f(self, level, isoverflow, label=None, msg=None, context=None):
        """calls print_f first, then raise_f"""
        self.print_f(level, isoverflow, label, msg, context)
        self.raise_f(level, isoverflow, label, msg, context)
        
    UNDERFLOW_ERR  = 100
    UNDERFLOW_WARN = 10000
    OVERFLOW_ERR   = UINT256MAX
    OVERFLOW_WARN  = OVERFLOW_ERR/UNDERFLOW_WARN
    
    def check_uint256(self, number, label=None, context=None, log_f=None):
        """
        checks number for uint256 bounds

        :number:    the number to be checked (cast to int)
        :label:     the label associated with this number
        :context:   other context information associated with this number
        :log_f:     the function to call on error (None: raise)
        :returns:   the number as int in the uint256 range
        """
        number = int(number)
        if log_f is None: log_f = self.print_raise_f
        if label is None: label = ""
        d = self.bindig
        
        if number < 0:
            log_f(level=self.LVL_ERR, isoverflow=True, label=label, msg=f"number < 0", context=context)
            return 0
        elif number < self.UNDERFLOW_ERR:
            log_f(level=self.LVL_ERR, isoverflow=False, label=label, msg=f"{d(number)} bits: < underflow threshold", context=context)
        elif number < self.UNDERFLOW_WARN:
            log_f(level=self.LVL_WARN, isoverflow=False, label=label, msg=f"{d(number)} bits: underflow warning", context=context)
        elif number >= self.OVERFLOW_ERR:
            log_f(level=self.LVL_ERR, isoverflow=True, label=label, msg=f"{d(number)} bits: > max", context=context)
        elif number >= self.OVERFLOW_WARN:
            log_f(level=self.LVL_WARN, isoverflow=True, label=label, msg=f"{d(number)} bits: close to max", context=context)
        else:
            log_f(level=self.LVL_LOG, isoverflow=False, label=label, msg=f"{d(number)} bits: ok", context=context)
        return number

    def __call__(self, number, label=None, context=None):
        """alias for check_uint256 with log_f = default"""
        return self.check_uint256(number, label, context)

        