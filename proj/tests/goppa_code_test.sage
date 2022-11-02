import sys
import unittest

load("proj/codes/goppa_code.sage")

class GoppaCodeTest(unittest.TestCase):
    def test_goppa_code(self):
        g = GoppaCode()
        parity_check_matrix = g.get_parity_check_matrix()
        self.assertIsNotNone(parity_check_matrix)

s = unittest.TestLoader().loadTestsFromTestCase(GoppaCodeTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)