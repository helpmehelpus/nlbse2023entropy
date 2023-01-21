import re

from constants import JAVA_KEYWORDS
from spiral import ronin

def remove_parentheses(code_string):
    return code_string.replace("(", " ").replace(")", " ")


def remove_operators(code_string):
    return re.sub("[-+=<>!%/*|&~?:\\[\\]^]", " ", code_string)


def remove_delimiters(code_string):
    return code_string.replace("{", " ").replace("}", " ").replace(";", " ").replace(",", " ")


def split_words(code_strings):
    return ronin.split(code_strings)


def sanitise_string(a_string):
    return a_string.replace("\"", "").replace("'", "").replace("\n", "").replace("\t", "").replace("\\", "").replace(
        "#", "")


def sanitise(string_list):
    sanitised = list(map(lambda w: sanitise_string(w), string_list))
    return [word for word in sanitised if word]


def remove_java_keywords(string_list):
    return [word for word in string_list if word not in JAVA_KEYWORDS]


def remove_numbers(string_list):
    return [word for word in string_list if not word.isdigit()]


def remove_comments(file_string):
    return re.sub("(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)", "", file_string)


def normalise(a_string):
    without_parentheses = remove_parentheses(a_string)
    without_operators = remove_operators(without_parentheses)
    without_delimiters = remove_delimiters(without_operators)
    tokenised = split_words(without_delimiters)
    sanitised = sanitise(tokenised)

    return list(map(lambda w: w.lower(), sanitised))
