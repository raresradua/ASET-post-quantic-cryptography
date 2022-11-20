from abc import ABC, abstractmethod
from proj.utilities.utilities import consumed_memory, resource_measurement_aspect, time_measurement_aspect


class LinearCode(ABC):
    def __init__(self, n, k, code):
        self.n = n
        self.k = k
        self.code = code

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_parity_check_matrix(self):
        ...

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def get_generator_matrix(self):
        ...

    @consumed_memory
    @resource_measurement_aspect
    @time_measurement_aspect
    @abstractmethod
    def error_correction(self, codeword):
        ...
