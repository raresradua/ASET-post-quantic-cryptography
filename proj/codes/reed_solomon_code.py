from proj.codes.linear_code import LinearCode
import numpy as np

''


class ReedSolomon(LinearCode):
    def __init__(self, code):
        super().__init__(code)
        self.x = np.array([])
        self.a = np.array([])
        self.A = np.matrix([][0])

    def p(self, x_value):
        pass

    def C(self, x_value):
        pass

    def set_code(self, code):
        pass

    def get_code(self, code):
        pass
