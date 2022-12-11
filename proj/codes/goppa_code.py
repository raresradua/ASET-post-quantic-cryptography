from .linear_code import LinearCode
import galois
from sympy import Matrix
import random as rand
from utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect, fernet_key, get_string_from_vec, get_vec_from_str
import logging
import numpy as np
from cryptography.fernet import Fernet


logger = logging.getLogger()


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def get_random_msg(size):
    return [rand.randint(0, 1) for index in range(size)]


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def get_random_error(size, number_errors):
    count_errors = 0
    vec = [0] * size
    while count_errors < number_errors:
        index_error = rand.randint(0, size - 1)
        if vec[index_error] == 0:
            vec[index_error] = 1
            count_errors += 1
    return vec


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def random_inv_matrix(size):
    while 1:
        candidate = np.random.randint(2, size=(size, size))
        det = int(round(np.linalg.det(candidate)))
        if det % 2 == 1:
            return candidate


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def pow_(a, b):
    r = a
    for i in range(b):
        r = r * a
    return r


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def extended_gcd(aa, bb):
    last_remainder, remainder = abs(aa), abs(bb)
    x, last_x, y, last_y = 0, 1, 1, 0
    while remainder:
        last_remainder, (quotient, remainder) = remainder, divmod(
            last_remainder, remainder)
        x, last_x = last_x - quotient * x, x
        y, last_y = last_y - quotient * y, y
    return last_remainder, last_x * (-1 if aa < 0 else 1), last_y * (-1 if bb < 0 else 1)

@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def mod_inv(a, mod):
    g, x, y = extended_gcd(a, mod)
    if g != 1:
        return None
    return x % mod


class GoppaCode(LinearCode):
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def __init__(self, m_val=20, t_val=5, n_val=12, k_val=10):
        logger.info('[INFO] Calling __init__ for GoppaCode')
        try:
            assert k_val >= n_val - m_val * t_val
        except Exception:
            logger.error('[ERROR] Invalid arguments.')
        else:
            logger.info('[INFO] Arguments are alright.')
            self.m = m_val  # 2 la m
            self.t = t_val  # erori - nr de 1
            self.n = n_val  # lungime
            self.base_field = 2
            self.val = 2 ** m_val
            self.k = k_val  # k dim matrice simetrizabila
            self.F = galois.GF(2 ** m_val)
            self.g = galois.irreducible_poly(self.F.order, self.t, 'random')
            self.coefficients = self.g.coefficients(self.t + 1, 'asc')
            self.alpha_set = self.generate_alpha_set()
            self.H = self.generate_parity_check_matrix()
            self.G = self.generate_generator_matrix()
            self.fernet_key = fernet_key
            self.fernet_cryptosys = Fernet(self.fernet_key)
            super().__init__(n_val, k_val, self)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def encrypt_message(self, msg, public_key):
        msg = [[int(d) for d in bin(ord(i))[2:]] for i in msg]
        for idx, i in enumerate(msg):
            if len(i) < self.k:
                msg[idx] = [0] * (self.k - len(i)) + i
        err = get_random_error(self.n, public_key['t'])

        encrypted = []
        print(msg)
        for i in msg:
            encrypted.append(np.array(i) @ np.array(public_key['G_prime']) + err)

        err_str = get_string_from_vec(err)
        enc_err = self.fernet_cryptosys.encrypt(err_str.encode())
        print(encrypted)
        print(len(encrypted))
        return ''.join([''.join([chr(c + 1000) for c in i]) for i in encrypted]), enc_err

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_keys(self):
        t = self.t  # face parte din cheia publica

        S = random_inv_matrix(self.k)  # matricea inversa care e simterica, cheie privata
        P = self.random_perm_matrix(self.n)  # matrice permutare, cheie privata

        G_prime = np.array(S @ self.code.get_generator_matrix() @ P)  # face parte din cheia publica

        for i in G_prime:
            for j in i:
                i[j] = int(i[j])

        for i in S:
            for j in i:
                i[j] = int(i[j])

        for i in P:
            for j in i:
                i[j] = int(i[j])

        return {
            'public_key': {
                'G_prime': G_prime.tolist(),
                't': t
            },
            'private_key': {
                'S': S.tolist(),
                'P': P.tolist()
            }
        }

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decrypt_message(self, cipher, err, key):
        dec_err = get_vec_from_str(self.fernet_cryptosys.decrypt(err).decode('utf-8'))
        arr = []
        start, end = 0, self.n
        while end <= len(cipher):
            arr.append(np.array([ord(c) - 1000 for c in cipher[start:end]]) - dec_err)
            start = end
            end += self.n

        mG_prime = []
        for i in arr:
            mG_prime.append(i)

        m_dec = [m_ @ np.linalg.pinv(np.float_(key['G_prime'])) for m_ in mG_prime]
        return ''.join([chr(int(''.join(str(c) for c in i), 2)) for i in [[round(x) for x in m_cc] for m_cc in m_dec]])

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
    def random_perm_matrix(self, size):
        return np.array([[1 if i == x else 0 for i in range(size)] for x in np.random.permutation(self.n)])

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
                    vec.append(int(h_bin.nullspace()[i][j]))
                g_matrix.append(vec)

            # g_matrix = Matrix(g_matrix)
            logger.info('[INFO] Generator matrix value: {}'.format(g_matrix))
            return g_matrix


if __name__ == '__main__':
    g = GoppaCode()
    msg_ = 'salut hei salut hei salut'

    keys = g.generate_keys()
    cryp, err = g.encrypt_message(msg_, keys['public_key'])
    dec = g.decrypt_message(cryp, err, keys['public_key'])
    print(dec)

    keys = g.generate_keys()
    cryp, err = g.encrypt_message(msg_, keys['public_key'])
    dec = g.decrypt_message(cryp, err, keys['public_key'])
    print(dec)

    keys = g.generate_keys()
    cryp, err = g.encrypt_message(msg_, keys['public_key'])
    dec = g.decrypt_message(cryp, err, keys['public_key'])
    print(dec)