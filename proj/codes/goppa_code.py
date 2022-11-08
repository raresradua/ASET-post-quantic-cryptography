from proj.codes.linear_code import LinearCode
from galois import GF
import numpy as np


class GoppaCode(LinearCode):
    def __init__(self, n, k, d, code=None, m=2, t=3, p=2):
        super().__init__(code)
        if code:
            self.m = m
            self.F = GF(p ^ m)
            self.t = t
            self.L = []
            self.g_factors = []
            self.code = self.generate_code()
            print("Generated Code: ", self.code)
        else:
            self.code = code

    def accept_code(self, n, k, d):
        if k < n - self.m * self.t:
            return False
        if d < 2 * self.t:
            return False
        return True

    def get_parity_check_matrix(self):
        return self.code.parity_check_matrix()

    def generate_code(self):
        g = self.generate_goppa_polynomial_v1()
        self.poly = g
        L = [a for a in self.F.list() if g(a) != 0]
        return self.code.GoppaCode(g, L)

    def generate_goppa_polynomial_v1(self):
        # TBD: we do not need this anymore because we implement g function
        # the poly is irreducible when accept_code function returns True and that is an Goppa code
        PolyRing = PolynomialRing(self.F, 'x')
        return PolyRing.irreducible_element(self.t)

    def g(self, value):
        if len(self.g_factors) == 0:
            i = 0
            while i < self.t:
                g = self.F.random_element()
                self.g_factors.append(g)
                i = i + 1
        sum = 0
        for i in range(self.t):
            sum = sum + self.g_factors[i] * (value ** i)
        return sum

    def determine_L_set(self, n):
        i = 0
        while 1:
            alpha = self.F.random_element()
            if self.g(alpha):
                if i < n:
                    self.L.append(alpha)
                    i = i + 1
                else:
                    break
