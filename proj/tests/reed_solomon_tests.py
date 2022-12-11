import sys
import unittest

import coverage

from proj.codes.reed_solomon import ReedSolomon


class ReedSolomonTest(unittest.TestCase):
    def test_generated_keys(self):
        code = ReedSolomon()
        keys = code.generate_keys()
        self.assertIsNotNone(keys['public_key'])
        self.assertIsNotNone(keys['private_key'])

    def test_encryption_goppa_code(self):
        code = ReedSolomon()
        msg_ = 'alabalaportocala'
        keys = code.generate_keys()
        cryp, err = code.encrypt_message(msg_, keys['public_key'])
        self.assertNotEqual(msg_, cryp)

    def test_decryption_goppa_code(self):
        r = ReedSolomon()
        msg_ = 'alabalaportocala'
        keys = r.generate_keys()
        cryp, err = r.encrypt_message(msg_, keys['public_key'])
        dec = r.decrypt_message(cryp, err, keys['public_key'])

        self.assertEqual(msg_, dec)


s = unittest.TestLoader().loadTestsFromTestCase(ReedSolomonTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
