import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xml.etree.cElementTree import parse


def get_output_values(filename, output_name):
    data = parse(filename).getroot().find('VXC').find('Structure').find(output_name)
    return [float(string) for layer in data for string in layer.text.split(', ') if string != ""]


def get_all_data(paths_to_files, delimiter="\t\t", lineterminator='\n', engine='python', drop_duplicates_subset=None):
    run = []
    df = pd.DataFrame()
    for n, path in enumerate(paths_to_files):
        this_df = pd.read_table(path, delimiter=delimiter, lineterminator=lineterminator, engine=engine)
        run += [n] * len(this_df)
        df = pd.concat([df, this_df])

        if drop_duplicates_subset is not None:
            start_length = len(df)
            df = df.drop_duplicates(subset=drop_duplicates_subset)
            num_duplicates = start_length - len(df)
            print "{} duplicates".format(num_duplicates)
            run = run[num_duplicates:]

    df['run'] = run
    return df


def combine_experiments(exp_dfs, names):
    condition = []
    for n in range(len(exp_dfs)):
        condition += [names[n]] * len(exp_dfs[n])
    df = pd.concat(exp_dfs)
    df['condition'] = condition
    return df


def plot_time_series(combined_exp_dfs, title):
    sns.tsplot(data=combined_exp_dfs, value="fitness", condition="condition", unit="run", time="gen")
    plt.title(title)
    plt.savefig("{}.pdf".format(title))


def get_fitness_trends(path_to_files, delimiter="\t\t", lineterminator='\n', engine='python'):
    all_files = [os.path.join(path_to_files, f) for f in os.listdir(path_to_files)]

    df = pd.concat(
        (pd.read_csv(f, delimiter=delimiter, lineterminator=lineterminator, engine=engine) for f in all_files))
    df = df[['gen', 'fitness']]
    df_mean = df.groupby('gen', as_index=False)['fitness'].mean().rename(columns={'fitness': 'avg'})
    df_max = df.groupby('gen', as_index=False)['fitness'].max().rename(columns={'fitness': 'max'})
    df_min = df.groupby('gen', as_index=False)['fitness'].min().rename(columns={'fitness': 'min'})
    df_median = df.groupby('gen', as_index=False)['fitness'].median().rename(columns={'fitness': 'median'})
    merged_df = pd.merge(pd.merge(df_mean, df_max, on='gen'), pd.merge(df_min, df_median, on='gen'), on='gen')
    fitness_df = pd.melt(merged_df, id_vars=['gen'], value_name='fitness', var_name='type', value_vars=['avg', 'max', 'min', 'median'])

    return fitness_df


def plot_fitness_trends(fitness_df, title):
    sns.lineplot(x='gen', y='fitness', hue='type', data=fitness_df)
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.legend(labels=['average', 'best', 'worst', 'median'])
    plt.savefig("{}.pdf".format(title))
    plt.show()
    plt.close()
