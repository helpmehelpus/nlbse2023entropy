import logging
import sys

from constants import *

logger = logging.getLogger('project-data-manager')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

def initialize_project_data_object():
    return {
        'commits': [],
        'previous_commits': [],
        'old_file_paths': [],
        'new_file_paths': [],
        'modified_files_added_lines': [],
        'modified_file_deleted_lines': [],
        'modified_files_nloc': [],
        'modified_files_complexity': [],
        'modified_files_token_count': [],
        'commit_messages': [],
        'commit_date': [],
        AST_EDGE_FILE_KEY: [],
        AST_EDGE_FILE_NORMALISED_KEY: [],
        # AST_EDGE_PROJECT_KEY: [],
        # AST_EDGE_PROJECT_NORMALISED_KEY: [],
        TOKEN_FILE_KEY: [],
        TOKEN_FILE_NORMALISED_KEY: [],
        # TOKEN_PROJECT_KEY: [],
        # TOKEN_PROJECT_NORMALISED_KEY: [],
        TOKEN_NO_KEYWORDS_FILE_KEY: [],
        TOKEN_NO_KEYWORDS_FILE_NORMALISED_KEY: [],
        # TOKEN_NO_KEYWORDS_PROJECT_KEY: [],
        # TOKEN_NO_KEYWORDS_PROJECT_NORMALISED_KEY: [],
        TOKEN_NO_KEYWORDS_NO_NUMBERS_FILE_KEY: [],
        TOKEN_NO_KEYWORDS_NO_NUMBER_FILE_NORMALISED_KEY: [],
        # TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_KEY: [],
        # TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_NORMALISED_KEY: [],
    }


def update_project_data(project_data_object, entropy_metrics, metadata):
    updated_data_object = project_data_object
    for key in entropy_metrics.keys():
        updated_data_object[key].append(entropy_metrics[key])

    modified_file = metadata['modified_file']
    commit = metadata['commit']

    updated_data_object['commits'].append(commit.hash)
    updated_data_object['previous_commits'].append(metadata['previous_commit'])
    updated_data_object['old_file_paths'].append(modified_file.old_path)
    updated_data_object['new_file_paths'].append(modified_file.new_path)
    updated_data_object['modified_files_added_lines'].append(modified_file.added_lines)
    updated_data_object['modified_file_deleted_lines'].append(modified_file.deleted_lines)
    updated_data_object['modified_files_nloc'].append(modified_file.nloc)
    updated_data_object['modified_files_complexity'].append(modified_file.complexity)
    updated_data_object['modified_files_token_count'].append(modified_file.token_count)
    updated_data_object['commit_messages'].append(commit.msg)
    updated_data_object['commit_date'].append(metadata['commit_date'])

    return updated_data_object
