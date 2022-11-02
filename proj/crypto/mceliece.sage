load("proj/crypto/code_based_cryptosystem.sage")
load("proj/codes/goppa_code.sage")

class McEliece(CodeBasedCryptosystem):
    def generate_keypair(self):
        if isinstance(self.code, GoppaCode):
            G = self.code.code.parity_check_matrix()
            n, k = G.ncols(), G.nrows()
            S = self.generate_random_nonsingular_matrix(k)
            P = self.generate_permutation_matrix(n)
            return (((S * G * P), self.code.t), (G, S, P))
    
    def encrypt(self, message):
        assert len(message) == self.public_key[0].nrows()
        G_pub, t = self.public_key
        c_prime = matrix(QQ, message) * matrix(QQ, G_pub)
        z = self.encode_(G_pub.ncols(), t)
        return c_prime + z
    
    def decrypt(self, cryptotext):
        raise NotImplementedError
    
    def generate_random_nonsingular_matrix(self, size):
        S = random_matrix(ZZ, size)
        
        while not S.is_singular() and S.determinant()==0:
            S = random_matrix(ZZ, size)
        return S
    
    def generate_permutation_matrix(self, size):
        return Permutations(size).random_element().to_matrix()
        
    def encode_(self, n, t):
        enc = [0]*n
        count = t
        while count>0:
            r = randrange(n)
            if enc[r] == 0:
                enc[r]+=1
                count-=1
        return matrix(enc)
    