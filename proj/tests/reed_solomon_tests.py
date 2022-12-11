import sys
import unittest

import galois
import numpy as np
from cryptography.fernet import Fernet

from proj.codes.reed_solomon import ReedSolomon, random_inv_matrix, random_perm_matrix, transform, get_random_msg, \
    get_random_error, get_string_from_vec, get_vec_from_str


class ReedSolomonTest(unittest.TestCase):
    def test_rs_code(self):
        r = ReedSolomon(15, 9)
        parity = r.get_parity_check_matrix()
        self.assertIsNotNone(parity)

    def test_G_rs_code(self):
        r = ReedSolomon(15, 9)
        generator = r.get_generator_matrix()
        self.assertIsNotNone(generator)

    def test_encryption_goppa_code(self):
        code = galois.ReedSolomon(15, 9)

        S = random_inv_matrix(9)
        P = random_perm_matrix(15)

        H = np.array([np.array(el) for el in transform(code.H)])
        G_ = S @ transform(code.G) @ P
        m = get_random_msg(9)
        e = get_random_error(15, code.t)
        y = m @ G_ + e
        self.assertNotEquals(m, y)

    def test_decryption_goppa_code(self):
        code = galois.ReedSolomon(15, 9)

        S = random_inv_matrix(9)
        P = random_perm_matrix(15)

        H = np.array([np.array(el) for el in transform(code.H)])
        G_ = S @ transform(code.G) @ P
        m = get_random_msg(9)
        e = get_random_error(15, code.t)
        y = m @ G_ + e

        t = get_string_from_vec(e).count('1')
        error_as_str = get_string_from_vec(e)
        FernetKey = Fernet.generate_key()
        FernetCryptoSystem = Fernet(FernetKey)
        encrypted_error = FernetCryptoSystem.encrypt(error_as_str.encode())
        print("encrypted_error=", str(encrypted_error))
        print("decrypted_error=", FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
        received_error = get_vec_from_str(FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
        print(f'received_error={received_error}')

        self.assertEquals(error_as_str, received_error)


s = unittest.TestLoader().loadTestsFromTestCase(ReedSolomonTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
