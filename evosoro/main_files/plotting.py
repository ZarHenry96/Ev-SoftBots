import os
import sys
sys.path.append(os.getcwd() + "/../..")
from evosoro.tools.data_analysis import get_fitness_trends, plot_fitness_trends

# directory names
materials_1 = "./basic_evolution_pareto_data/allIndividualsData"

mat1_fitness_df = get_fitness_trends(materials_1)

plot_fitness_trends(mat1_fitness_df, "materials_evolution_fitness_trends")