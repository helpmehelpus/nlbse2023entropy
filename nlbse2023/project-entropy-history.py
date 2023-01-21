import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

from constants import *

for project_name in EXPERIMENT_PROJECTS_LIST:
    print(f'Creating project entropy history plots for project: {project_name}')

    raw_df = pd.read_csv(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/raw/commit-entropy_historical-{project_name}.csv',
        index_col=[0])
    file_count_df = pd.read_csv(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/raw/commit-entropy_historical-{project_name}-file-count.csv',
        index_col=[0])

    entropy_aggregates = raw_df.groupby(['commits', 'commit_date'], as_index=False, sort=False) \
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

    entropy_aggregates['project_entropy_ast_edge_file_context'] = entropy_aggregates[
        'entropy_ast_edge_file_context'].cumsum()
    entropy_aggregates['project_entropy_token_file_context'] = entropy_aggregates['entropy_token_file_context'].cumsum()
    entropy_aggregates['project_entropy_token_no_keywords_file_context'] = entropy_aggregates[
        'entropy_token_no_keywords_file_context'].cumsum()
    entropy_aggregates['project_entropy_token_no_keywords_no_numbers_file_context'] = entropy_aggregates[
        'entropy_token_no_keywords_no_numbers_file_context'].cumsum()

    entropy_aggregates['file_count'] = entropy_aggregates['commits'].apply(
        lambda commit_hash: file_count_df.loc[file_count_df['commit_sha'] == commit_hash, 'file_count'].iloc[0])

    entropy_aggregates['project_entropy_ast_edge_file_context_per_file'] = entropy_aggregates[
                                                                               'project_entropy_ast_edge_file_context'] / \
                                                                           entropy_aggregates['file_count']
    entropy_aggregates['project_entropy_token_file_context_per_file'] = entropy_aggregates[
                                                                            'project_entropy_token_file_context'] / \
                                                                        entropy_aggregates['file_count']
    entropy_aggregates['project_entropy_token_no_keywords_file_context_per_file'] = entropy_aggregates[
                                                                                        'project_entropy_token_no_keywords_file_context'] / \
                                                                                    entropy_aggregates['file_count']
    entropy_aggregates['project_entropy_token_no_keywords_no_numbers_file_context_per_file'] = entropy_aggregates[
                                                                                                   'project_entropy_token_no_keywords_no_numbers_file_context'] / \
                                                                                               entropy_aggregates[
                                                                                                   'file_count']

    entropy_aggregates['number_of_commits'] = np.arange(len(entropy_aggregates))
    entropy_aggregates.to_csv(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/project-history/test-{project_name}.csv')

    project_entropy_history_fig = go.FigureWidget()
    project_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_ast_edge_file_context'],
        marker=dict(color="crimson", size=1),
        mode="markers",
        name='structural',
    ))
    project_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_file_context'],
        marker=dict(color="blue", size=1),
        mode="markers",
        name='textual'
    ))
    project_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_no_keywords_file_context'],
        marker=dict(color="black", size=1),
        mode="markers",
        name='textual_no_keywords'
    ))
    project_entropy_history_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_no_keywords_no_numbers_file_context'],
        marker=dict(color="green", size=1),
        mode="markers",
        name='textual_no_keywords_no_numbers'
    ))
    project_entropy_history_fig.update_layout(xaxis_title="commit#", yaxis_title="entropy", legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    project_entropy_history_fig.write_image(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/project-history/project-entropy-history.png')

    project_entropy_history_per_file_fig = go.FigureWidget()
    project_entropy_history_per_file_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_ast_edge_file_context_per_file'],
        marker=dict(color="crimson", size=1),
        mode="markers",
        name='structural'
    ))
    project_entropy_history_per_file_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_file_context_per_file'],
        marker=dict(color="blue", size=1),
        mode="markers",
        name='textual'
    ))
    project_entropy_history_per_file_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_no_keywords_file_context_per_file'],
        marker=dict(color="black", size=1),
        mode="markers",
        name='textual_no_keywords'
    ))
    project_entropy_history_per_file_fig.add_trace(go.Scatter(
        x=entropy_aggregates['number_of_commits'],
        y=entropy_aggregates['project_entropy_token_no_keywords_no_numbers_file_context_per_file'],
        marker=dict(color="green", size=1),
        mode="markers",
        name='textual_no_keywords_no_numbers'
    ))
    project_entropy_history_per_file_fig.update_layout(xaxis_title="commit#", yaxis_title="entropy", legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    project_entropy_history_per_file_fig.write_image(
        f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/project-history/project-entropy-history-per-file.png')
