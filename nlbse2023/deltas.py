import os
from pathlib import Path
from constants import *
import pandas as pd

for project_name in EXPERIMENT_PROJECTS_LIST:
    raw_history_df = pd.read_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/raw/commit-entropy_historical-{project_name}.csv', index_col=[0])

    output_path = f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/deltas'

    if not os.path.exists(output_path):
        path = Path(output_path)
        path.mkdir(parents=True, exist_ok=True)

    raw_history_df['delta_entropy_ast_edge_file_context'] = raw_history_df['entropy_ast_edge_file_context'] - raw_history_df['entropy_ast_edge_file_context'].shift(-1)
    raw_history_df['delta_entropy_ast_edge_file_normalised'] = raw_history_df['entropy_ast_edge_file_normalised'] - raw_history_df['entropy_ast_edge_file_normalised'].shift(-1)
    raw_history_df['delta_entropy_token_file_context'] = raw_history_df['entropy_token_file_context'] - raw_history_df['entropy_token_file_context'].shift(-1)
    raw_history_df['delta_entropy_token_file_normalised'] = raw_history_df['entropy_token_file_normalised'] - raw_history_df['entropy_token_file_normalised'].shift(-1)
    raw_history_df['delta_entropy_token_no_keywords_file_context'] = raw_history_df['entropy_token_no_keywords_file_context'] - raw_history_df['entropy_token_no_keywords_file_context'].shift(-1)
    raw_history_df['delta_entropy_token_no_keywords_file_normalised'] = raw_history_df['entropy_token_no_keywords_file_normalised'] - raw_history_df['entropy_token_no_keywords_file_normalised'].shift(-1)
    raw_history_df['delta_entropy_token_no_keywords_no_numbers_file_context'] = raw_history_df['entropy_token_no_keywords_no_numbers_file_context'] - raw_history_df['entropy_token_no_keywords_no_numbers_file_context'].shift(-1)
    raw_history_df['delta_entropy_token_no_keywords_no_numbers_file_normalised'] = raw_history_df['entropy_token_no_keywords_no_numbers_file_normalised'] - raw_history_df['entropy_token_no_keywords_no_numbers_file_normalised'].shift(-1)

    raw_history_df.to_csv(f'/home/adriano/Projects/phd/surprisal-se/ast-edge-entropy/nlbse2023/experiment-data/{project_name}/deltas/commit-entropy_historical-{project_name}.csv')