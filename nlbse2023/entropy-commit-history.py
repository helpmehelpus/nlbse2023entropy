import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go

from constants import *
from pathlib import Path
from remove_outliers import remove_outliers

for project_name in EXPERIMENT_PROJECTS_LIST:
    print(f'Creating project entropy history plots for project: {project_name}')

    output_path = f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/commit-history'
    if not os.path.exists(output_path):
        path = Path(output_path)
        path.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/raw/commit-entropy_historical-{project_name}.csv', index_col=[0])

    entropy_aggregates = df.groupby(['commits', 'commit_date'], as_index=False, sort=False)\
        .agg(
          {
                'entropy_ast_edge_file_context': 'sum',
                'entropy_ast_edge_file_normalised': 'sum',
                'entropy_token_file_context': 'sum',
                'entropy_token_file_normalised': 'sum',
                'entropy_token_no_keywords_file_context': 'sum',
                'entropy_token_no_keywords_file_normalised': 'sum',
                'entropy_token_no_keywords_no_numbers_file_context': 'sum',
                'entropy_token_no_keywords_no_numbers_file_normalised': 'sum'
          })
    entropy_aggregates['number_of_commits'] = np.arange(len(entropy_aggregates))
    entropy_aggregates.to_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/commit-history/test-{project_name}.csv')

    commit_entropy_history_fig = go.FigureWidget()
    commit_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_ast_edge_file_context'],
        marker=dict(color="crimson", size=1),
        mode="markers",
        name='structural'
    ))
    commit_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_file_context'],
        marker=dict(color="blue", size=1),
        mode="markers",
        name='textual'
    ))
    commit_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_no_keywords_file_context'],
        marker=dict(color="black", size=1),
        mode="markers",
        name='textual_no_keywords'
    ))
    commit_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_no_keywords_no_numbers_file_context'],
        marker=dict(color="green", size=1),
        mode="markers",
        name='textual_no_keywords_no_numbers'
    ))
    commit_entropy_history_fig.write_image(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/commit-history/commit-entropy-history.png')

    commit_entropy_history_normalised_fig = go.FigureWidget()
    commit_entropy_history_normalised_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_ast_edge_file_normalised'],
        marker=dict(color="crimson", size=1),
        mode="markers",
        name='structural'
    ))
    commit_entropy_history_normalised_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_file_normalised'],
        marker=dict(color="blue", size=1),
        mode="markers",
        name='textual'
    ))
    commit_entropy_history_normalised_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_no_keywords_file_normalised'],
        marker=dict(color="black", size=1),
        mode="markers",
        name='textual_no_keywords'
    ))
    commit_entropy_history_normalised_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['entropy_token_no_keywords_no_numbers_file_normalised'],
        marker=dict(color="green", size=1),
        mode="markers",
        name='textual_no_keywords_no_numbers'
    ))
    commit_entropy_history_normalised_fig.write_image(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/commit-history/commit-entropy-history-normalised.png')


    # raw_history_df['delta_entropy_ast_edge_file_context'] = raw_history_df['entropy_ast_edge_file_context'] - raw_history_df['entropy_ast_edge_file_context'].shift(-1)


    # outliers_removed = remove_outliers(entropy_aggregates, ['entropy_ast_edge_file_context', 'entropy_ast_edge_file_normalised',
    #                                      'entropy_token_file_context', 'entropy_token_file_normalised',
    #                                      'entropy_token_no_keywords_file_context', 'entropy_token_no_keywords_file_normalised',
    #                                      'entropy_token_no_keywords_no_numbers_file_context', 'entropy_token_no_keywords_no_numbers_file_normalised'], 3)

    # sns.lineplot(data=outliers_removed, x='commit_date', y='entropy_ast_edge_file_context')
    # plt.savefig(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/commit-history/entropy_ast_edge_file_context_outliers_removed.png', dpi=300)


