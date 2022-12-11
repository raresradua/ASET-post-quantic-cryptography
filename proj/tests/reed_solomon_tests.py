import sys
import unittest
from proj.codes.reed_solomon import ReedSolomon


class ReedSolomonTest(unittest.TestCase):
    def test_goppa_code(self):
        r = ReedSolomon(15, 9)
        parity = r.get_parity_check_matrix()
        self.assertIsNotNone(parity)


s = unittest.TestLoader().loadTestsFromTestCase(ReedSolomonTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
