
class CodeBasedCryptoSystem:
    def __init__(self, code):
        self.linear_code = code

    def generateKeyPair(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def encrypt(self):
        raise NotImplementedError

    def decrypt(self):
        raise NotImplementedError
