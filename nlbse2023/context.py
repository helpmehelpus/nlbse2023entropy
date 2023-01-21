import json
import logging
import os

import sys
import redis

from constants import *
from histogram import get_ast_edges_histogram, create_histogram, add_histograms, subtract_histograms
from parser import get_file_string
from tokeniser import normalise, remove_java_keywords, remove_numbers

logger = logging.getLogger('context-manager')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

redis_client = redis.Redis(host='localhost', port=6379)


def create_file_context(file_path):
    """Returns dicts representing histograms of AST edges, or tokens"""
    ast_edges_histogram = get_ast_edges_histogram(file_path)
    if not ast_edges_histogram:
        logger.error(f'unable to parse {file_path}, returning empty context')
        return None

    file_string = get_file_string(file_path)
    tokenised_code = normalise(file_string)

    if len(tokenised_code) == 0:
        logger.error(f'no legal tokens for file {file_path}, returning empty context')
        return None

    tokenised_without_keywords = remove_java_keywords(tokenised_code)
    tokenised_without_keywords_and_numbers = remove_numbers(tokenised_without_keywords)

    token_histogram = create_histogram(tokenised_code)
    token_no_keywords_histogram = create_histogram(tokenised_without_keywords)
    token_no_keywords_no_numbers_histogram = create_histogram(tokenised_without_keywords_and_numbers)

    file_context = {
        AST_EDGE_HISTOGRAM_KEY: ast_edges_histogram,
        TOKEN_HISTOGRAM_KEY: token_histogram,
        TOKEN_HISTOGRAM_NO_KEYWORDS_KEY: token_no_keywords_histogram,
        TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY: token_no_keywords_no_numbers_histogram,
    }

    logger.info(f'successfully created file context for {file_path}')
    return file_context


def add_to_context(target_context, source_context):
    return {
        AST_EDGE_HISTOGRAM_KEY: add_histograms(target_context[AST_EDGE_HISTOGRAM_KEY], source_context[AST_EDGE_HISTOGRAM_KEY]),
        TOKEN_HISTOGRAM_KEY: add_histograms(target_context[TOKEN_HISTOGRAM_KEY], source_context[TOKEN_HISTOGRAM_KEY]),
        TOKEN_HISTOGRAM_NO_KEYWORDS_KEY: add_histograms(target_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY],
                                                      source_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY]),
        TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY: add_histograms(target_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY],
                                                     source_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY])
    }


def remove_from_context(target_context, source_context):
    return {
        AST_EDGE_HISTOGRAM_KEY: subtract_histograms(target_context[AST_EDGE_HISTOGRAM_KEY], source_context[AST_EDGE_HISTOGRAM_KEY]),
        TOKEN_HISTOGRAM_KEY: subtract_histograms(target_context[TOKEN_HISTOGRAM_KEY], source_context[TOKEN_HISTOGRAM_KEY]),
        TOKEN_HISTOGRAM_NO_KEYWORDS_KEY: subtract_histograms(target_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY],
                                                           source_context[TOKEN_HISTOGRAM_NO_KEYWORDS_KEY]),
        TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY: subtract_histograms(target_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY],
                                                          source_context[TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY])
    }


def calculate_context_diff(updated_context, cached_context):
    diff = {
        AST_EDGE_HISTOGRAM_KEY: {},
        TOKEN_HISTOGRAM_KEY: {},
        TOKEN_HISTOGRAM_NO_KEYWORDS_KEY: {},
        TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY: {}
    }
    for histogram in updated_context.keys():
        for row in updated_context[histogram]:
            if row in cached_context[histogram].keys():
                diff[histogram][row] = updated_context[histogram][row] - cached_context[histogram][row]
            else:
                diff[histogram][row] = updated_context[histogram][row]

    for histogram in cached_context.keys():
        for row in cached_context[histogram]:
            if row not in updated_context[histogram].keys():
                diff[histogram][row] = - cached_context[histogram][row]

    return diff


def create_project_context(project_path, cache=True):
    """Parses all files present in the project. Used to build the project's histogram context in the first commit, or
    to take a snapshot of the entire project at this point in time"""

    logger.debug(f'creating project context')
    project_context = {
        AST_EDGE_HISTOGRAM_KEY: {},
        TOKEN_HISTOGRAM_KEY: {},
        TOKEN_HISTOGRAM_NO_KEYWORDS_KEY: {},
        TOKEN_HISTOGRAM_NO_KEYWORDS_NO_NUMBERS_KEY: {}
    }

    for root, dirs, files in os.walk(project_path):
        java_files = [f for f in files if f.endswith('.java')]
        for file in java_files:
            file_path = root + os.sep + file
            logger.debug(f'creating context for file {file_path}')
            file_context = create_file_context(file_path)

            if not file_context:
                logger.warning(f'unable to parse {file_path}, keeping project context as is')
                continue

            # CACHE STORE
            if cache:
                redis_client.set(file_path, json.dumps(file_context))
            # logger.debug(f'cached context of file {file_context}')

            # PROJECT CONTEXT
            project_context = add_to_context(project_context, file_context)

    logger.debug(f'finished creating project context')
    return project_context
