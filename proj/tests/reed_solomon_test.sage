import sys
import unittest

load("proj/codes/reed_solomon_code.sage")

class ReedSolomonTest(unittest.TestCase):
    def test_goppa_code(self):
        r = ReedSolomon()
        parity = r.get_parity_check_matrix()
        self.assertIsNotNone(parity)

s = unittest.TestLoader().loadTestsFromTestCase(ReedSolomonTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)