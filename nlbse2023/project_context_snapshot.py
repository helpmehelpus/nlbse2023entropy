import csv
import git
import logging
import os
import pandas as pd
import shutil
import sys

from pathlib import Path
from pydriller import Git

from context import create_project_context

INPUT_PROJECTS_ROOT = '/home/adriano/Projects/phd/code-java-projects'
EDGE_ABSOLUTE_FREQUENCY_PATH = 'edge-absolute-frequency'
PROJECT_SNAPSHOT = 'project-snapshot'
GITHUB_URL = 'https://github.com'

logger = logging.getLogger('commit_project_context_snapshot')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def get_column_name(key):
    if 'edge' in key:
        return 'edge'
    return 'token'


def create_project_snapshot(project_name, project_branch):
    project_full_path = INPUT_PROJECTS_ROOT + os.sep + project_name

    project_snapshot_path = PROJECT_SNAPSHOT + os.sep + project_name

    if os.path.isdir(project_snapshot_path):
        shutil.rmtree(os.path.join(Path.cwd(), project_snapshot_path))
    os.makedirs(project_snapshot_path)

    if os.path.isdir(project_full_path):
        shutil.rmtree(project_full_path)
    os.makedirs(project_full_path)

    logger.info(f'cloning {project_name}')
    project_repo_path = GITHUB_URL + os.sep + project_name
    git.Git(project_full_path).clone(project_repo_path)

    github = Git(project_full_path + os.sep + project_name.split("/")[-1])
    github.checkout(project_branch)

    project_context = create_project_context(project_full_path)
    logger.info(f'finished creating project context')

    for key in project_context.keys():
        df = pd.DataFrame(project_context[key].items(), columns=['edge', 'absolute_frequency'])
        sum_frequencies = df['absolute_frequency'].sum()
        # TYPO HERE. FIX IN build_global_context()
        df['relative_frequeny'] = df['absolute_frequency'] / sum_frequencies
        output_path = project_snapshot_path + os.sep + key
        df.to_csv(fr'{output_path}.csv', index=False, header=True)


if __name__ == '__main__':
    create_project_snapshot('dbeaver/dbeaver', 'devel')
    #
    # with open('project.csv', newline='') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         print(row['name'], row['defaultBranch'])

    # project_names = ['brettwooldridge/hikaricp']
    # for name in project_names:
    #     create_project_snapshot(name)
