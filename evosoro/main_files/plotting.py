from evosoro.tools.data_analysis import get_fitness_trends, plot_fitness_trends

# directory names
materials_1 = "./materials_evolution_data/allIndividualsData"
materials_2 = "./minimize_materials_evolution_data/allIndividualsData"

mat1_fitness_df = get_fitness_trends(materials_1)
#mat2_fitness_df = get_fitness_trends(materials_2)

plot_fitness_trends(mat1_fitness_df, "materials_evolution_fitness_trends")
#plot_fitness_trends(mat2_fitness_df, "minimize_materials_evolution_fitness_trends")
