load("proj/crypto/code_based_cryptosystem.sage")
load("proj/codes/goppa_code.sage")
from proj.utilities.utilities import time_measurement_aspect, consumed_memory, resource_measurement_aspect

class McEliece(CodeBasedCryptosystem):
    #def __init__(self, code, public_key=None, private_key=None):
    #   super().__init__(code, public_key, private_key)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_keypair(self):
        if isinstance(self.code, GoppaCode):
            G = self.code.code.parity_check_matrix()
            n, k = G.ncols(), G.nrows()
            S = self.generate_random_nonsingular_matrix(k)
            P = self.generate_permutation_matrix(n)
            return (((S * G * P), self.code.t), (G, S, P))

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def encrypt(self, message):
        assert len(message) == self.public_key[0].nrows()
        G_pub, t = self.public_key
        c_prime = matrix(QQ, message) * matrix(QQ, G_pub)
        z = self.encode_(G_pub.ncols(), t)
        return c_prime + z
    
    def decrypt(self, cryptotext):
        raise NotImplementedError

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_random_nonsingular_matrix(self, size):
        S = random_matrix(ZZ, size)
        
        while not S.is_singular() and S.determinant()==0:
            S = random_matrix(ZZ, size)
        return S

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_permutation_matrix(self, size):
        return Permutations(size).random_element().to_matrix()

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def encode_(self, n, t):
        enc = [0]*n
        count = t
        while count>0:
            r = randrange(n)
            if enc[r] == 0:
                enc[r]+=1
                count-=1
        return matrix(enc)
    