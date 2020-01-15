import random
import math

import copy
import numpy as np
from scipy import spatial


def fit_tournament_selection(population, tournament_size=2):
    """Return a list of selected individuals from the population.

    The selection is based on the fitness values.

    Parameters
    ----------
    population : Population
        This provides the individuals for selection.
    tournament_size : number

    Returns
    -------
    new_population : list
        A list of selected individuals.

    """

    while len(population) > population.pop_size:
        indices = random.sample(range(len(population)), tournament_size)
        fitnesses = [population[i].fitness for i in indices]
        max_indx = np.argmin(fitnesses)

        population.pop(indices[max_indx])

    return population.individuals


def pareto_selection(population):
    """Return a list of selected individuals from the population.

    All individuals in the population are ranked by their level, i.e. the number of solutions they are dominated by.
    Individuals are added to a list based on their ranking, best to worst, until the list size reaches the target
    population size (population.pop_size).

    Parameters
    ----------
    population : Population
        This provides the individuals for selection.

    Returns
    -------
    new_population : list
        A list of selected individuals.

    """
    new_population = []

    # (re)compute dominance for each individual
    population.calc_dominance()

    # sort the population multiple times by objective importance
    population.sort_by_objectives()

    # divide individuals into "pareto levels":
    # pareto level 0: individuals that are not dominated,
    # pareto level 1: individuals dominated one other individual, etc.
    done = False
    pareto_level = 0
    while not done:
        this_level = []
        size_left = population.pop_size - len(new_population)
        for ind in population:
            if len(ind.dominated_by) == pareto_level:
                this_level += [ind]

        # add best individuals to the new population.
        # add the best pareto levels first until it is not possible to fit them in the new_population
        if len(this_level) > 0:
            if size_left >= len(this_level):  # if whole pareto level can fit, add it
                new_population += this_level

            else:  # otherwise, select by sorted ranking within the level
                new_population += [this_level[0]]
                while len(new_population) < population.pop_size:
                    random_num = random.random()
                    log_level_length = math.log(len(this_level))
                    for i in range(1, len(this_level)):
                        if math.log(i) / log_level_length <= random_num < math.log(i + 1) / log_level_length and \
                                        this_level[i] not in new_population:
                            new_population += [this_level[i]]
                            continue

        pareto_level += 1
        if len(new_population) == population.pop_size:
            done = True

    for ind in population:
        if ind in new_population:
            ind.selected = 1
        else:
            ind.selected = 0

    return new_population


def pareto_tournament_selection(population):
    """Reduce the population pairwise.

    Two individuals from the population are randomly sampled and the inferior individual is removed from the population.
    This process repeats until the population size is reduced to either the target population size (population.pop_size)
    or the number of non-dominated individuals / Pareto front (population.non_dominated_size).

    Parameters
    ----------
    population : Population
        This provides the individuals for selection.

    Returns
    -------
    new_population : list
        A list of selected individuals.

    """
    # population.add_random_individual()  # adding in random ind in algorithms.py
    population.calc_dominance()
    random.shuffle(population.individuals)
    print "The nondominated size is", population.non_dominated_size

    while len(population) > population.pop_size and len(population) > population.non_dominated_size:

        inds = random.sample(range(len(population)), 2)
        ind0 = population[inds[0]]
        ind1 = population[inds[1]]

        if population.dominated_in_multiple_objectives(ind0, ind1):
            print "(fit) {0} dominated by {1}".format(ind0.fitness, ind1.fitness)
            population.pop(inds[0])
        elif population.dominated_in_multiple_objectives(ind1, ind0):
            print "(fit) {1} dominated by {0}".format(ind0.fitness, ind1.fitness)
            population.pop(inds[1])
        # else:
        #     population.pop(random.choice(inds))

    population.sort_by_objectives()

    return population.individuals


def from_centroids_to_trajectory(centroids):
    trajectory = []
    for i in range(1, len(centroids)):
        trajectory.append(centroids[i] - centroids[i-1])
    return trajectory

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """
    Returns the angle in radians between vectors 'v1' and 'v2'::

    angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    angle_between((1, 0, 0), (1, 0, 0))
    0.0
    angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793

    Ref. https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)

    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def similarity(v1, v2):
    angle = angle_between(v1, v2)
    similarity = 0.0

    if angle > math.pi / 2.0:
        similarity = 1 - spatial.distance.cosine(v1, v2)

    return similarity