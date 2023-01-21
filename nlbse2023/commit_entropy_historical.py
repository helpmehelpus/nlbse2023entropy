import logging
import json
import os
import pandas as pd
import redis
import shutil
import sys

from pathlib import Path
from pydriller import Git, Repository

from context import create_project_context, create_file_context, add_to_context, remove_from_context, calculate_context_diff
from constants import *
from entropy import calculate_entropy_metrics
from project_data import initialize_project_data_object, update_project_data

redis_client = redis.Redis(host='localhost', port=6379)

logger = logging.getLogger('commit_entropy_historical')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def create_project_entropy_folder(project_history_path):
    if os.path.isdir(project_history_path):
        shutil.rmtree(os.path.join(Path.cwd(), project_history_path))

    os.makedirs(project_history_path)


GLOBAL_CONTEXT_EDGE_HISTOGRAM_KEY = 'edge_histogram'
GLOBAL_CONTEXT_TOKEN_HISTOGRAM_KEY = 'token_histogram'
GLOBAL_CONTEXT_TOKEN_NO_KEYWORDS_KEY = 'token_histogram_no_keywords_no_numbers'
GLOBAL_CONTEXT_TOKEN_NO_KEYWORDS_NO_NUMBERS_KEY = 'token_histogram_no_keywords_no_numbers'


def calculate_historical_entropy(project_full_path, default_branch):
    project_name = project_full_path.split("/")[-1]
    entropy_history_path = HISTORICAL_ENTROPY_ROOT + os.sep + project_name
    create_project_entropy_folder(entropy_history_path)

    github = Git(project_full_path)
    github.checkout(default_branch)
    previous_commit = None
    project_context = {}

    if os.path.isdir(entropy_history_path):
        shutil.rmtree(os.path.join(Path.cwd(), entropy_history_path))
    os.makedirs(entropy_history_path)

    project_data = initialize_project_data_object()

    for commit in Repository(project_full_path).traverse_commits():
        logger.info(f'checking out commit {commit.hash}')
        github.checkout(commit.hash)

        if previous_commit is None:
            logger.info(f'initial commit, building project context context')
            project_context = create_project_context(project_full_path)

        for modified_file in commit.modified_files:
            if not modified_file.filename.endswith('.java'):
                continue
            logger.info(f'modified file {modified_file.filename}')
            metadata = {
                'commit': commit,
                'previous_commit': previous_commit,
                'modified_file': modified_file
            }

            # old_path is not reliable to say if the file is new. If you add a new src/Whatever.java file in a commit
            # that is not the first one, old_path == new_path, and yet the file is new
            # old_path seems to only be None in the first commit (??)
            if modified_file.old_path is None:
                logger.info(f'new file {modified_file.new_path}, parsing')
                new_file_path = project_full_path + os.sep + modified_file.new_path
                new_file_context = create_file_context(new_file_path)

                if new_file_context is None:
                    logger.warning(f'no file context for new file, parsing has failed')
                    continue

                redis_client.set(new_file_path, json.dumps(new_file_context))
                project_context = add_to_context(project_context, new_file_context)
                logger.debug(f'finished updating project context for new file {modified_file.new_path}')

                entropy_metrics = calculate_entropy_metrics(project_context, new_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue

            # File was deleted. Retrieve histograms from cache, update context, wipe cache
            if modified_file.new_path is None:
                logger.info(f'file {modified_file.old_path} was deleted')
                deleted_file_path = project_full_path + os.sep + modified_file.old_path
                cached_file_object = redis_client.get(deleted_file_path)
                if cached_file_object is None:
                    # file was renamed at some point and its old cache reference is now dangling
                    # there is no way to retrieve the old file context in this case. since the cache reference is lost
                    # we cannot subtract from the context. this is expected to be a rare event, and should not impact
                    # final numbers.
                    # No need to wipe the cache, as a concurrent commit might use it before the commits are merged
                    # redis_client.delete(deleted_file_path)
                    logger.info(f'no cached contents for file {modified_file.old_path}. the file was probably renamed'
                                f'at some point and its cached contents are no longer retrievable')

                    entropy_metrics = calculate_entropy_metrics(project_context, None)
                    project_data = update_project_data(project_data, entropy_metrics, metadata)
                    redis_client.delete(deleted_file_path)
                    continue

                cached_deleted_file_context = json.loads(redis_client.get(deleted_file_path))
                project_context = remove_from_context(project_context, cached_deleted_file_context)
                redis_client.delete(deleted_file_path)

                logger.debug(f'finished updating project context for deleted file {modified_file.old_path}')

                entropy_metrics = calculate_entropy_metrics(project_context, None)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue
            # Same location, file contents changed. Need parsing to update
            # new files can fall here too. apparently has new_path == old_path if it is not in the first commit
            # Files that were deleted in previous commits, then reintroduced later on, end up falling here.
            if modified_file.new_path == modified_file.old_path:
                logger.info(f'file updated - old path {modified_file.old_path} new path {modified_file.new_path}')
                new_or_updated_file_path = project_full_path + os.sep + modified_file.new_path
                new_or_updated_file_context = create_file_context(new_or_updated_file_path)
                # Empty file
                if not new_or_updated_file_context:
                    logger.warning(f'no file context available for {modified_file.new_path}, skipping')
                    continue
                # if the contents have not been cached yet, the file is new. if the file is new, we cache its context,
                # add to the project context, cache it, and bail.
                cached_file_object = redis_client.get(new_or_updated_file_path)
                if cached_file_object is None:
                    logger.debug(f'file is not in cache, so it is new')
                    project_context = add_to_context(project_context, new_or_updated_file_context)
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))
                    entropy_metrics = calculate_entropy_metrics(project_context, new_or_updated_file_context)
                    project_data = update_project_data(project_data, entropy_metrics, metadata)
                    continue
                else:
                    cached_file_context = json.loads(cached_file_object)

                if cached_file_context is None:
                    logger.error('no cached context for updated file')

                if new_or_updated_file_context != cached_file_context:
                    logger.debug(f'context changed for file {modified_file.new_path}')
                    diff = calculate_context_diff(new_or_updated_file_context, cached_file_context)
                    logger.debug(f'diff between contexts is {json.dumps(diff, sort_keys=True, indent=4)}')
                    project_context = add_to_context(project_context, diff)
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))
                    logger.debug(f'finished updating project context for updated file {modified_file.new_path}')
                else:
                    logger.debug(f'unchanged context for file {modified_file.new_path}')
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))

                entropy_metrics = calculate_entropy_metrics(project_context, new_or_updated_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue

            # location changed. need to parse, diff with cached, add to project context
            if modified_file.new_path != modified_file.old_path:
                logger.info(f'file was moved from {modified_file.old_path} to {modified_file.new_path}')
                old_file_path = project_full_path + os.sep + modified_file.old_path
                new_file_path = project_full_path + os.sep + modified_file.new_path

                moved_file_context = create_file_context(new_file_path)
                if moved_file_context is None:
                    logger.warning(f'no context available for file {modified_file.new_path}, skipping')
                    continue

                project_context = add_to_context(project_context, moved_file_context)
                cached_file_object = redis_client.get(old_file_path)
                # File was moved and cannot find in cache: Java file was renamed. Since the file can have also changed,
                # we parse again and update
                if cached_file_object is None:
                    logger.debug(f'file {modified_file.old_path} was renamed to {modified_file.new_path}')
                    logger.debug(f'no cached version found for file {modified_file.new_path}, adding fresh to context')
                    project_context = add_to_context(project_context, moved_file_context)
                    redis_client.set(new_file_path, json.dumps(moved_file_context))
                    # Update reference to old file to contain the right context?
                    redis_client.set(old_file_path, json.dumps(moved_file_context))
                    entropy_metrics = calculate_entropy_metrics(project_context, moved_file_context)
                    project_data = update_project_data(project_data, entropy_metrics, metadata)
                    continue
                else:
                    cached_file_context = json.loads(cached_file_object)

                if moved_file_context != cached_file_context:
                    logger.debug('different context. caching updated context')
                    diff = calculate_context_diff(moved_file_context, cached_file_context)
                    project_context = add_to_context(project_context, diff)
                    redis_client.set(new_file_path, json.dumps(moved_file_context))
                    redis_client.set(old_file_path, json.dumps(moved_file_context))
                    redis_client.delete(old_file_path)
                else:
                    logger.debug(f'contexts were the same, file {modified_file.new_path} was just moved')

                logger.debug(f'finished updating project context for moved file {modified_file.new_path}')

                entropy_metrics = calculate_entropy_metrics(project_context, moved_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue

        previous_commit = commit.hash

    df = pd.DataFrame({k: v for k, v in project_data.items()})
    output_path = entropy_history_path + os.sep + 'commit-entropy_historical' + '-' + project_name
    df.to_csv(f'{output_path}.csv')

    # redis_client.flushall()
    # generalise me to main branch
    github.checkout(default_branch)
    logger.info(f'finished')


if __name__ == '__main__':
    # project_paths = ['/home/adriano/Projects/phd/code-java-projects/googlecontainertools/jib/jib']
    repo_path = sys.argv[1]
    default_branch = sys.argv[2]
    repo_name = repo_path.split('/')[-1]
    projects_root = '/home/adriano/Projects/phd/code-java-projects'
    project_root = projects_root + os.sep + repo_path + os.sep + repo_name
    calculate_historical_entropy(project_root, default_branch)
