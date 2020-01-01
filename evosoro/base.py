from __future__ import division

import math
import numpy as np

from evosoro.obstacle import Obstacle
from evosoro.tools.utils import xml_format

# TODO: classes should hold dictionaries of variables, vxa tags and values
# TODO: remove most of the hard coded text from read_write_voxelyze.py and replace with a few loops
# TODO: add method to VoxCadParams for organizing (nested) subsections in vxa files


class VoxCadParams(object):
    """Container for VoxCad parameters."""

    def __init__(self):
        self.sub_groups = []
        self.new_param_tag_dict = {}

    def add_param(self, name, val, tag):
        setattr(self, name, val)
        self.new_param_tag_dict[name] = xml_format(tag)


class Sim(VoxCadParams):
    """Container for VoxCad simulation parameters."""

    def __init__(self, self_collisions_enabled=True, simulation_time=10, dt_frac=0.7, stop_condition=2,
                 fitness_eval_init_time=2, equilibrium_mode=0, min_temp_fact=0.1, max_temp_fact_change=0.00001,
                 max_stiffness_change=10000, min_elastic_mod=5e006, max_elastic_mod=5e008, afterlife_time=0,
                 mid_life_freeze_time=0):

        VoxCadParams.__init__(self)

        self.sub_groups = ["Integration", "Damping", "Collisions", "Features", "StopCondition", "EquilibriumMode", "GA"]
        # custom nested things in "SurfMesh", "CMesh"

        self.self_collisions_enabled = self_collisions_enabled
        self.simulation_time = simulation_time
        self.dt_frac = dt_frac
        self.stop_condition = stop_condition
        self.fitness_eval_init_time = fitness_eval_init_time
        self.equilibrium_mode = equilibrium_mode
        self.min_temp_fact = min_temp_fact
        self.max_temp_fact_change = max_temp_fact_change
        self.max_stiffness_change = max_stiffness_change
        self.min_elastic_mod = min_elastic_mod
        self.max_elastic_mod = max_elastic_mod

        self.afterlife_time = afterlife_time
        self.mid_life_freeze_time = mid_life_freeze_time


class Env(VoxCadParams):
    """Container for VoxCad environment parameters."""

    def __init__(self, period=0.25, gravity_enabled=1, temp_enabled=1, floor_enabled=1, floor_slope=0.0,
                 lattice_dimension=0.01, fat_stiffness=5e+006, bone_stiffness=5e+008, muscle_stiffness=5e+006,
                 cte=0.01, temp_base=25, temp_amp=39, sticky_floor=0, time_between_traces=0, actuation_variance=0,
                 obstacles=False, ind_size=(6, 6, 6), env_size=(50, 50, 6), init_num_obstacles=1):

        VoxCadParams.__init__(self)

        self.sub_groups = ["Fixed_Regions", "Forced_Regions", "Gravity", "Thermal"]

        self.period = period
        self.gravity_enabled = gravity_enabled
        self.floor_enabled = floor_enabled
        self.temp_enabled = temp_enabled
        self.floor_slope = floor_slope
        self.lattice_dimension = lattice_dimension
        self.muscle_stiffness = muscle_stiffness
        self.bone_stiffness = bone_stiffness
        self.fat_stiffness = fat_stiffness
        self.cte = cte
        self.temp_amp = temp_amp
        self.temp_base = temp_base
        self.sticky_floor = sticky_floor
        self.time_between_traces = time_between_traces
        self.actuation_variance = actuation_variance
        self.obstacles = obstacles
        if self.obstacles:
            self.ind_size = ind_size
            self.env_size = env_size
            self.obst_list = []
            self.generate_obstacles(init_num_obstacles)
            self.env_matrix = np.zeros(self.env_size, dtype=int)
            self.build_env_matrix()

    def generate_obstacles(self, num_obstacles, max_num_obstacles=5):
        total = min(num_obstacles, max_num_obstacles)
        for i in range(0, total):
            diameter_x = self.ind_size[0] + int(round(((i+1)/max_num_obstacles)*(self.env_size[0]-self.ind_size[0])))
            if (diameter_x % 2) != 0:
                diameter_x += 1
            diameter_y = self.ind_size[1] + int(round(((i+1)/max_num_obstacles)*(self.env_size[1]-self.ind_size[1])))
            if (diameter_y % 2) != 0:
                diameter_y += 1
            self.obst_list.append(Obstacle(diameter_x, diameter_y, self.env_size, 1))

    def build_env_matrix(self):
        for obstacle in self.obst_list:
            for wall in obstacle.walls:
                x_start = int(round(wall["X"] * self.env_size[0]))
                x_end = x_start + int(round(wall["dX"] * self.env_size[0]))
                for i in range(x_start, x_end):
                    y_start = int(round(wall["Y"] * self.env_size[1]))
                    y_end = y_start + int(round(wall["dY"] * self.env_size[1]))
                    for j in range(y_start, y_end):
                        for k in range(0, obstacle.height):
                            self.env_matrix[i][j][k] = 5

    def insert_individual(self, ind_details):
        x_start = int((self.env_size[0]-self.ind_size[0])/2)
        for i in range(x_start, x_start + self.ind_size[0]):
            y_start = int((self.env_size[1]-self.ind_size[1])/2)
            for j in range(y_start, y_start + self.ind_size[0]):
                for k in range(0, self.ind_size[2]):
                    self.env_matrix[i][j][k] = ind_details["output_type"](ind_details["state"][i-x_start, j-y_start, k])


class ObjectiveDict(dict):
    """A dictionary describing the objectives for optimization. See self.add_objective()."""

    def __init__(self):
        super(ObjectiveDict, self).__init__()
        self.max_rank = 0

    # def __setitem__(self, key, value):
    #     # only allow adding entries through add_objective()
    #     raise SyntaxError
    # TODO: want to restrict input but this prevents deep copying: maybe instead just make object with embedded dict

    def add_objective(self, name, maximize, tag, node_func=None, output_node_name=None, logging_only=False):
        """Add an optimization objective to the dictionary.

        Objectives must be added in order of importance, however fitness is fixed to be the most important.

        The keys of an ObjectiveDict correspond to the objective's rank or importance. The ranks are set via the order
        in which objectives are added (fitness will auto-correct to rank 0).

        For each rank key, starting with 0, the corresponding value is another dictionary with three components:
        name, maximized, tag.

        Parameters
        ----------
        name : str
            The associated individual-level attribute name
        maximize : bool
            Whether superior individuals maximized (True) or minimize (False) the objective.
        tag : str or None
            The tag used in parsing the resulting output from a VoxCad simulation.
            If this is None then the attribute is calculated outside of VoxCad (in Python only).
        node_func : function
            If tag is None then the objective is not computed in VoxCad and is instead calculated on an output of a
            network.
        output_node_name : str
            The output node which node_func operates on.

        logging_only : bool
            If True then don't use as objective, only to track statistics from the simulation.

        """
        curr_rank = self.max_rank

        # if fitness is not added first, shift every other objective "down" in importance
        if name == "fitness" and self.max_rank > 0:
            curr_rank = 0  # change the key to rank 0
            for rank in reversed(range(len(self))):
                self[rank+1] = self[rank]

        super(ObjectiveDict, self).__setitem__(curr_rank, {"name": name,
                                                           "maximize": maximize,
                                                           "tag": xml_format(tag) if tag is not None else None,
                                                           "worst_value": -10e6 if maximize else 10e6,
                                                           "node_func": node_func,
                                                           "output_node_name": output_node_name,
                                                           "logging_only": logging_only})

        # TODO: logging_only 'objectives' should be a separate 'SimStats' class
        self.max_rank += 1
