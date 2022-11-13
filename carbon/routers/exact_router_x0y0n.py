"""
Exact-method router class using the x0, y0, n variables.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
from .exact_base_router import *


@dataclass
class ExactRouterX0Y0N(ExactBase):
    """
    Main class to handle the exact routing mothod. This method determines the ideal distribution of the input
    amount to arrive at **the** theoretical best price that can be obtained for a given set of orders.

    There are two versions of the exact method, which are equivilent in terms of the output, but differ in terms of
    variables used throughout. This version uses the x0, y0, n variables - which are not used in the smart-contract
    implementation or in the other simulator class ExactRouterSBY.
    """

    def amt_by_src(
        self, subject: int, dx: DecFloatInt, position_subset: List[int]
    ) -> DecFloatInt:
        """
        Calculates the liquidity amount change [delta-y] for y, via contributing delta-x (dx)
        """
        sub = self.orders[subject]
        n_sub, x0_sub, y_sub, y0_sub, x_sub, k_sub, a = (
            sub.n,
            sub.x0,
            sub.y,
            sub.y0,
            sub.x,
            sub.k,
            sub.a,
        )
        collections = self.handle_subfunctions_src(subject, position_subset, dx)
        b = self.b_src(x_sub, n_sub, x0_sub, k_sub, collections)
        e = collections["e_src"]
        f = collections["f_src"]

        self.logger.debug(
            "amt_by_src: a=%s, b=%s, e=%s, f=%s",
            self.frmt(a),
            self.frmt(b),
            self.frmt(e),
            self.frmt(f),
        )
        return (
            a**2 * b / (x0_sub * (a * b * n_sub + k_sub * x0_sub * (e * n_sub + f)))
        )

    def amt_by_target(
        self, subject: int, dx: DecFloatInt, position_subset: List[int]
    ) -> DecFloatInt:
        """
        Calculates the liquidity amount change [delta-y] for y, via contributing delta-x (dx)
        """
        sub = self.orders[subject]
        n, x0, y, y0, x, k, a_sub = (
            sub.n,
            sub.x0,
            sub.y,
            sub.y0,
            sub.x,
            sub.k,
            sub.a,
        )
        collections = self.handle_subfunctions_target(subject, position_subset)
        a = collections["a_target"]
        b = collections["b_target"]
        c = collections["c_target"]
        d = -(n * y + y0 * (1 - n))
        e = collections["e_target"]
        self.logger.debug(
            "amt_by_target: a=%s, b=%s, c=%s, d=%s, e=%s",
            self.frmt(a),
            self.frmt(b),
            self.frmt(c),
            self.frmt(d),
            self.frmt(e),
        )
        return (x0 * y0 * (a * (b + dx) + c) + d * e) / (n * e + x0 * y0 * a)

    def handle_subfunctions_src(
        self, subject: int, position_subset: List[int], amt: DecFloatInt
    ) -> dict:
        """
        Subfunction calculations for "c", "e", "f", "g" variables in the dy_by_src equation.
        """
        subject_free_indexes = [i for i in position_subset if i != subject]
        n, e_src, c_src, g_src = [], [], [], [-amt]
        for i in subject_free_indexes:
            n += [self.orders[i].n]
            g_src += [self.orders[i].x0]
            g_src += [-self.orders[i].x]
            n_collection, rs = [], {}
            sub_list = [j for j in subject_free_indexes if j != i]
            for j in sub_list:
                n_collection += [self.orders[j].n]
            e_src += [
                self.prod(n_collection)
                * Decimal.sqrt(self.orders[subject].k * self.orders[i].k)
            ]
            c_src += [self.prod(n_collection) * self.orders[i].x0]
        return {
            "c_src": sum(c_src),
            "e_src": sum(e_src),
            "f_src": self.orders[subject].k * self.prod(n),
            "g_src": sum(g_src),
        }

    def handle_subfunctions_target(
        self, subject: int, position_subset: List[int]
    ) -> dict:
        """
        Subfunction calculations for "a", "b", "c", "e" variables in the dy_by_target equation.
        """
        subject_free_indexes = [i for i in position_subset if i != subject]
        n_observers = [self.orders[i].n for i in subject_free_indexes]
        y_observers = [self.orders[i].y for i in subject_free_indexes]
        y0_observers = [self.orders[i].y0 for i in subject_free_indexes]
        rotation_sets = {}
        for j in subject_free_indexes:
            n_elements = [self.orders[k].n for k in subject_free_indexes if k != j]
            rotation_sets[j] = {
                "n_elements": n_elements,
                "x0_element": self.orders[j].x0,
                "y0_element": self.orders[j].y0,
            }
        x0, y0, y = (
            self.orders[subject].x0,
            self.orders[subject].y0,
            self.orders[subject].y,
        )
        return {
            "a_target": self.prod(n_observers),
            "b_target": sum(y_observers) - sum(y0_observers),
            "c_target": sum(
                [
                    self.prod(rotation_sets[i]["n_elements"])
                    * rotation_sets[i]["y0_element"]
                    for i in rotation_sets
                ]
            ),
            "e_target": sum(
                [
                    self.prod(rotation_sets[i]["n_elements"])
                    * Decimal.sqrt(
                        rotation_sets[i]["x0_element"]
                        * rotation_sets[i]["y0_element"]
                        * x0
                        * y0
                    )
                    for i in rotation_sets
                ]
            ),
        }

    def b_src(
        self,
        x: DecFloatInt,
        n: DecFloatInt,
        x0: DecFloatInt,
        k: DecFloatInt,
        collections: dict,
    ) -> DecFloatInt:
        """
        Subfunction calculation for "b" variable in the dy_by_src equation.
        """
        e = collections["e_src"]
        f = collections["f_src"]
        g = collections["g_src"]
        c = collections["c_src"]
        d = -n * x0 + n * x + x0
        self.logger.debug(
            "b_src: x=%s, n=%s, x0=%s, k=%s, e=%s, f=%s, g=%s, c=%s, d=%s",
            self.frmt(x),
            self.frmt(n),
            self.frmt(x0),
            self.frmt(k),
            self.frmt(e),
            self.frmt(f),
            self.frmt(g),
            self.frmt(c),
            self.frmt(d),
        )
        return -c * k + d * e + f * g
