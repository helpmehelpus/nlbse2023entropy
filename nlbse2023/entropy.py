import json
import logging
import sys
from math import log2, inf
from constants import *
from dataframe import create_dataframe, is_single_comment_node_ast_edge

logger = logging.getLogger('commit_entropy_historical')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def entropy(source_dataframe, distribution_dataframe, same_context=False):
    # If source data frame has a single row -> shannon_entropy = 0 (no surprise)
    logger.debug(f'calculating entropy metrics')

    if len(source_dataframe['edge'].unique()) == 1:
        logger.warning(f'datafram has only one type of edge, so entropy is zero')
        return 0

    shannon_entropy = 0

    if same_context:
        for idx, row in source_dataframe.iterrows():
            # For each row in target data frame, get the frequency
            edge_relative_freq_in_file = row['relative_frequency']
            shannon_entropy += edge_relative_freq_in_file * log2(edge_relative_freq_in_file)
    else:
        for idx, row in source_dataframe.iterrows():
            edge_relative_freq_in_file = row['relative_frequency']
            edge_relative_freq_in_dist_row = distribution_dataframe.loc[
                distribution_dataframe["edge"] == row["edge"], 'relative_frequency'].to_list()

            if len(edge_relative_freq_in_dist_row) == 0:
                logger.error(f'edge not found in context. this should not happen')
                return inf

            edge_relative_freq_in_dist = edge_relative_freq_in_dist_row[0]

            logger.debug(f'edge {row["edge"]} freq in file: {edge_relative_freq_in_file}, freq in project: {edge_relative_freq_in_dist}')

            frequency_quotinent = edge_relative_freq_in_file / edge_relative_freq_in_dist
            # If quotient is 1, this most likely means the project has a single file, so the contribution to entropy is that of the file
            if frequency_quotinent == 1:
                logger.debug(f'edge {row["edge"]} is only present in file context. Not in rest of project right now.')
                shannon_entropy += edge_relative_freq_in_file * log2(edge_relative_freq_in_file)
            else:
                shannon_entropy += frequency_quotinent * log2(frequency_quotinent)

    return -shannon_entropy


def calculate_entropy_metrics(larger_context, file_context=None):
    entropy_metrics = {
        AST_EDGE_FILE_KEY: 0,
        AST_EDGE_FILE_NORMALISED_KEY: 0,
        # AST_EDGE_PROJECT_KEY: 0,
        # AST_EDGE_PROJECT_NORMALISED_KEY: 0,
        TOKEN_FILE_KEY: 0,
        TOKEN_FILE_NORMALISED_KEY: 0,
        # TOKEN_PROJECT_KEY: 0,
        # TOKEN_PROJECT_NORMALISED_KEY: 0,
        TOKEN_NO_KEYWORDS_FILE_KEY: 0,
        TOKEN_NO_KEYWORDS_FILE_NORMALISED_KEY: 0,
        # TOKEN_NO_KEYWORDS_PROJECT_KEY: 0,
        # TOKEN_NO_KEYWORDS_PROJECT_NORMALISED_KEY: 0,
        TOKEN_NO_KEYWORDS_NO_NUMBERS_FILE_KEY: 0,
        TOKEN_NO_KEYWORDS_NO_NUMBER_FILE_NORMALISED_KEY: 0,
        # TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_KEY: 0,
        # TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_NORMALISED_KEY: 0,
    }

    # logger.debug(f'larger_context IS \n {json.dumps(larger_context, sort_keys=True, indent=4)}')
    # logger.debug(f'file_context IS \n {json.dumps(file_context, sort_keys=True, indent=4)}')

    if file_context is None:
        logger.info(f'no context available to get histograms from. file was probably deleted')
        return entropy_metrics

    max_ast_entropy_file_context = log2(len(file_context[AST_EDGE_HISTOGRAM_KEY]))

    # logger.debug(f'max entropy larger: {max_ast_entropy_larger_context}, max entropy file {max_ast_entropy_file_context}')

    if file_context is None:
        logger.error(f'no context available to get histograms from')
        return entropy_metrics

    # Extract these functions later
    # Calculate AST entropy
    if file_context[AST_EDGE_HISTOGRAM_KEY] is None:
        logger.error(f'no ast edge histogram available')
        entropy_ast_edge_file = 0
    else:
        file_ast_edges_df = create_dataframe(file_context[AST_EDGE_HISTOGRAM_KEY])
        # If ast only has the comment block, it has no entropy
        if is_single_comment_node_ast_edge(file_ast_edges_df):
            logger.debug(f'only comments in file. its ast entropy should be 0, and so should the normalised entropy')
            entropy_ast_edge_file = 0
            entropy_ast_edge_file_normalised = 0
        else:
            entropy_ast_edge_file = entropy(file_ast_edges_df, file_ast_edges_df, same_context=True)
            entropy_ast_edge_file_normalised = entropy_ast_edge_file / max_ast_entropy_file_context

    # Calculate TOKEN entropy
    if file_context[TOKEN_HISTOGRAM_KEY] is None:
        logger.error(f'no tokens available')
        entropy_token_file = 0
    else:
        file_token_df = create_dataframe(file_context[TOKEN_HISTOGRAM_KEY])
        if len(file_token_df.index) == 1:
            logger.debug(f'single token in file. it is meaningless, so gets zero entropy')
            entropy_token_file = 0
            entropy_token_file_normalised = 0
        else:
            entropy_token_file = entropy(file_token_df, file_token_df, same_context=True)
            entropy_token_file_normalised = entropy_token_file / log2(len(file_token_df.index))

    # Calculate TOKEN entropy (no keywords)
    if file_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY] is None:
        logger.error(f'no tokens other than keywords available')
        entropy_token_no_keywords_file = 0
    else:
        file_token_no_keywords_df = create_dataframe(file_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY])
        if len(file_token_no_keywords_df.index) == 1:
            logger.debug(f'single token in file (no keywords). it is meaningless, so gets zero entropy')
            entropy_token_no_keywords_file = 0
            entropy_token_no_keywords_file_normalised = 0
        else:
            entropy_token_no_keywords_file = entropy(file_token_no_keywords_df, file_token_no_keywords_df,
                                                     same_context=True)
            entropy_token_no_keywords_file_normalised = entropy_token_no_keywords_file / log2(
                len(file_token_no_keywords_df.index))

    # Calculate token entropy (no keywords, no numbers)
    if file_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY] is None:
        logger.error(f'no tokens other than keywords or numbers avialable')
        entropy_token_no_keywords_no_numbers_file = 0
    else:
        file_token_no_keywords_no_numbers_df = create_dataframe(
            file_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY])
        if len(file_token_no_keywords_no_numbers_df.index) == 1:
            logger.debug(f'single token (no keywords, no numbers), meaningless. zero entropy')
            entropy_token_no_keywords_no_numbers_file = 0
            entropy_token_no_keywords_no_numbers_file_normalised = 0
        else:
            entropy_token_no_keywords_no_numbers_file = entropy(file_token_no_keywords_no_numbers_df,
                                                                file_token_no_keywords_no_numbers_df, same_context=True)
            entropy_token_no_keywords_no_numbers_file_normalised = entropy_token_no_keywords_no_numbers_file / log2(len(file_token_no_keywords_no_numbers_df.index))

    project_ast_edges_df = create_dataframe(larger_context[AST_EDGE_HISTOGRAM_KEY])
    if project_ast_edges_df is None:
        logger.error(f'no dataframe available for project context. this is fatal')
        raise 'rato'

    # Project dataframes
    project_token_df = create_dataframe(larger_context[TOKEN_HISTOGRAM_KEY])
    project_token_no_keywords_df = create_dataframe(larger_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY])
    project_token_no_keywords_and_numbers_df = create_dataframe(
        larger_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY])

    # Project entropies
    # entropy_ast_edge_project = entropy(file_ast_edges_df, project_ast_edges_df)
    # entropy_token_project = entropy(file_token_df, project_token_df)
    # entropy_token_no_keywords_project = entropy(file_token_no_keywords_df, project_token_no_keywords_df)
    # entropy_token_no_keywords_no_numbers_project = entropy(file_token_no_keywords_no_numbers_df,
    #                                                        project_token_no_keywords_and_numbers_df)

    entropy_metrics[AST_EDGE_FILE_KEY] = entropy_ast_edge_file
    entropy_metrics[AST_EDGE_FILE_NORMALISED_KEY] = entropy_ast_edge_file_normalised

    # entropy_metrics[AST_EDGE_PROJECT_KEY] = entropy_ast_edge_project
    # entropy_metrics[AST_EDGE_PROJECT_NORMALISED_KEY] = entropy_ast_edge_project / log2(
    #     len(project_ast_edges_df.index))

    entropy_metrics[TOKEN_FILE_KEY] = entropy_token_file
    entropy_metrics[TOKEN_FILE_NORMALISED_KEY] = entropy_token_file_normalised

    # entropy_metrics[TOKEN_PROJECT_KEY] = entropy_token_project
    # entropy_metrics[TOKEN_PROJECT_NORMALISED_KEY] = entropy_token_project / log2(len(project_token_df.index))

    entropy_metrics[TOKEN_NO_KEYWORDS_FILE_KEY] = entropy_token_no_keywords_file
    entropy_metrics[TOKEN_NO_KEYWORDS_FILE_NORMALISED_KEY] = entropy_token_no_keywords_file_normalised

    # entropy_metrics[TOKEN_NO_KEYWORDS_PROJECT_KEY] = entropy_token_no_keywords_project
    # entropy_metrics[TOKEN_NO_KEYWORDS_PROJECT_NORMALISED_KEY] = entropy_token_no_keywords_project / log2(len(project_token_no_keywords_df))

    entropy_metrics[TOKEN_NO_KEYWORDS_NO_NUMBERS_FILE_KEY] = entropy_token_no_keywords_no_numbers_file
    entropy_metrics[TOKEN_NO_KEYWORDS_NO_NUMBER_FILE_NORMALISED_KEY] = entropy_token_no_keywords_no_numbers_file_normalised

    # entropy_metrics[TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_KEY] = entropy_token_no_keywords_no_numbers_project
    # entropy_metrics[
    #     TOKEN_NO_KEYWORDS_NO_NUMBERS_PROJECT_NORMALISED_KEY] = entropy_token_no_keywords_no_numbers_project / log2(
    #     len(project_token_no_keywords_and_numbers_df.index))

    return entropy_metrics
