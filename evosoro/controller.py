import random
from evosoro.tools.utils import clamp


class Controller(object):
    """Base class for controller."""

    def __init__(self, init_temp_ampl=14, init_temp_period=0.25, init_muscles_cte=0.01):
        self.temp_amplitude = init_temp_ampl
        self.temp_period = init_temp_period
        self.muscles_cte = init_muscles_cte

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __str__(self):
        return "\ntemp_amplitude: "+str(self.temp_amplitude) + "\ntemp_period: " + str(self.temp_period) + \
               "\nmuscles_cte: " + str(self.muscles_cte)

    def mutate(self):
        self.temp_amplitude += random.gauss(0, 1)
        self.temp_amplitude = clamp(self.temp_amplitude, 1, 25)

        self.temp_period += random.gauss(0, 0.1)
        self.temp_period = clamp(self.temp_period, 0.001, 1)

        self.muscles_cte += random.gauss(0, 0.01)
        self.muscles_cte = clamp(self.muscles_cte, 0.0001, 0.035)

