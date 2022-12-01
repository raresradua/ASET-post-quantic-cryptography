from linear_code import LinearCode
import galois
from sympy import Matrix, symbols, sqf_part
import random as rand
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
import logging
import numpy as np

logger = logging.getLogger()


def random_perm_matrix(size):
    return np.array([[1 if i == x else 0 for i in range(size)] for x in np.random.permutation(n)])


def get_random_msg(size):
    return [rand.randint(0, 1) for index in range(size)]


def random_inv_matrix(size):
    while 1:
        candidate = np.random.randint(2, size=(size, size))
        det = int(round(np.linalg.det(candidate)))
        if det % 2 == 1:
            return candidate


def pow_(a, b):
    r = a
    for i in range(b):
        r = r * a
    return r


def extended_gcd(aa, bb):
    last_remainder, remainder = abs(aa), abs(bb)
    x, last_x, y, last_y = 0, 1, 1, 0
    while remainder:
        last_remainder, (quotient, remainder) = remainder, divmod(
            last_remainder, remainder)
        x, last_x = last_x - quotient * x, x
        y, last_y = last_y - quotient * y, y
    return last_remainder, last_x * (-1 if aa < 0 else 1), last_y * (-1 if bb < 0 else 1)


def mod_inv(a, mod):
    g, x, y = extended_gcd(a, mod)
    if g != 1:
        return None
    return x % mod


class BinaryGoppaCode(LinearCode):

    def __init__(self, m_val, t_val, n_val, k_val):
        logger.info('[INFO] Calling __init__ for GoppaCode')
        try:
            assert k_val >= n_val - m_val * t_val
        except Exception:
            logger.error('[ERROR] Invalid arguments.')
        else:
            logger.info('[INFO] Arguments are alright.')
            self.m = m_val
            self.t = t_val
            self.n = n_val
            self.base_field = 2
            self.val = 2 ** m_val
            self.k = k_val
            self.F = galois.GF(2 ** m_val)
            self.g = galois.irreducible_poly(self.F.order, self.t, 'random')
            self.coefficients = self.g.coefficients(self.t + 1, 'asc')
            self.alpha_set = self.get_alpha_set()
            self.H = self.get_parity_check_matrix()
            self.G = self.get_generator_matrix()
            self.syndrome_polynom = self.get_syndrome_polynom([1, 1, 1, 1, 1, 1, 1])
            self.e = self.error_correction([1, 1, 1, 1, 1, 1, 1])
            super().__init__(n, k, self)
            logger.info('Arguments for Goppa Code: {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(
                self.m, self.t, self.n, self.base_field, self.val, self.k, self.F, self.g, self.coefficients,
                self.alpha_set, self.H, self.H, self.G, self.syndrome_polynom
            ))

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_alpha_set(self):
        logger.info('[INFO] Calling get_alpha_set')
        alpha_set = []
        while len(alpha_set) < self.n:
            element = rand.randint(0, self.val)
            if int(self.g(element)) % int(self.val) != 0 and mod_inv(int(self.g(element)) % int(self.val),
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
        z_matrix = Matrix(self.n, self.n, lambda i, j: mod_inv(
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
            h_bin = Matrix(self.H.shape[0], self.H.shape[1], lambda index_i, index_j: self.H[index_i, index_j] % 2)
            g_matrix = []
            for i in range(len(h_bin.nullspace())):
                vec = []
                for j in range(len(h_bin.nullspace()[i])):
                    vec.append(h_bin.nullspace()[i][j])
                g_matrix.append(vec)
            g_matrix = Matrix(g_matrix)
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

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_syndrome_polynom(self, codeword):
        logger.info('[INFO] Calling get_syndrome_polynom')
        x = symbols('x')
        s = 0
        g = self.transform_polynom(self.g)
        for i in range(len(codeword)):
            s = s + codeword[i] * (x - self.alpha_set[i]).invert(g)
        return s

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def error_correction(self, codeword):
        x = symbols('x')
        g_x = self.transform_polynom(self.g)
        S_polynom = self.get_syndrome_polynom(codeword)
        if S_polynom == 0:
            return codeword
        H_polynom = S_polynom.invert(g_x)
        quotient, T_polynom = divmod(sqf_part(H_polynom + x), g_x)
        T_polynom = T_polynom.__getnewargs__()[0]
        return None

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return None


if __name__ == '__main__':
    m = 13
    t = 13
    n = 12
    k = 10
    code = BinaryGoppaCode(m, t, n, k)
    S = random_inv_matrix(k)
    P = random_perm_matrix(n)
    G_ = S @ code.get_generator_matrix() @ P
    m = get_random_msg(k)
