#!/usr/bin/python
"""

In this example we evolve running soft robots in a terrestrial environment using a standard version of the physics
engine (_voxcad). After running this program for some time, you can start having a look at some of the evolved
morphologies and behaviors by opening up some of the generated .vxa (e.g. those in
evosoro/evosoro/basic_data/bestSoFar/fitOnly) with ./evosoro/evosoro/_voxcad/release/VoxCad
(then selecting the desired .vxa file from "File -> Import -> Simulation")

The phenotype is here based on a discrete, predefined palette of materials, which are visualized with different colors
when robots are simulated in the GUI.

Materials are identified through a material ID:
0: empty voxel, 1: passiveSoft (light blue), 2: passiveHard (blue), 3: active+ (red), 4:active- (green)

Active+ and Active- voxels are in counter-phase.


Additional References
---------------------

This setup is similar to the one described in:

    Cheney, N., MacCurdy, R., Clune, J., & Lipson, H. (2013).
    Unshackling evolution: evolving soft robots with multiple materials and a powerful generative encoding.
    In Proceedings of the 15th annual conference on Genetic and evolutionary computation (pp. 167-174). ACM.

    Related video: https://youtu.be/EXuR_soDnFo

"""
import random
import numpy as np
import subprocess as sub
from functools import partial
import os
import sys

# Appending repo's root dir in the python path to enable subsequent imports
sys.path.append(os.getcwd() + "/../..")

from evosoro.base import Sim, Env, ObjectiveDict
from evosoro.controller import Controller
from evosoro.networks import CPPN
from evosoro.softbot import Genotype, Phenotype, Population
from evosoro.tools.algorithms import ControllerOptimization, ParetoOptimization
from evosoro.tools.utils import count_occurrences, make_material_tree
from evosoro.tools.checkpointing import continue_from_checkpoint
from evosoro.tools.selection import pareto_selection, fit_tournament_selection

VOXELYZE_VERSION = '_voxcad'
sub.call("cp ../" + VOXELYZE_VERSION + "/voxelyzeMain/voxelyze .", shell=True)

NUM_RANDOM_INDS = 1  # Number of random individuals to insert each generation
MAX_GENS = 20  # Number of generations (the first one is excluded)
POPSIZE = 15  # Population size (number of individuals in the population)
IND_SIZE = (6, 6, 6)  # Bounding box dimensions (x,y,z). e.g. (6, 6, 6) -> workspace is a cube of 6x6x6 voxels
SIM_TIME = 5  # (seconds), including INIT_TIME!
INIT_TIME = 1
DT_FRAC = 0.9  # Fraction of the optimal integration step. The lower, the more stable (and slower) the simulation.

INIT_TEMP_AMPL = 14
INIT_TEMP_PERIOD = 0.25
INIT_MUSCLES_CTE = 0.01

ENV_SIZE = (50, 50, 6) # Size of the environment including the softbot
INIT_NUM_OBSTACLES = 1

TIME_TO_TRY_AGAIN = 45  # (seconds) wait this long before assuming simulation crashed and resending
MAX_EVAL_TIME = 120  # (seconds) wait this long before giving up on evaluating this individual
SAVE_LINEAGES = False
MAX_TIME = 8  # (hours) how long to wait before autosuspending
EXTRA_GENS = 0  # extra gens to run when continuing from checkpoint

RUN_DIR = "evolution_vs_env_controller_0.01_pareto_17_constraint_bone_data"  # Results subdirectory
RUN_NAME = "Environment"
CHECKPOINT_EVERY = 1  # How often to save an snapshot of the execution state to later resume the algorithm
SAVE_POPULATION_EVERY = 1  # How often (every x generations) we save a snapshot of the evolving population

SEED = 17
random.seed(SEED)  # Initializing the random number generator for reproducibility
np.random.seed(SEED)


# Defining a custom genotype, inheriting from base class Genotype
class MyGenotype(Genotype):
    def __init__(self):
        # We instantiate a new genotype for each individual which must have the following properties
        Genotype.__init__(self, orig_size_xyz=IND_SIZE)

        # The genotype consists of :
        # - a single Compositional Pattern Producing Network (CPPN), with multiple inter-dependent outputs determining
        #   the material constituting each voxel (e.g. two types of active voxels, actuated with a different phase, two
        #   types of passive voxels, softer and stiffer). The material IDs that you will see in the phenotype mapping
        #   dependencies refer to a predefined palette of materials currently hardcoded in tools/read_write_voxelyze.py:
        #   (0: empty, 1: passiveSoft, 2: passiveHard, 3: active+, 4:active-), but this can be changed.
        # - a controller instance
        self.add_network(CPPN(output_node_names=["shape", "muscleOrTissue", "muscleType", "tissueType"]))

        self.to_phenotype_mapping.add_map(name="material", tag="<Data>", func=make_material_tree,
                                          dependency_order=["shape", "muscleOrTissue", "muscleType", "tissueType"], output_type=int)  # BUGFIX: "tissueType" was not listed

        self.to_phenotype_mapping.add_output_dependency(name="shape", dependency_name=None, requirement=None,
                                                        material_if_true=None, material_if_false="0")

        self.to_phenotype_mapping.add_output_dependency(name="muscleOrTissue", dependency_name="shape",
                                                        requirement=True, material_if_true=None, material_if_false=None)  # BUGFIX: was material_if_false=1

        self.to_phenotype_mapping.add_output_dependency(name="tissueType", dependency_name="muscleOrTissue",
                                                        requirement=False, material_if_true="1", material_if_false="2")

        self.to_phenotype_mapping.add_output_dependency(name="muscleType", dependency_name="muscleOrTissue",
                                                        requirement=True, material_if_true="3", material_if_false="4")

        self.controller = Controller(INIT_TEMP_AMPL, INIT_TEMP_PERIOD, INIT_MUSCLES_CTE)


# Define a custom phenotype, inheriting from the Phenotype class
class MyPhenotype(Phenotype):
    def is_valid(self, min_percent_full=0.3, min_percent_tissue=0.1, min_percent_muscle=0.1):
        # override super class function to redefine what constitutes a valid individuals
        for name, details in self.genotype.to_phenotype_mapping.items():
            if np.isnan(details["state"]).any():
                return False
            if name == "material":
                state = details["state"]
                # Discarding the robot if it doesn't have at least a given percentage of non-empty voxels
                if np.sum(state > 0) < np.product(self.genotype.orig_size_xyz) * min_percent_full:
                    return False

                # Discarding the robot if it doesn't have at least a given percentage of tissues (materials 1 and 2)
                if count_occurrences(state, [1, 2]) < np.sum(state > 0) * min_percent_tissue:
                    return False

                # Discarding the robot if it doesn't have at least one bone (material 2)
                if count_occurrences(state, [2]) == 0:
                    return False

                # Discarding the robot if it doesn't have at least a given percentage of muscles (materials 3 and 4)
                if count_occurrences(state, [3, 4]) < np.sum(state > 0) * min_percent_muscle:
                    return False

        return True


# Setting up the simulation object
my_sim = Sim(dt_frac=DT_FRAC, simulation_time=SIM_TIME, fitness_eval_init_time=INIT_TIME)

# Setting up the environment object
my_env = Env(obstacles=True, ind_size=IND_SIZE, env_size=ENV_SIZE, init_num_obstacles=INIT_NUM_OBSTACLES,
             time_between_traces=0.1)

# Now specifying the objectives for the optimization.
# Creating an objectives dictionary
my_objective_dict = ObjectiveDict()

'''
# Adding an objective named "L-coeff", which we want to maximize. This information is returned by Voxelyze
# in a fitness .xml file, with a tag named "LCoefficient"
my_objective_dict.add_objective(name="fitness", maximize=True, tag="<LCoefficient>")
'''

# Adding an objective named "fitness", which we want to maximize. This information is returned by Voxelyze
# in a fitness .xml file, with a tag named "MaxXYDist"
my_objective_dict.add_objective(name="fitness", maximize=True, tag="<MaxXYDist>")

# Adding an objective named "L-coeff", which we want to maximize. This information is returned by Voxelyze
# in a fitness .xml file, with a tag named "LCoefficient"
my_objective_dict.add_objective(name="L-coeff", maximize=True, tag="<LCoefficient>")

# Add an objective to minimize the age of solutions: promotes diversity
my_objective_dict.add_objective(name="age", maximize=False, tag=None)


'''
# Adding another objective named "energy", which should be minimized.
# This information is not returned by Voxelyze (tag=None): it is instead computed in Python.
# by counting the occurrences of active materials (materials number 3 and 4)
my_objective_dict.add_objective(name="energy", maximize=False, tag=None,
                                node_func=partial(count_occurrences, keys=[3, 4]),
                                output_node_name="material")
'''

# Initializing a population of SoftBots
my_pop = Population(my_objective_dict, MyGenotype, MyPhenotype, pop_size=POPSIZE)

# Setting up our optimization
'''
my_optimization = ParetoOptimization(my_sim, my_env, my_pop)
'''
my_optimization = ControllerOptimization(my_sim, my_env, my_pop, selection_func=pareto_selection)

# And, finally, our main
if __name__ == "__main__":

    # Checkpointing mechanism
    if not os.path.isfile("./" + RUN_DIR + "/pickledPops/Gen_0.pickle"):
        # start optimization
        my_optimization.run(max_hours_runtime=MAX_TIME, max_gens=MAX_GENS, num_random_individuals=NUM_RANDOM_INDS,
                            directory=RUN_DIR, name=RUN_NAME, max_eval_time=MAX_EVAL_TIME,
                            time_to_try_again=TIME_TO_TRY_AGAIN, checkpoint_every=CHECKPOINT_EVERY,
                            save_vxa_every=SAVE_POPULATION_EVERY, save_lineages=SAVE_LINEAGES)

    else:
        continue_from_checkpoint(directory=RUN_DIR, additional_gens=EXTRA_GENS, max_hours_runtime=MAX_TIME,
                                 max_eval_time=MAX_EVAL_TIME, time_to_try_again=TIME_TO_TRY_AGAIN,
                                 checkpoint_every=CHECKPOINT_EVERY, save_vxa_every=SAVE_POPULATION_EVERY,
                                 save_lineages=SAVE_LINEAGES)


