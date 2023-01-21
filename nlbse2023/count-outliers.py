import os

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from constants import *
from pathlib import Path

total_outliers = None
count = 0

for project_name in EXPERIMENT_PROJECTS_LIST:
    print(f'Counting outliers for project: {project_name}')

    raw_history_df = pd.read_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/deltas/commit-entropy_historical-{project_name}.csv', index_col=[0])

    output_path = f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/outliers'
    if not os.path.exists(output_path):
        path = Path(output_path)
        path.mkdir(parents=True, exist_ok=True)

    entropy_columns_df = raw_history_df[['entropy_ast_edge_file_context', 'entropy_token_file_context',
                                         'entropy_token_no_keywords_file_context', 'entropy_token_no_keywords_no_numbers_file_context',
                                         'entropy_ast_edge_file_normalised', 'entropy_token_file_normalised',
                                         'entropy_token_no_keywords_file_normalised', 'entropy_token_no_keywords_no_numbers_file_normalised']]

    delta_entropy_aggregates = raw_history_df.groupby(['commits', 'commit_date'], as_index=False, sort=False) \
        .agg(
        {
            'delta_entropy_ast_edge_file_context': 'sum',
            'delta_entropy_ast_edge_file_normalised': 'sum',
            'delta_entropy_token_file_context': 'sum',
            'delta_entropy_token_file_normalised': 'sum',
            'delta_entropy_token_no_keywords_file_context': 'sum',
            'delta_entropy_token_no_keywords_file_normalised': 'sum',
            'delta_entropy_token_no_keywords_no_numbers_file_context': 'sum',
            'delta_entropy_token_no_keywords_no_numbers_file_normalised': 'sum'
        })
    delta_entropy_aggregates['number_of_commits'] = np.arange(len(delta_entropy_aggregates))

    Q1 = delta_entropy_aggregates.quantile(0.25)
    Q3 = delta_entropy_aggregates.quantile(0.75)
    IQR = Q3 - Q1
    total_commit_count = len(delta_entropy_aggregates.index)
    outliers = ((delta_entropy_aggregates < (Q1 - 3 * IQR)) | (delta_entropy_aggregates > (Q3 + 3 * IQR)))



    outliers_sum = outliers.sum()
    outliers_sum['commit_count'] = total_commit_count

    outliers.to_csv(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/outliers/{project_name}-outliers.csv')

    if total_outliers is None:
        total_outliers = outliers_sum
    else:
        total_outliers = total_outliers.add(outliers_sum, fill_value=0)

    outliers_sum['delta_entropy_ast_edge_file_context_ratio'] = outliers_sum['delta_entropy_ast_edge_file_context'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_ast_edge_file_normalised_ratio'] = outliers_sum['delta_entropy_ast_edge_file_normalised'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_file_context_ratio'] = outliers_sum['delta_entropy_token_file_context'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_file_normalised_ratio'] = outliers_sum['delta_entropy_token_file_normalised'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_no_keywords_file_context_ratio'] = outliers_sum['delta_entropy_token_no_keywords_file_context'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_no_keywords_file_normalised_ratio'] = outliers_sum[
                                                                      'delta_entropy_token_no_keywords_file_normalised'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_no_keywords_no_numbers_file_context_ratio'] = outliers_sum[
                                                                              'delta_entropy_token_no_keywords_no_numbers_file_context'] / len(
        delta_entropy_aggregates.index)
    outliers_sum['delta_entropy_token_no_keywords_no_numbers_file_normalised_ratio'] = outliers_sum[
                                                                                 'delta_entropy_token_no_keywords_no_numbers_file_normalised'] / len(
        delta_entropy_aggregates.index)

    outliers_sum.to_csv(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/outliers/{project_name}-extreme-outliers-sum.csv')

total_outliers.to_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/outliers/total-extreme-outliers.csv')