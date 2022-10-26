from proj.codes.linear_code import LinearCode
import numpy as np


class GoppaCode(LinearCode):

    def __init__(self, code):
        super().__init__(code)
        self.L = np.array([])
        self.C = np.matrix([][0])

    def g(self, x_val):
        pass

    def R(self, c_vector, x_integer):
        pass

    def set_code(self, code):
        pass

    def get_code(self, code):
        pass
