from linear_code import LinearCode
import galois
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect
from abc import abstractmethod


class ReedSolomon(LinearCode):

    def __int__(self, n, k):
        self.n = n
        self.k = k
        self.reed_solomon = galois.ReedSolomon(n, k)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_parity_check_matrix(self):
        return self.reed_solomon.H

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_generator_matrix(self):
        return self.reed_solomon.G

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def error_correction(self, codeword):
        return self.reed_solomon.detect(codeword)

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    def decode(self, codeword):
        return self.reed_solomon.decode(codeword)
