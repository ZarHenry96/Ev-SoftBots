import random
from evosoro.tools.utils import clamp

class NewMaterial(object):
    """
    A class used to represent a new material.

    Attributes
    ----------
    name : str
        the name of the material that will be displayed in VoxCad
    rgb : array_like
        the normalized RGB tuple used to display the material in VoxCad
    type : str
        the material type, it can be either "muscle" or "tissue"
    young_modulus : float
        the mechanical property which measures the stiffness of a solid material (default None)
    density : float
        the measure of mass per unit of volume (default None)
    cte : float
        the coefficient of thermal expansion (default None)
    """

    def __init__(self, name, rgb, type, young_modulus=None, density=None, cte=None):
        """
        Parameters
        ----------
        name : str
            the name of the material that will be displayed in VoxCad
        rgb : array_like
            the normalized RGB tuple used to display the material in VoxCad
        type : str
            the material type, it can be either "muscle" or "tissue"
        young_modulus : float
            the mechanical property which measures the stiffness of a solid material (default None)
        density : float
            the measure of mass per unit of volume (default None)
        cte : float
            the coefficient of thermal expansion (default None)
        """

        self.name = name
        self.rgb = rgb
        self.type = type
        self.young_modulus = young_modulus
        self.density = density
        self.cte = cte

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __str__(self):
        return "type: " + str(self.type) + "\nyoung_modulus: " + str(self.young_modulus) + "\ndensity: " + str(
            self.density) + "\ncte: " + str(self.cte)

    def mutate(self):
        """
        Add a Gaussian distributed random variable to each attribute.
        """

        self.density += random.gauss(0, 1e+005)
        self.density = clamp(self.density, 1000, 1e+007)

        if self.type == "muscle":
            self.cte += random.gauss(0, 0.01)
            self.cte = clamp(self.cte, 0.001, 0.04)
        elif self.type == "tissue":
            self.young_modulus += random.gauss(0, 5000)
            self.young_modulus = clamp(self.young_modulus, 5000000.0, 500000000.0)
        else:
            assert False




