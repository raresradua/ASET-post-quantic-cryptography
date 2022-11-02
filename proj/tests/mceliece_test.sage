import sys
import unittest

load("proj/codes/goppa_code.sage")
load("proj/codes/reed_solomon_code.sage")
load("proj/crypto/mceliece.sage")

class McElieceTest(unittest.TestCase):
    def test_mcelice_code(self):
        g = GoppaCode()
        r = ReedSolomon()
        m_g = McEliece(g)
        # to_encrypt = [1,2,3,4,5]
        to_encrypt = [1,2,3,4,5,6]
        y = m_g.encrypt(to_encrypt)
        self.assertEquals(y.nrows(), 1)
        self.assertEquals(y.ncols(), 4)


s = unittest.TestLoader().loadTestsFromTestCase(McElieceTest)
unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)