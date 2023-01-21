import json
import logging
import sys

from subprocess import check_output

logger = logging.getLogger('histogram-manager')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def get_ast_edges_histogram(file_path):
    """Calls JAR file to parse the file and produce a histogram of the AST edges"""
    java_parser_output = check_output(['java', '-Xmx8192M', '-jar', 'nodetransitions.jar', file_path]).decode('utf8')
    return json.loads(java_parser_output)


def create_histogram(string_list):
    histogram = {}
    for word in string_list:
        histogram[word] = histogram.get(word, 0) + 1
    return histogram


def add_histograms(target_histogram, source_histogram):
    """Adds histogram entries from source_histogram into target_histogram"""
    output_histogram = target_histogram
    for key in source_histogram.keys():
        if key in output_histogram.keys():
            output_histogram[key] = output_histogram[key] + source_histogram[key]
        else:
            output_histogram[key] = source_histogram[key]

    return output_histogram


def subtract_histograms(target_histogram, source_histogram):
    """Adds histogram entries from source_histogram into target_histogram"""
    output_histogram = target_histogram
    for key in source_histogram.keys():
        if key in target_histogram.keys():
            if output_histogram[key] < source_histogram[key]:
                logger.error(f'this is very strange. freq in target {output_histogram[key]} versus {source_histogram[key]}')
                output_histogram[key] = 0
            else:
                output_histogram[key] = output_histogram[key] - source_histogram[key]
        else:
            logger.error(f'target_histogram is missing key {key} from source_histogram')

    return output_histogram
