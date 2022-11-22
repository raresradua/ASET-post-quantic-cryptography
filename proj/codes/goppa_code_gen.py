from linear_code import LinearCode
import galois
import numpy as np
from sympy import Matrix, randMatrix, zeros
from sympy.abc import x, alpha
import random as rand
from sympy.polys.galoistools import gf_gcdex
from sympy.polys.domains import ZZ


def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(
            lastremainder, remainder)
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)


def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


class GoppaCode:
    def __init__(self, m=2, t=3, base_field=2, n=12, k=10):
        self.m = m
        self.t = t
        self.n = n
        self.base_field = base_field
        self.val = base_field ** m
        self.k = k
        self.F = galois.GF(base_field ** m)
        self.g = galois.irreducible_poly(self.F.order, self.t, 'random')
        self.coefficients = self.g.coefficients(self.t + 1, 'asc')
        self.H = self.get_parity_check_matrix()
        self.G = self.get_generator_matrix()

        print(self.H)
        print(self.G)

    def get_parity_check_matrix(self):
        alpha_set = []
        while len(alpha_set) < self.n:
            element = rand.randint(0, self.val)
            if int(self.g(element)) % int(self.val) != 0 and modinv(int(self.g(element)) % int(self.val),
                                                                    int(self.val)) is not None:
                alpha_set.append(element)

        X = Matrix(self.t, self.t, lambda i, j: int(
            self.coefficients[j - i]) if 0 <= i - j < self.t else 0)
        Y = Matrix(self.t, self.n, lambda i, j: (alpha_set[j] ** i) % self.val)
        Z = Matrix(self.n, self.n,
                   lambda i, j: modinv(int(self.g(alpha_set[i])) % int(self.val), int(self.val)) if i == j else 0)
        H = X * Y * Z
        H = Matrix(H.shape[0], H.shape[1], lambda i, j: H[i, j] % self.val)
        self.H = H
        return H

    def get_generator_matrix(self):
        H_bin = Matrix(self.H.shape[0], self.H.shape[1], lambda i, j: self.H[i, j] % 2)
        G = []
        for i in range(len(H_bin.nullspace())):
            vec = []
            for j in range(len(H_bin.nullspace()[i])):
                vec.append(H_bin.nullspace()[i][j])
            G.append(vec)

        G = Matrix(G)
        return G


obj = GoppaCode(13, 13, 2, 12)
