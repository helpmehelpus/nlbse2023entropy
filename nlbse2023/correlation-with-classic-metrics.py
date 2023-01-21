import os

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from constants import *
from pathlib import Path

for project_name in EXPERIMENT_PROJECTS_LIST:
    print(f'Creating entropy correlations with classic metrics for project: {project_name}')

    raw_history_df = pd.read_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/raw/commit-entropy_historical-{project_name}.csv', index_col=[0])

    output_path = f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/correlations-classic'
    if not os.path.exists(output_path):
        path = Path(output_path)
        path.mkdir(parents=True, exist_ok=True)

    entropy_columns_df = raw_history_df[['entropy_ast_edge_file_context', 'entropy_token_file_context',
                                         'entropy_token_no_keywords_file_context', 'entropy_token_no_keywords_no_numbers_file_context',
                                         'modified_files_nloc', 'modified_files_complexity', 'modified_files_token_count']]


    corr_matrix = entropy_columns_df.corr()
    plt.figure(figsize=(5, 5))
    # print(len(ax))
    # print(fig)
    sns.heatmap(corr_matrix, annot=True, xticklabels=True, yticklabels=True, vmax=1, vmin=-1, cbar=False, cmap=sns.cubehelix_palette(start=3, rot=-.5, as_cmap=True, dark=0.5, light=0.99))
    title = project_name
    if project_name == 'material-components-android':
        title = 'mca'
    if project_name == 'deeplearning4j':
        title = 'dl4j'
    if project_name == 'arduino':
        title = 'ard'
    if project_name == 'grpc-java':
        title = 'grpc'
    if project_name == 'hikaricp':
        title = 'hikari'
    if project_name == 'mybatis-3':
        title = 'mbts'
    if project_name == 'realm-java':
        title = 'realm'
    if project_name == 'mockito':
        title = 'mckt'
    if project_name == 'skywalking':
        title = 'skyw'
    if project_name == 'thingsboard':
        title = 'thgsb'
    if project_name == 'lombok':
        title = 'lmbk'
    if project_name == 'redisson':
        title = 'rdsn'

    plt.title(title, fontsize=11)
    plt.savefig(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/correlations-classic/{project_name}-annotated.png', dpi=300, bbox_inches='tight')
    plt.close()
