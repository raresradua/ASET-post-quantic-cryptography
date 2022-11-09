from abc import ABC, abstractmethod
from proj.utilities.utilities import time_measurement_aspect, consumed_memory, resource_measurement_aspect

class CodeBasedCryptosystem(ABC):
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
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
