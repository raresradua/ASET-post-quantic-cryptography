from linear_code import LinearCode
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
from abc import abstractmethod
import galois
import numpy as np
import random as rand
from sympy import Poly, Symbol, roots, solve, CRootOf

GF = galois.GF(2 ** 4)


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


def calculate_poly(message):
    x = Symbol('x')
    s = 0
    for i in range(len(message)):
        s = s + message[i] * (x ** i)
    return Poly(s)


def transform_polynom(polynom):
    x = Symbol('x')
    poly = x * 0
    for i in range(len(polynom.coeffs)):
        poly = poly + x ** (len(polynom.coeffs) - 1 - i) * polynom.coeffs[i]
    return Poly(poly)


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
    G1 = S @ transform(code.G) @ P
    m = get_random_msg(k)
    e = get_random_error(n, code.t)
    y = m @ G1 + e

    quotients = []
    y_ = y @ np.linalg.inv(P)
    copy_y_ = y_

    y_ = [int(el) for el in y_]

    syndrom = y_ @ H.T

    print(f'H={H}')
    print(f'S={S}')
    print(f'G={code.G}')
    print(f'P={P}')
    print(f'G\'={G1}')
    print(f'm={m}')
    print(f'y={y}')
    print(f'e={e}')
    print(f'y_={y_}')
    print(f'syndrome={syndrom}')

    s = m @ G1
    mG = y - e
    j = mG @ np.linalg.pinv(G1)
    j = [int(el) for el in j]
    print(f'm\'={s}')
    print(f'm\'={mG}')
    print(f'm={j}')