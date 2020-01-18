import os
import sys
sys.path.append(os.getcwd() + "/../..")
from evosoro.tools.data_analysis import get_fitness_trends, plot_fitness_trends

# directory names
materials_1 = "./materials_evolution_data/allIndividualsData"
materials_2 = "./materials_evolution_data_2/allIndividualsData"

mat1_fitness_df = get_fitness_trends(materials_1)
mat2_fitness_df = get_fitness_trends(materials_2)

plot_fitness_trends(mat1_fitness_df, "materials_evolution_fitness_trends")
plot_fitness_trends(mat2_fitness_df, "materials_evolution_fitness_trends_2")
