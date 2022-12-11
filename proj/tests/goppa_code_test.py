import sys
import unittest
import numpy as np
from cryptography.fernet import Fernet

from proj.codes.goppa_code import BinaryGoppaCode, random_inv_matrix, random_perm_matrix, get_random_msg, \
    get_random_error, get_string_from_vec, get_vec_from_str


class GoppaCodeTests(unittest.TestCase):
    def test_P_goppa_code(self):
        g = BinaryGoppaCode(13, 5,  12, 10)
        parity_check_matrix = g.get_parity_check_matrix()
        self.assertIsNotNone(parity_check_matrix)

    def test_alpha_goppa_code(self):
        g = BinaryGoppaCode(13, 5, 12, 10)
        alpha_set = g.get_alpha_set()
        self.assertIsNotNone(alpha_set)

    def test_G_goppa_code(self):
        g = BinaryGoppaCode(13, 5, 12, 10)
        generator = g.get_generator_matrix
        self.assertIsNotNone(generator)

    def test_encryption_goppa_code(self):
        code = BinaryGoppaCode(13, 5, 12, 10)
        S = random_inv_matrix(10)
        P = random_perm_matrix(12)
        G_ = S @ code.get_generator_matrix() @ P
        message = get_random_msg(10)
        e = get_random_error(12, 5)
        ciphertext = np.array(message) @ np.array(G_) + e
        self.assertNotEquals(message, ciphertext)

    def test_decryption_goppa_code(self):
        code = BinaryGoppaCode(13, 5, 12, 10)
        S = random_inv_matrix(10)
        P = random_perm_matrix(12)
        G_ = S @ code.get_generator_matrix() @ P
        message = get_random_msg(10)
        e = get_random_error(12, 5)
        ciphertext = np.array(message) @ np.array(G_) + e
        error_as_str = get_string_from_vec(e)

        FernetKey = Fernet.generate_key()
        FernetCryptoSystem = Fernet(FernetKey)
        encrypted_error = FernetCryptoSystem.encrypt(error_as_str.encode())
        print("encrypted_error=", str(encrypted_error))
        print("decrypted_error=", FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
        received_error = get_vec_from_str(FernetCryptoSystem.decrypt(encrypted_error).decode("utf-8"))
        print(f'received_error={received_error}')

        self.assertEquals(error_as_str, received_error)


s = unittest.TestLoader().loadTestsFromTestCase(GoppaCodeTests)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
