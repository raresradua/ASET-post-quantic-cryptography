from abc import ABC, abstractmethod

class CodeBasedCryptosystem(ABC):
    def __init__(self, code, public_key=None, private_key=None):
        self.code = code
        self.decoder = code.code.decoder
        self.ambient_space = code.code.ambient_space
        if public_key == None or private_key == None:
            self.public_key, self.private_key = self.generate_keypair()
        else:
            self.public_key = public_key
            self.private_key = private_key

    @abstractmethod
    def generate_keypair(self):
        ...

    @abstractmethod
    def encrypt(self, message):
        ...

    @abstractmethod
    def decrypt(self, cryptotext):
        ...

        
class McEliece(CodeBasedCryptosystem):
    def generate_keypair(self):
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
        print(z)
        print(c_prime)
        return c_prime + z
    
    def decrypt(self, cryptotext):
        inverse_P = ~self.private_key[2]
        c_caciula = cryptotext * inverse_P
        m_cacuila = self.decoder(c_caciula)
        return m_cacuila * ~self.private_key[1]
    
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