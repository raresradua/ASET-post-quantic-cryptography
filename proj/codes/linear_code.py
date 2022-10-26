from abc import ABC


class LinearCode(ABC):
    def __init__(self, code):
        self.code = code

    def set_code(self, code):
        raise NotImplementedError

    def get_code(self, code):
        raise NotImplementedError

