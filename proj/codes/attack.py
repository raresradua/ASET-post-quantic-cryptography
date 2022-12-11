import numpy as np
import itertools
from utilities.utilities import get_string_from_vec


def generate_errors(received_error, t):
    good_errors = []
    possible_errors = [np.array(list(i)) for i in list(itertools.product([0, 1], repeat=len(received_error)))]
    for possible_error in possible_errors:
        number_ones = get_string_from_vec(possible_error).count('1')
        if number_ones == t:
            good_errors.append(possible_error)

    return good_errors


def attack_cipher(good_errors, n, ciph, crypto, pub):
    good_results = 5
    rez = []
    for err in good_errors:
        try:
            arr = []
            start, end = 0, n
            while end <= len(ciph):
                arr.append(np.array([ord(c) - 1000 if crypto == 'goppa' else ord(c) for c in ciph[start:end]]) - err)
                start = end
                end += n

            mG_prime = []
            for i in arr:
                mG_prime.append(i)

            m_dec = [m_ @ np.linalg.pinv(np.float_(pub['G_prime'] if crypto == 'goppa' else np.array(pub['G_prime']))) for m_ in mG_prime]
            rez.append(
                ''.join([chr(int(''.join(str(c) for c in i), 2)) for i in [[round(x) for x in m_cc] for m_cc in m_dec]]))
            if len(rez) == good_results:
                break

        except:
            continue
    return rez
