load("proj/codes/linear_code.sage")
from proj.utilities.utilities import time_measurement_aspect, consumed_memory, resource_measurement_aspect


class GoppaCode(LinearCode):
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def __init__(self, code=None, m=2, t=3, base_field=2):
        if code == None:
            self.m = m
            self.F = GF(base_field ^ m)
            self.t = t
            self.code = self.generate_code()
            print("Generated Code: ", self.code)
        else:
            self.code = code

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_parity_check_matrix(self):
        return self.code.parity_check_matrix()

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_code(self):
        g = self.generate_goppa_polynomial_v1()
        self.poly = g
        L = [a for a in self.F.list() if g(a) != 0]
        return codes.GoppaCode(g, L)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_goppa_polynomial_v1(self):
        PolyRing = PolynomialRing(self.F, 'x')
        return PolyRing.irreducible_element(self.t) 
        