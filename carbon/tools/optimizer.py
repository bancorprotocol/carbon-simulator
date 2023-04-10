"""
object encapsulating various optimization methods, including convex optimization

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
__VERSION__ = "2.0"
__DATE__ = "10/Apr/2023"

from dataclasses import dataclass, field, asdict, astuple, InitVar
import pandas as pd
import numpy as np
import cvxpy as cp
import time
import math
import numbers
from .cpc import ConstantProductCurve as CPC, CPCInverter, CPCContainer 
from sys import float_info


class _DCBase():
    """base class for all data classes, adding some useful methods"""

    @property
    def asdict(self):
        return asdict(self)
    
    @property
    def astuple(self):
        return astuple(self)    

@dataclass
class ScaledVariable(_DCBase):
    """
    wraps a cvxpy variable to allow for scaling
    """
    variable: cp.Variable
    scale: any = 1.0
    token: list = None

    def __post_init__(self):
        try:
            len_var = len(self.variable.value)
        except TypeError as e:
            print("[ScaledVariable] variable.value is None", self.variable)
            return
        
        if not isinstance(self.scale, numbers.Number):
            self.scale = np.array(self.scale)
            if not len(self.scale) == len_var:
                raise ValueError("scale and variable must have same length or scale must be a number", self.scale, self.variable.value)
        if not self.token is None:
            if not len(self.token) == len_var:
                raise ValueError("token and variable must have same length", self.token, self.variable.value)
    
    @property
    def value(self):
        """
        converts value from USD to token units*
        
        Note: with scaling, the calculation is set up in a way that the values of the raw variables
        dx, dy correspond approximately to USD numbers, so their relative scale is natural and only 
        determined by the problem, not by units.

        The scaling factor is the PRICE in USD PER TOKEN, therefore

            self.variable.value = USD value of the token
            self.variable.value / self.scale = number of tokens
        """
        try:
            return np.array(self.variable.value) / self.scale
        except Exception as e:
            print("[value] exception", e, self.variable.value, self.scale)
            return self.variable.value
    
    @property
    def v(self):
        """alias for variable"""
        return self.variable
        

class OptimizerBase:
    """
    base class for all optimizers

    :problem:   the problem object (eg allowing to read `problem.status`)
    :result:    the return value of problem.solve
    :time:      the time it took to solve this problem (optional)
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    @dataclass
    class OptimizerResult(_DCBase):
        result: float
        time: float
        method: str = None

        def __post_init__(self):
            #print("[OptimizerResult] post_init")
            pass
            
        @property
        def status(self):
            """problem status"""
            raise NotImplementedError("must be implemented in derived class")
        
        @property
        def is_error(self):
            """True if problem status is not OPTIMAL"""
            raise NotImplementedError("must be implemented in derived class")
        
        def detailed_error(self):
            """detailed error analysis"""
            raise NotImplementedError("must be implemented in derived class")
        
        @property
        def error(self):
            """problem error"""
            if not self.is_error:
                return None
            return self.detailed_error()

    @dataclass
    class SimpleResult(_DCBase):
        result: float
        method: str = None
        errormsg: str = None
        context_dct: dict = None

        def __float__(self):
            if self.is_error:
                raise ValueError("cannot convert error result to float")
            return float(self.result)

        @property
        def is_error(self):
            return not self.errormsg is None
        
        @property
        def context(self):
            return self.context_dct if not self.context_dct is None else {}

    
    DERIVEPS = 1e-6
    @classmethod
    def deriv(cls, func, x):
        """
        computes the derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - func(x - h)) / (2 * h)
    
    @classmethod
    def deriv2(cls, func, x):
        """
        computes the second derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - 2 * func(x) + func(x - h)) / (h * h)
    
    @classmethod
    def findmin_gd(cls, func, x0, learning_rate=0.1, N=100):
        """
        finds the minimum of `func` using gradient descent starting at `x0`
        """
        x = x0
        for _ in range(N):
            x -= learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmin_gd")
    
    @classmethod
    def findmax_gd(cls, func, x0, learning_rate=0.1, N=100):
        """
        finds the maximum of `func` using gradient descent, starting at `x0`
        """
        x = x0
        for _ in range(N):
            x += learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmax_gd")
    
    @classmethod
    def findminmax_nr(cls, func, x0, N=20):
        """
        finds the minimum or maximum of func using Newton Raphson, starting at x0
        """
        x = x0
        for _ in range(N):
            #print("[NR]", x, func(x), cls.deriv(func, x), cls.deriv2(func, x))
            try:
                x -= cls.deriv(func, x) / cls.deriv2(func, x)
            except Exception as e:
                return cls.SimpleResult(
                        result=None, 
                        errormsg=f"Newton Raphson failed: {e} [x={x}, x0={x0}]",
                        method="findminmax_nr"
                    )
        return cls.SimpleResult(result=x, method="findminmax_nr")
    findmin = findminmax_nr
    findmax = findminmax_nr
    
    GOALSEEKEPS = 1e-6
    @classmethod
    def goalseek(cls, func, a, b):
        """
        finds the value of `x` where `func(x)` x is zero, using binary search between a,b
        """
        if func(a) * func(b) > 0:
            cls.SimpleResult(
                result=None, 
                errormsg=f"function must have different signs at a,b [{a}, {b}, {func(a)} {func(b)}]",
                method="findminmax_nr"
                )
            raise ValueError("function must have different signs at a,b")
        while (b - a) > cls.GOALSEEKEPS:
            c = (a + b) / 2
            if func(c) == 0:
                return c
            elif func(a) * func(c) < 0:
                b = c
            else:
                a = c
        return cls.SimpleResult(result=(a + b) / 2, method="findminmax_nr")

    @staticmethod
    def posx(vector):
        """
        returns the positive elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.maximum(0, vector)
        return tuple(max(0, x) for x in vector)
    
    @staticmethod
    def negx(vector):
        """
        returns the negative elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.minimum(0, vector)
        return tuple(min(0, x) for x in vector)
    
    @staticmethod
    def a(vector):
        """returns vector as np.array"""
        return np.array(vector)
    
    @staticmethod
    def t(vector):
        """returns vector as tuple"""
        return tuple(vector)

FORMATTER = lambda x: '' if ((abs(x) < 1e-10) or math.isnan(x)) else f'{x:,.2f}'

class CPCArbOptimizer(OptimizerBase):
    """
    main optimizer class for CPC arbitrage optimzisation
    """

    def __init__(self, curve_container):
        if not isinstance(curve_container, CPCContainer):
            curve_container = CPCContainer(curve_container)
        self.curve_container = curve_container

    @property
    def tokens(self):
        return self.curve_container.tokens

    @dataclass 
    class ConvexOptimizerResult(OptimizerBase.OptimizerResult):
        problem: cp.Problem = field(repr=False, default=None)

        def __post_init__(self):
            super().__post_init__()
            #print("[ConvexOptimizerResult] post_init")
            assert not self.problem is None, "problem must be set"
            if self.method is None:
                self.method = "convex"
        
        @property
        def status(self):
            """problem status"""
            return self.problem.status
        
        @property
        def is_error(self):
            """True if problem status is not OPTIMAL"""
            return self.status != cp.OPTIMAL or isinstance(self.result, str)
        
        @property
        def error(self):
            """problem error"""
            if not self.is_error:
                return None
            if isinstance(self.result, str):
                return f"{self.result} [{self.status}]"
            return f"{self.status}"

    @dataclass
    class NofeesOptimizerResult(ConvexOptimizerResult):
        """
        results of the nofees optimizer
        """
        token_table: dict = None
        sfc: any = field(repr=False, default=None) # SelfFinancingConstraints
        curves: CPCContainer = field(repr=False, default=None)
        curves_new: CPCContainer = field(repr=False,  default=None)
        dx: cp.Variable = field(repr=False, default=None)
        dy: cp.Variable = field(repr=False, default=None)

        def __post_init__(self):
            super().__post_init__()
            #print("[NofeesOptimizerResult] post_init")
            assert not self.token_table is None, "token_table must be set"
            assert not self.sfc is None, "sfc must be set"
            assert not self.curves is None, "curves must be set"
            #assert not self.curves_new is None, "curves_new must be set"
            assert not self.dx is None, "dx must be set"
            assert not self.dy is None, "dy must be set"
  
        def dxdydf(self, asdict=False, pretty=True, inclk=False):
            """returns dataframe with dx, dy per curve"""
            if inclk:
                dct = [
                    {"cid": c.cid, "pair": c.pair, "tknx": c.tknx, "tkny": c.tkny, 
                    "x": c.x, "y": c.y, "xa": c.x_act, "ya": c.y_act, "k": c.k, 
                    "kpost": (c.x+dxv)*(c.y+dyv), "kk": (c.x+dxv)*(c.y+dyv)/c.k, 
                    c.tknx: dxv, c.tkny: dyv}   
                    for dxv, dyv, c in zip(self.dx.value, self.dy.value, self.curves)
                ]
            else:
                dct = [
                {"cid": c.cid, "pair": c.pair, "tknx": c.tknx, "tkny": c.tkny, 
                "x": c.x, "y": c.y, "xa": c.x_act, "ya": c.y_act, "kk": (c.x+dxv)*(c.y+dyv)/c.k,
                c.tknx: dxv, c.tkny: dyv}   
                for dxv, dyv, c in zip(self.dx.value, self.dy.value, self.curves)
                ]
            if asdict:
                return dct
            df = pd.DataFrame.from_dict(dct).set_index("cid")
            df0 = df.fillna(0)
            dfa = df0[df0.columns[8:]].sum().to_frame(name="total").T
            dff = pd.concat([df, dfa], axis=0)
            if pretty:
                try:
                    dff = dff.style.format({col: FORMATTER for col in dff.columns[3:] })
                except Exception as e:
                    print("[dxdydf] exception", e, dff.columns)
            return dff
                

    @dataclass
    class SelfFinancingConstraints(_DCBase):
        """
        describes self financing constraints and determines optimization variable

        :data:      a dict TKN -> amount, or AMMPays, AMMReceives
                    :amount:        from the AMM perspective, total inflows (>0) or outflows (<0)
                                    for all items not present in data the value is assumed zero
                    :AMMPays:       the AMM payout should be maximized [from the trader (!) perspective]
                    :AMMReceives:   the money paid into the AMM should be minimized [ditto]
        :tokens:    set of all tokens in the problem (if None, use data.keys())

        """
        AMMPays = "AMMPays"
        AMMReceives = "AMMReceives"

        data: dict
        tokens: set = None

        def __post_init__(self):
            optimizationvars = tuple(k for k,v in self.data.items() 
                                      if v in {self.AMMPays, self.AMMReceives})
            assert len(optimizationvars) == 1, f"there must be EXACTLY one AMMPays, AMMReceives {self.data}"
            self._optimizationvar = optimizationvars[0]
            if self.tokens is None:
                self.tokens = set(self.data.keys()) 
            else:
                if isinstance(self.tokens, str):
                    self.tokens = set(t.strip() for t in self.tokens.split(","))
                else:
                    self.tokens = set(self.tokens)
                assert set(self.data.keys()) - self.tokens == set(), f"constraint keys {set(self.data.keys())} > {self.tokens}"

        @property
        def optimizationvar(self):
            """optimization variable, ie the in that is set to AMMPays or AMMReceives"""
            return self._optimizationvar
        
        @property
        def tokens_s(self):
            """tokens as a comma-separated string"""
            return ", ".join(self.tokens_l)
        
        @property
        def tokens_l(self):
            """tokens as a list"""
            return sorted(list(self.tokens))
        
        def asdict(self, short=False):
            """dict representation including zero-valued tokens (unless short)"""
            if short:
                return {**self.data}
            return {k: self.get(k) for k in self.tokens}
        
        def items(self, short=False):
            return self.asdict(short).items()

        @classmethod
        def new(cls, tokens, **data):
            """alternative constructor with data as kwargs"""
            return cls(data=data, tokens=tokens)
        
        def get(self, item):
            """gets the constraint, or 0 if not present"""
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return self.data.get(item, 0)
 
        def is_constraint(self, item):
            """
            returns True iff item is a constraint (ie not an optimisation variable)
            """
            return not self.is_optimizationvar(item)

        def is_optimizationvar(self, item):
            """
            returns True iff item is the optimization variable
            """
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return item == self.optimizationvar

        def __call__(self, item):
            """alias for get"""
            return self.get(item)
    
    def SFC(self, **data):
        """alias for SelfFinancingConstraints.new"""
        return self.SelfFinancingConstraints.new(self.curve_container.tokens(), **data)
    
    def SFCd(self, data_dct):
        """alias for SelfFinancingConstraints.new, with data as a dict"""
        return self.SelfFinancingConstraints.new(self.curve_container.tokens(), **data_dct)
    
    AMMPays = SelfFinancingConstraints.AMMPays
    AMMReceives = SelfFinancingConstraints.AMMReceives

    SOLVER_ECOS = "ECOS"
    SOLVER_SCS = "SCS"
    SOLVER_OSQP = "OSQP"
    SOLVER_CVXOPT = "CVXOPT"
    SOLVER_CBC = "CBC"
    SOLVERS = {
        SOLVER_ECOS: cp.ECOS,
        SOLVER_SCS: cp.SCS,
        SOLVER_OSQP: cp.OSQP,
        SOLVER_CVXOPT: cp.CVXOPT,
        SOLVER_CBC: cp.CBC,
        
        # those solvers will usually have to be installed separately
        "ECOS_BB": cp.ECOS_BB,
        "OSQP": cp.OSQP,
        "GUROBI": cp.GUROBI,
        "MOSEK": cp.MOSEK,
        "GLPK": cp.GLPK,
        "GLPK_MI": cp.GLPK_MI,
        "CPLEX": cp.CPLEX,
        "XPRESS": cp.XPRESS,
        "SCIP": cp.SCIP,
        
    }

    def nofees_optimizer(self, sfc, **params):
        """
        convex optimization for determining the arbitrage opportunities

        :sfc:       a SelfFinancingConstraints object
        :params:    additional parameters to be passed to the solver
                    :verbose:       if True, generate verbose output
                    :solver:        the solver to be used (default: "CVXOPT"; see SOLVERS)
                    :nosolve:       if True, do not solve the problem, but return the problem object
                    :nominconstr:   if True, do NOT add the minimum constraints
                    :maxconstr:     if True, DO add the (reundant) maximum constraints
                    :retcurves:     if True, also return the curves object (default: False)
                    :s_xxx:         pass the parameter `xxx` to the solver (eg s_verbose)    
                    :s_verbose:     if True, generate verbose output from the solver


        note: CVXOPT is a pip install (pip install cvxopt); OSQP is not suitable for this problem,
        ECOS and SCS do work sometimes but can go dramatically wrong   
        """

        # This code runs the actual optimization. It has two major parts

        # 1. the **constraints**, and 
        # 2. the **objective function** to be optimized (min or max)

        # The objective function is to either maximize the number of tokens
        # received from the AMM (which is a negative number, hence formally the
        # condition is `cp.Minimize` or to minimize the number of tokens paid to
        # the AMM which is a positive number. Therefore `cp.Minimize` is the
        # correct choice in each case.

        # The constraints come in three types:

        # - **curve constraint**: the curve constraints correspond to the
        #   $x\cdot y=k$ invariant of the respective AMM; the constraint is
        #   formally `>=` but it has been shown eg by Angeris et al that the
        #   constraint will always be optimal on the boundary

        # - **range constraints**: the range constraints correspond to the
        #   tokens actually available on curve; for the full-curve AMM those
        #   constraints would formally be `dx >= -c.x` and the same for `y`, but
        #   those constraint are automatically fulfilled because of the
        #   asymptotic behaviour of the curves so could be omitted

        # - **self-financing constraints**: the self-financing constraints
        #   corresponds to the condition that all `dx` and `dy` corresponding to
        #   a specific token other than the token in the objective function must
        #   sum to the target amount provided in `inputs` (or zero if not
        #   provided)
        
        
        curves_t = self.curve_container.curves
        c0 = curves_t[0]
        tt = self.curve_container.tokentable()
        prtkn = sfc.optimizationvar

        P = lambda x: params.get(x)
        
        start_time = time.time()

        # set up the optimization variables
        if P("verbose"):
            print(f"Setting up dx[0..{len(curves_t)-1}] and dy[0..{len(curves_t)-1}]")
        dx = cp.Variable(len(curves_t), value=[0]*len(curves_t))
        dy = cp.Variable(len(curves_t), value=[0]*len(curves_t))

        # the geometric mean of objects in a list
        gmean = lambda lst: cp.geo_mean(cp.hstack(lst))
       
        ## assemble the constraints...
        constraints = []

        # curve constraints
        for i, c in enumerate(curves_t):
            constraints += [gmean([c.x+dx[i]/c.scalex, c.y+dy[i]/c.scaley]) >= c.kbar]
            if P("verbose"):
                print(f"CC {i} [{c.cid}]: {c.pair} x={c.x:.1f} {c.tknx } (s={c.scalex}), y={c.y:.1f} {c.tkny} (s={c.scaley}), k={c.k:2.1f}, p_dy/dx={c.p:2.1f}, p_dx/dy={1/c.p:2.1f}")
                
        if P("verbose"):
            print("number of constraints: ", len(constraints))
        
        # range constraints (min)
        for i, c in enumerate(curves_t):

            pass
            
            if not P("nominconstr"):
                constraints += [
                    dx[i]/c.scalex >= c.dx_min,
                    dy[i]/c.scaley >= c.dy_min,
                ]            
                if P("verbose"):
                    print(f"RC {i} [{c.cid}]: dx>{c.dx_min:.4f} {c.tknx} (s={c.scalex}), dy>{c.dy_min:.4f} {c.tkny} (s={c.scaley}) [{c.pair}]")

            if P("maxconstr"):
                if not c.dx_max is None:
                    constraints += [
                        dx[i]/c.scalex <= c.dx_max,
                    ]
                if not c.dy_max is None:
                    constraints += [
                        dy[i]/c.scaley <= c.dy_max,
                    ]            
                if P("verbose"):
                    print(f"RC {i} [{c.cid}]: dx<{c.dx_max} {c.tknx} (s={c.scalex}), dy<{c.dy_max} {c.tkny} (s={c.scaley}) [{c.pair}]")
        
        
        if P("verbose"):
            print("number of constraints: ", len(constraints))
        
            
        # self-financing constraints
        for tkn, tknvalue in sfc.items():
            if not isinstance(tknvalue, str):
                constraints += [
                    cp.sum([dy[i] for i in tt[tkn].y])+cp.sum([dx[i] for i in tt[tkn].x]) == tknvalue*c0.scale(tkn)
                        # note: we can access the scale from any curve as it is a class method
                ]
                if P("verbose"):
                    print(f"SFC [{tkn}={tknvalue}, s={c0.scale(tkn)}]: y={[i for i in tt[tkn].y]}, x={[i for i in tt[tkn].x]}")
        
        if P("verbose"):
            print("number of constraints: ", len(constraints))

        # objective function  (note: AMM out is negative, AMM in is positive)
        if P("verbose"):
            print(f'O: y={[i for i in tt[prtkn].y]}, x={[i for i in tt[prtkn].x]}, {prtkn}')
                
        objective = cp.Minimize(
            cp.sum([dy[i] for i in tt[prtkn].y])+cp.sum([dx[i] for i in tt[prtkn].x])
        )

        # run the optimization
        problem = cp.Problem(objective, constraints)
        solver = self.SOLVERS.get(P("solver"), cp.CVXOPT)
        if not P("nosolve"):
            sp = {k[2:]:v for k,v in params.items() if k[:2]=="s_"}
            print("Solver params:", sp)
            if(P("verbose")):
                print(f"Solving the problem with {solver}...")
            try:
                problem_result = problem.solve(solver=solver, **sp)
                #problem_result = problem.solve(solver=solver)
            except cp.SolverError as e:
                if P("verbose"):
                    print(f"Solver error: {e}")
                problem_result = str(e)
            if P("verbose"):
                print(f"Problem solved in {time.time()-start_time:.2f} seconds; result: {problem_result}")
        else:
            problem_result = None
        
        dx_=ScaledVariable(dx, [c.scalex for c in curves_t], [c.tknx for c in curves_t])
        dy_=ScaledVariable(dy, [c.scaley for c in curves_t], [c.tkny for c in curves_t])
            
        return self.NofeesOptimizerResult(
            problem=problem,
            sfc=sfc,
            result=problem_result,
            time=time.time()-start_time,
            dx=dx_,
            dy=dy_,
            token_table=tt,
            curves=self.curve_container,
            curves_new=self.adjust_curves(dxvals = dx_.value),
        )
    
    SO_DXDYVECFUNC = "dxdyvecfunc"
    SO_DXDYSUMFUNC = "dxdysumfunc"
    SO_DXDYVALXFUNC = "dxdyvalxfunc"
    SO_DXDYVALYFUNC = "dxdyvalyfunc"
    SO_PMAX = "pmax"

    @dataclass
    class SimpleOptimizerResult(OptimizerBase.OptimizerResult):
        """
        results of the simple optimizer
        
        :curves:            list of curves used in the optimization, possibly wrapped in CPCInverter objects*
        :dxdyfromp_vec_f:   vector of tuples (dx, dy), as a function of p
        :dxdyfromp_sum_f:   sum of the above, also as a function of p
        :dxdyfromp_valx_f:  valx = dy/p + dx, also as a function of p
        :dxdyfromp_valy_f:  valy = dy + p*dx/p, also as a function of p
        :p_optimal:         optimal p value

        *the CPCInverter object ensures that all curves in the list correspond to the same quote
        conventions, according to the primary direction of the pair (as determined by the Pair
        object). Accordingly, tknx and tkny are always the same for all curves in the list, regardless
        of the quote direction of the pair. The CPCInverter object abstracts this away, but of course
        only for functions that are accessible through it.
        """
        NONEFUNC = lambda x: None

        curves: list = field(repr=False, default=None)
        dxdyfromp_vec_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_sum_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_valx_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_valy_f: any = field(repr=False, default=NONEFUNC)
        p_optimal: float = field(repr=False, default=None)
        errormsg: str = field(repr=False, default=None)

        def __post_init__(self):
            super().__post_init__()
            #print("[SimpleOptimizerResult] post_init")
            assert self.p_optimal is not None or self.errormsg is not None, "p_optimal must be set unless errormsg is set"
            if self.method is None:
                self.method = "simple"

        @property
        def is_error(self):
            return self.errormsg is not None
        
        def detailed_error(self):
            return self.errormsg
        
        def status(self):
            return "error" if self.is_error else "converged"

        def dxdyfromp_vecs_f(self, p):
            """returns dx, dy as separate vectors instead as a vector of tuples"""
            return tuple(zip(*self.dxdyfromp_vec_f(p)))

        @property
        def tknx(self):
            return self.curves[0].tknx
        
        @property
        def tkny(self):
            return self.curves[0].tkny
        
        @property
        def tknxp(self):
            return self.curves[0].tknxp
        
        @property
        def tknyp(self):
            return self.curves[0].tknyp
        
        @property
        def pair(self):
            return self.curves[0].pair
        
        @property
        def pairp(self):
            return self.curves[0].pairp

        @property
        def dxdy_vecs(self):
            return self.dxdyfromp_vecs_f(self.p_optimal)
        
        @property
        def dxvalues(self):
            return self.dxdy_vecs[0]
        dxv = dxvalues

        @property
        def dyvalues(self):
            return self.dxdy_vecs[1]
        dyv = dyvalues
        
        @property
        def dxdy_vec(self):
            return self.dxdyfromp_vec_f(self.p_optimal)
        
        @property
        def dxdy_sum(self):
            return self.dxdyfromp_sum_f(self.p_optimal)
        
        @property
        def dxdy_valx(self):
            return self.dxdyfromp_valx_f(self.p_optimal)
        valx = dxdy_valx
        
        @property
        def dxdy_valy(self):
            return self.dxdyfromp_valy_f(self.p_optimal)
        valy = dxdy_valy
        
        @property
        def status(self):
            return "converged"

        @property
        def is_error(self):
            return False

        @property
        def error(self):
            return None

    
    def simple_optimizer(self, result=None, params=None):
        """
        a simple optimizer that does not use cvxpy and the works only on curves on one pair

        :result:            determines what to return
                            :SO_DXDYVECFUNC:    function of p returning vector of dx,dy values 
                            :SO_DXDYSUMFUNC:    function of p returning sum of dx,dy values
                            :SO_DXDYVALXFUNC:   function of p returning value of dx,dy sum in units of tknx
                            :SO_DXDYVALYFUNC:   ditto tkny
        :params:            dict of parameters (not currently used)
        """
        start_time = time.time()
        curves_t = CPCInverter.wrap(self.curve_container)
        pairs = set(c.pair for c in curves_t)
        assert len(pairs)!=0, f"no pairs found, probably empty curves [{curves_t}]"
        assert len(pairs)==1, f"simple_optimizer only works on curves of one pair [{pairs}]"
        
        dxdy = lambda r: (np.array(r[0:2]))
        
        dxdyfromp_vec_f = lambda p: tuple(dxdy(c.dxdyfromp_f(p)) for c in curves_t)
        if result == self.SO_DXDYVECFUNC:
            return dxdyfromp_vec_f
        
        dxdyfromp_sum_f = lambda p: sum(dxdy(c.dxdyfromp_f(p)) for c in curves_t)
        if result == self.SO_DXDYSUMFUNC:
            return dxdyfromp_sum_f
        
        dxdyfromp_valy_f = lambda p: np.dot(dxdyfromp_sum_f(p), np.array([p,1]))
        if result == self.SO_DXDYVALYFUNC:
            return dxdyfromp_valy_f
        
        dxdyfromp_valx_f = lambda p: dxdyfromp_valy_f(p)/p
        if result == self.SO_DXDYVALXFUNC:
            return dxdyfromp_valx_f
        
        p_avg = np.mean([c.p for c in curves_t])
        p_optimal = self.findmax(dxdyfromp_valx_f, p_avg)
        if result == self.SO_PMAX:
            return p_optimal
        
        if p_optimal.is_error:
            return self.SimpleOptimizerResult(
                result = None,
                time=time.time()-start_time,
                curves=curves_t,
                dxdyfromp_vec_f=dxdyfromp_vec_f,
                dxdyfromp_sum_f=dxdyfromp_sum_f,
                dxdyfromp_valx_f=dxdyfromp_valx_f,
                dxdyfromp_valy_f=dxdyfromp_valy_f,
                p_optimal=None,
                errormsg = p_optimal.errormsg,
        )
        return self.SimpleOptimizerResult(
            result = dxdyfromp_valx_f(float(p_optimal)),
            time=time.time()-start_time,
            curves=curves_t,
            dxdyfromp_vec_f=dxdyfromp_vec_f,
            dxdyfromp_sum_f=dxdyfromp_sum_f,
            dxdyfromp_valx_f=dxdyfromp_valx_f,
            dxdyfromp_valy_f=dxdyfromp_valy_f,
            p_optimal=float(p_optimal),
        )

    def adjust_curves(self, dxvals, verbose=False, raiseonerror=False):
        """
        returns a new curve container with the curves shifted by the given dx values
        """
        #print("[adjust_curves]", dxvals)
        if dxvals is None:
            if raiseonerror:
                raise ValueError("dxvals is None")
            else:
                print("[adjust_curves] dxvals is None")
                return None
        curves = self.curve_container
        try:
            newcurves = [c.execute(dx=dx, verbose=verbose, ignorebounds=True) for c, dx in zip(curves, dxvals)]
            return CPCContainer(newcurves)
        except Exception as e:
            if raiseonerror:
                raise e
            else:
                print(f"Error in adjust_curves: {e}")
                #raise e
                return None
    
def F(func, rg):
    """helper: returns list of [func(x) for x in rg]"""
    return [func(x) for x in rg]
    

    