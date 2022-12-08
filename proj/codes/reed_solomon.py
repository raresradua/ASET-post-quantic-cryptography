from linear_code import LinearCode
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
from abc import abstractmethod
import galois
import numpy as np
import random as rand
from cryptography.fernet import Fernet


def get_string_from_vec(vec):
    s = ""
    for element in vec:
        s += str(element)
    return s


def get_vec_from_str(string_):
    vec = []
    for ch in string_:
        vec.append(int(ch))
    return vec


def random_perm_matrix(n):
    return np.array([[1 if i == x else 0 for i in range(n)] for x in np.random.permutation(n)])


def random_inv_matrix(n):
    candidate_ = None
    while 1:
        candidate = np.random.randint(2, size=(n, n))
        det = int(round(np.linalg.det(candidate)))
        if det % 2 == 1:
            candidate_ = candidate
            break
    return candidate_


def transform(matrix):
    res = []
    for i in range(len(matrix)):
        vec = []
        for j in range(len(matrix[i])):
            vec.append(int(matrix[i][j]))
        res.append(vec)
    return res


def get_random_msg(size):
    return [rand.randint(0, 1) for i in range(size)]


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

    def __int__(self, n, k):
        self.n = n
        self.k = k
        self.reed_solomon = galois.ReedSolomon(n, k)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_parity_check_matrix(self):
        return self.reed_solomon.H

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_generator_matrix(self):
        return self.reed_solomon.G

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def error_correction(self, codeword):
        return self.reed_solomon.detect(codeword)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return self.reed_solomon.decode(codeword)


if __name__ == '__main__':
    n = 15
    k = 9

    code = galois.ReedSolomon(n, k)

    S = random_inv_matrix(k)
    P = random_perm_matrix(n)

    H = np.array([np.array(el) for el in transform(code.H)])
    G_ = S @ transform(code.G) @ P
    m = get_random_msg(k)
    e = get_random_error(n, code.t)
    y = m @ G_ + e

    print(f'H={H}')
    print(f'S={S}')
    print(f'G={code.G}')
    print(f'P={P}')
    print(f'G\'={G_}')
    print(f'm={m}')
    print(f'y={y}')
    print(f'e={e}')

    error_as_str = get_string_from_vec(e)
    FernetKey = Fernet.generate_key()
    FernetCryptoSystem = Fernet(FernetKey)
    encrypted_error = FernetCryptoSystem.encrypt(error_as_str.encode())
    print("encrypted_error=", str(encrypted_error))
    print("decrypted_error=", FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
    received_error = get_vec_from_str(FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
    print(f'received_error={received_error}')

    mG_ = y - received_error
    print(f'mG_={mG_}')
    G_ = np.float_(G_)
    m = mG_ @ np.linalg.pinv(G_)
    m = [round(x) for x in m]
    print(f'm\'={m}')
