from abc import ABC, abstractmethod


class LinearCode(ABC):
    def __init__(self, code):
        self.code = code

    def set_code(self, code):
        raise NotImplementedError

    def get_code(self, code):
        raise NotImplementedError

    @abstractmethod
    def get_parity_check_matrix(self):
        ...
    
    @abstractmethod
    def get_generator_matrix(self):
        ...
