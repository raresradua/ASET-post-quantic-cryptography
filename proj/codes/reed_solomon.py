from .linear_code import LinearCode
from utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect, fernet_key, get_string_from_vec, get_vec_from_str
import galois
import numpy as np
import random as rand
from cryptography.fernet import Fernet


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def random_perm_matrix(n):
    return np.array([[1 if i == x else 0 for i in range(n)] for x in np.random.permutation(n)])


@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def random_inv_matrix(n):
    candidate_ = None
    while 1:
        candidate = np.random.randint(2, size=(n, n))
        det = int(round(np.linalg.det(candidate)))
        if det % 2 == 1:
            candidate_ = candidate
            break
    return candidate_

@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def transform(matrix):
    res = []
    for i in range(len(matrix)):
        vec = []
        for j in range(len(matrix[i])):
            vec.append(int(matrix[i][j]))
        res.append(vec)
    return res

@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def get_random_msg(size):
    return [rand.randint(0, 1) for i in range(size)]

@consumed_memory
@resource_measurement_aspect
@time_measurement_aspect
def get_random_error(size, capacity):
    e = [0 for i in range(size)]
    i = 0
    while i < capacity:
        poz = rand.randint(0, size - 1)
        if e[poz] == 0:
            e[poz] = 1
            i = i + 1
    return e


class ReedSolomon(LinearCode):
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def __init__(self, n=15, k=8):
        super().__init__(n, k, galois.ReedSolomon(n, k))
        self.fernet_key = fernet_key
        self.fernet_cryptosys = Fernet(self.fernet_key)

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
        for i in msg:
            encrypted.append(i @ np.array(public_key['G_prime']) + err)

        err_str = get_string_from_vec(err)
        enc_err = self.fernet_cryptosys.encrypt(err_str.encode())
        return ''.join([''.join([chr(c) for c in i]) for i in encrypted]), enc_err

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decrypt_message(self, cipher, err, key):
        dec_err = get_vec_from_str(self.fernet_cryptosys.decrypt(err).decode('utf-8'))
        arr = []
        start, end = 0, self.n
        while end <= len(cipher):
            arr.append(np.array([ord(c) for c in cipher[start:end]]) - dec_err)
            start = end
            end += self.n

        mG_prime = []
        for i in arr:
            mG_prime.append(i)

        m_dec = [m_ @ np.linalg.pinv(np.float_(np.array(key['G_prime']))) for m_ in mG_prime]
        return ''.join([chr(int(''.join(str(c) for c in i), 2)) for i in [[round(x) for x in m_cc] for m_cc in m_dec]])

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_keys(self):
        t = self.code.t  # public

        S = random_inv_matrix(self.k)  # priv
        P = random_perm_matrix(self.n)  # priv

        G_prime = S @ transform(self.code.G) @ P  # public
        return {
            'public_key': {'G_prime': G_prime.tolist(), 't': t},
            'private_key': {'S': S.tolist(), 'P': P.tolist()}
        }


if __name__ == '__main__':
    r = ReedSolomon()
    msg_ = 'salut hei salut hei salut'
    import json
    keys = r.generate_keys()
    exit(1)
    keys_1 = r.generate_keys()

    keys_2 = r.generate_keys()

    cryp, err = r.encrypt_message(msg_, keys['public_key'])

    cryp_1, err_1 = r.encrypt_message(msg_, keys_1['public_key'])

    cryp_2, err_2 = r.encrypt_message(msg_, keys_2['public_key'])

    print(cryp)
    print(cryp_1)
    print(cryp_2)

    dec = r.decrypt_message(cryp, err, keys['public_key'])
    dec_1 = r.decrypt_message(cryp_1, err_1, keys_1['public_key'])
    dec_2 = r.decrypt_message(cryp_2, err_2, keys_2['public_key'])

    print(dec)
    print(dec_1)
    print(dec_2)
