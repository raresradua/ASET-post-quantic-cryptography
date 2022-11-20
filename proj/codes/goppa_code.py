from linear_code import LinearCode
import galois
from sympy import Matrix
import random as rand
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect


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


class BinaryGoppaCode(LinearCode):

    def __init__(self, m, t, n, k):
        if k >= n - m * t:
            self.m = m
            self.t = t
            self.n = n
            self.base_field = 2
            self.val = 2 ** m
            self.k = k
            self.F = galois.GF(2 ** m)
            self.g = galois.irreducible_poly(self.F.order, self.t, 'random')
            self.coefficients = self.g.coefficients(self.t + 1, 'asc')
            self.H = self.get_parity_check_matrix()
            self.G = self.get_generator_matrix()
            super().__init__(n, k, self)
        else:
            print("Invalid arguments ! ")

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_parity_check_matrix(self):
        alpha_set = []
        while len(alpha_set) < self.n:
            element = rand.randint(0, self.val)
            if int(self.g(element)) % int(self.val) != 0 and modinv(int(self.g(element)) % int(self.val),
                                                                    int(self.val)) is not None:
                alpha_set.append(element)

        x_matrix = Matrix(self.t, self.t, lambda i, j: int(
            self.coefficients[j - i]) if 0 <= i - j < self.t else 0)
        y_matrix = Matrix(self.t, self.n, lambda i, j: (alpha_set[j] ** i) % self.val)
        z_matrix = Matrix(self.n, self.n, lambda i, j: modinv(
            int(self.g(alpha_set[i])) % int(self.val), int(self.val)) if i == j else 0)
        h_matrix = x_matrix * y_matrix * z_matrix
        h_matrix = Matrix(h_matrix.shape[0], h_matrix.shape[1], lambda i, j: h_matrix[i, j] % self.val)
        return h_matrix

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_generator_matrix(self):
        if self.H is not None:
            h_bin = Matrix(self.H.shape[0], self.H.shape[1], lambda i, j: self.H[i, j] % 2)
            g_matrix = []
            for i in range(len(h_bin.nullspace())):
                vec = []
                for j in range(len(h_bin.nullspace()[i])):
                    vec.append(h_bin.nullspace()[i][j])
                g_matrix.append(vec)
            g_matrix = Matrix(g_matrix)
            return g_matrix
        else:
            return None

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def error_correction(self, codeword):
        return None

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return None


obj = BinarryGoppaCode(13, 13, 12, 10)
