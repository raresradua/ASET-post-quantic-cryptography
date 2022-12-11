import logging
import sys
import unittest
import coverage
from proj.codes.goppa_code import GoppaCode

logger = logging.getLogger()


class GoppaCodeTests(unittest.TestCase):
    def test_P_goppa_code(self):
        g = GoppaCode()
        parity_check_matrix = g.get_parity_check_matrix()
        self.assertIsNotNone(parity_check_matrix)

    def test_alpha_goppa_code(self):
        g = GoppaCode()
        alpha_set = g.get_alpha_set()
        self.assertIsNotNone(alpha_set)

    def test_G_goppa_code(self):
        g = GoppaCode()
        generator = g.get_generator_matrix()
        self.assertIsNotNone(generator)

    def test_generated_keys(self):
        code = GoppaCode()
        keys = code.generate_keys()
        self.assertIsNotNone(keys['public_key'])
        self.assertIsNotNone(keys['private_key'])

    def test_encryption_goppa_code(self):
        g = GoppaCode()
        msg_ = 'alabalaportocala'
        keys = g.generate_keys()
        cryp, err = g.encrypt_message(msg_, keys['public_key'])

        self.assertNotEqual(msg_, cryp)

    def test_decryption_goppa_code(self):
        g = GoppaCode()
        msg_ = 'alabalaportocala'

        keys = g.generate_keys()
        cryp, err = g.encrypt_message(msg_, keys['public_key'])
        dec = g.decrypt_message(cryp, err, keys['public_key'])
        print(dec)

        self.assertEquals(msg_, dec)


s = unittest.TestLoader().loadTestsFromTestCase(GoppaCodeTests)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)

