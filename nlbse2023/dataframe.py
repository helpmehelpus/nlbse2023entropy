import logging
import sys

import pandas as pd

logger = logging.getLogger('dataframe-manager')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def create_dataframe(histogram_dict):
    if not histogram_dict:
        logger.error(f'empty histogram for file. Maybe JavaParser was unable to properly parse, skipping')
        return None

    logger.debug(f'creating dataframe for histogram: \n {histogram_dict}')

    edges = []
    absolute_frequencies = []
    for key, value in histogram_dict.items():
        edges.append(key)
        absolute_frequencies.append(value)

    total_absolute_frequencies = sum(absolute_frequencies)
    relative_frequencies = map(lambda f: f / total_absolute_frequencies, absolute_frequencies)

    return pd.DataFrame({'edge': edges, 'absolute_frequency': absolute_frequencies,
                         'relative_frequency': relative_frequencies})


def is_single_comment_node_ast_edge(ast_dataframe):
    if len(ast_dataframe.index) == 1:
        if "CompilationUnit,BlockComment" in ast_dataframe["edge"].unique():
            return True
        if "CompilationUnit,LineComment" in ast_dataframe["edge"].unique():
            return True
    return False

