from linear_code import LinearCode
import galois
from sympy import Matrix, symbols
import random as rand
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
import logging

logger = logging.getLogger()


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
        logger.info('[INFO] Calling __init__ for GoppaCode')
        try:
            assert k >= n - m * t
        except Exception:
            logger.error('[ERROR] Invalid arguments.')
        else:
            logger.info('[INFO] Arguments are alright.')
            self.m = m
            self.t = t
            self.n = n
            self.base_field = 2
            self.val = 2 ** m
            self.k = k
            self.F = galois.GF(2 ** m)
            self.g = galois.irreducible_poly(self.F.order, self.t, 'random')
            self.coefficients = self.g.coefficients(self.t + 1, 'asc')
            self.alpha_set = self.get_alpha_set()
            self.H = self.get_parity_check_matrix()
            self.G = self.get_generator_matrix()
            self.syndrome_polynom = self.get_syndrome_polynom([1] * self.n)
            self.error_correction([1] * self.n)

            super().__init__(n, k, self)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_alpha_set(self):
        logger.info('[INFO] Calling get_alpha_set')
        alpha_set = []
        while len(alpha_set) < self.n:
            element = rand.randint(0, self.val)
            if int(self.g(element)) % int(self.val) != 0 and modinv(int(self.g(element)) % int(self.val),
                                                                    int(self.val)) is not None:
                alpha_set.append(element)
        logger.info('[INFO] Alpha set value: {}'.format(alpha_set))
        return alpha_set

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_parity_check_matrix(self):
        logger.info('[INFO] Calling get_parity_check_matrix')
        x_matrix = Matrix(self.t, self.t, lambda i, j: int(
            self.coefficients[j - i]) if 0 <= i - j < self.t else 0)
        y_matrix = Matrix(self.t, self.n, lambda i, j: (self.alpha_set[j] ** i) % self.val)
        z_matrix = Matrix(self.n, self.n, lambda i, j: modinv(
            int(self.g(self.alpha_set[i])) % int(self.val), int(self.val)) if i == j else 0)
        h_matrix = x_matrix * y_matrix * z_matrix
        h_matrix = Matrix(h_matrix.shape[0], h_matrix.shape[1], lambda i, j: h_matrix[i, j] % self.val)
        logger.info('[INFO] Parity check matrix: {}'.format(h_matrix))
        return h_matrix

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_generator_matrix(self):
        logger.info('[INFO] Calling get_generator_matrix')
        try:
            assert self.H
        except Exception:
            logger.error('[ERROR] Parity check matrix not computed.')
            return None
        else:
            logger.info('[INFO] Everything is alright.')
            h_bin = Matrix(self.H.shape[0], self.H.shape[1], lambda i, j: self.H[i, j] % 2)
            g_matrix = []
            for i in range(len(h_bin.nullspace())):
                vec = []
                for j in range(len(h_bin.nullspace()[i])):
                    vec.append(h_bin.nullspace()[i][j])
                g_matrix.append(vec)
            g_matrix = Matrix(g_matrix)
            print(g_matrix.shape)
            logger.info('[INFO] Generator matrix value: {}'.format(g_matrix))
            return g_matrix

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def transform_polynom(self, polynom):
        x = symbols('x')
        poly = x * 0
        for i in range(len(polynom.coeffs)):
            poly = poly + x ** (len(polynom.coeffs) - 1 - i) * polynom.coeffs[i]
        return poly

    # TO DO
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_syndrome_polynom(self, codeword):
        logger.info('[INFO] Calling get_syndrome_polynom')
        x = symbols('x')
        g = self.transform_polynom(self.g)
        syndrome_polynom = x * 0
        for i in range(len(codeword)):
            syndrome_polynom = syndrome_polynom + codeword[i] * (x - self.alpha_set[i]).invert(g)
        return syndrome_polynom

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def error_correction(self, codeword):
        x = symbols('x')
        syndrome_polynom = self.get_syndrome_polynom(codeword)
        h_polynom = syndrome_polynom.invert(self.transform_polynom(self.g))
        h_polynom = h_polynom + x * 1
        print(h_polynom.co)
        return None

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return None


if __name__ == '__main__':
    obj = BinaryGoppaCode(13, 13, 12, 10)
