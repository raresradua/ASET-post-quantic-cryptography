from linear_code import LinearCode
import galois
from sympy import Matrix, symbols, Poly
import random as rand
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
import logging
import numpy as np
from cryptography.fernet import Fernet
import itertools

logger = logging.getLogger()


def random_perm_matrix(size):
    return np.array([[1 if i == x else 0 for i in range(size)] for x in np.random.permutation(n)])


def get_random_msg(size):
    return [rand.randint(0, 1) for index in range(size)]


def get_random_error(size, number_errors):
    count_errors = 0
    vec = [0] * size
    while count_errors < number_errors:
        index_error = rand.randint(0, size - 1)
        if vec[index_error] == 0:
            vec[index_error] = 1
            count_errors += 1
    return vec


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


def get_string_from_vec(vec):
    s = ""
    for element in vec:
        s += str(element)
    return s


def get_vec_from_str(str):
    vec = []
    for ch in str:
        vec.append(int(ch))
    return vec


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
            self.alpha_set = self.generate_alpha_set()
            self.H = self.generate_parity_check_matrix()
            self.G = self.generate_generator_matrix()
            super().__init__(n, k, self)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_alpha_set(self):
        return self.alpha_set

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_generator_matrix(self):
        return self.G

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_parity_check_matrix(self):
        return self.H

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_alpha_set(self):
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
    def generate_parity_check_matrix(self):
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
    def generate_generator_matrix(self):
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
    def solve_equation(self, A_polynom, B_polynom):
        x = symbols('x')
        s, h, t = Poly(A_polynom).gcdex(Poly(B_polynom))
        A = (s * A_polynom).as_expr()
        B = (h - t * B_polynom).as_expr()
        return A ** 2 + x * (B ** 2)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return None

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_error_locating_polynomial(self, v_error):
        x = symbols('x')
        error_locating_poly = 1
        for i in range(len(v_error)):
            if v_error[i] == 1:
                error_locating_poly = error_locating_poly * (x - self.alpha_set[i])
        return Poly(error_locating_poly)


if __name__ == '__main__':
    m = 13
    t = 5
    n = 12
    k = 10
    code = BinaryGoppaCode(m, t, n, k)
    S = random_inv_matrix(k)
    P = random_perm_matrix(n)
    G_ = S @ code.get_generator_matrix() @ P
    message = get_random_msg(k)
    e = get_random_error(n, t)
    ciphertext = np.array(message) @ np.array(G_) + e
    error_as_str = get_string_from_vec(e)
    print(f'message={message}')
    print(f'S={S}')
    print(f'P={P}')
    print(f'G={code.get_generator_matrix()}')
    print(f'G\'={G_}')
    print(f'ciphertext={ciphertext}')
    print(f'error={e}')

    FernetKey = Fernet.generate_key()
    FernetCryptoSystem = Fernet(FernetKey)
    encrypted_error = FernetCryptoSystem.encrypt(error_as_str.encode())
    print("encrypted_error=", str(encrypted_error))
    print("decrypted_error=", FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
    received_error = get_vec_from_str(FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
    print(f'received_error={received_error}')

    mG_ = ciphertext - received_error
    print(f'mG_={mG_}')
    G_ = np.float_(G_)
    m = mG_ @ np.linalg.pinv(G_)
    m = [round(x) for x in m ]
    print(f'm\'={m}')
    # print(f'm={(mG_ @ np.linalg.inv(P)) @ np.linalg.pinv(S @ G_)}')
    copy_msg = m

    good_errors = []
    possible_errors = [np.array(list(i)) for i in list(itertools.product([0, 1], repeat=len(received_error)))]
    for possible_error in possible_errors:
        number_ones = get_string_from_vec(possible_error).count('1')
        if number_ones == t:
            good_errors.append(possible_error)

    for error in good_errors:
        mG_ = ciphertext - error
        G_ = np.float_(G_)
        m = mG_ @ np.linalg.pinv(G_)
        m = [round(x) for x in m]
        if np.array_equal(m, copy_msg):
            print(f'error={error}')
            print(f'm={m}')
            print("Cryptosystem broken ! Message recovered")
