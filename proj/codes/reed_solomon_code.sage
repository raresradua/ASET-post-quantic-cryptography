load("proj/codes/linear_code.sage")
from proj.utilities.utilities import time_measurement_aspect, consumed_memory, resource_measurement_aspect

class ReedSolomon(LinearCode):
    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def __init__(self, code=None, n=10, k=5, q=11):
        if code == None:
            self.code = self.generate_code(n, k, q)
            self.decoder = codes.decoders.GRSKeyEquationSyndromeDecoder(self.code)
            self.ambient_space = self.code.ambient_space()
        else:
            self.code = code
            self.decoder = codes.decoders.GRSKeyEquationSyndromeDecoder(self.code)
            self.ambient_space = self.code.ambient_space()

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def get_parity_check_matrix(self):
        return self.code.parity_check_matrix()

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def generate_code(self, n, k, q):
        F = GF(q)
        return codes.GeneralizedReedSolomonCode(F.list()[1:n+1], k)