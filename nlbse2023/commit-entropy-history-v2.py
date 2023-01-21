import logging
import json
import os
import pandas as pd
import redis
import shutil
import sys

from pathlib import Path
from pydriller import Git, Repository

from context import create_project_context, create_file_context, add_to_context
from constants import *
from entropy import calculate_entropy_metrics
from project_data import initialize_project_data_object, update_project_data

redis_client = redis.Redis(host='localhost', port=6379)

logger = logging.getLogger('commit_entropy_historical')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def create_project_entropy_folder(project_history_path):
    if os.path.isdir(project_history_path):
        shutil.rmtree(os.path.join(Path.cwd(), project_history_path))

    os.makedirs(project_history_path)


def get_file_count(project_path):
    java_files_count = 0
    for root, dirs, files in os.walk(project_path):
        java_files_count += len([f for f in files if f.endswith('.java')])
    return java_files_count


def calculate_historical_entropy(project_full_path, branch):
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
    # Traverse the history in order
    commits = []
    file_count = []
    for commit in Repository(project_full_path).traverse_commits():
        logger.info(f'checking out commit {commit.hash} for project {project_name}')
        github.checkout(commit.hash)

        java_files_count = get_file_count(project_full_path)
        logger.info(f'there are {java_files_count} files in commit {commit.hash}')
        commits.append(commit.hash)
        file_count.append(java_files_count)

        if previous_commit is None:
            logger.info(f'commit {commit.hash} is the initial commit in the sequence. building project context')
            project_context = create_project_context(project_full_path)

        modified_java_files = [f for f in commit.modified_files if f.filename.endswith('.java')]
        logger.info(f'there are {len(modified_java_files)} modified files in commit {commit.hash}')
        for modified_file in modified_java_files:
            logger.info(f'file {modified_file.filename} was modified, old path: {modified_file.old_path}, new path: {modified_file.new_path} commit {commit.hash}')

            metadata = {
                'commit': commit,
                'previous_commit': previous_commit,
                'modified_file': modified_file,
                'commit_date': commit.committer_date
            }
            # old_path is not reliable to say if the file is new. If you add a new src/Whatever.java file in a commit
            # that is not the first one, old_path == new_path, and yet the file is new. old_path seems to only be None
            # for a new file in the first commit.
            if modified_file.old_path is None:
                logger.info(f'file {modified_file.new_path} nas no old path, parsing it')
                new_file_path = project_full_path + os.sep + modified_file.new_path
                new_file_context = create_file_context(new_file_path)
                # If it's not possible to get a file context, move to the next one
                if new_file_context is None:
                    logger.error(f'either no valid AST edges or no tokens in file {modified_file.new_path}')
                    continue
                # If there is a context, then it must be added to the project context, and cached
                project_context = add_to_context(project_context, new_file_context)
                # extract to cache store module
                logger.debug(f'caching contents of {new_file_path}')
                redis_client.set(new_file_path, json.dumps(new_file_context))

                logger.info(f'computing entropy metrics file {modified_file.new_path} commit {commit.hash}')
                entropy_metrics = calculate_entropy_metrics(project_context, new_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue
            # File was deleted. Retrieve histograms from cache, update context, wipe cache
            if modified_file.new_path is None:
                logger.info(f'file {modified_file.old_path} was deleted commit {commit.hash}')
                deleted_file_path = project_full_path + os.sep + modified_file.old_path
                cached_file_object = redis_client.get(deleted_file_path)
                if cached_file_object is None:
                    # file was renamed at some point and its old cache reference is now dangling
                    # there is no way to retrieve the old file context in this case. since the cache reference is lost
                    # we cannot subtract from the context. this is expected to be a rare event, and should not impact
                    # final numbers.
                    # No need to wipe the cache, as a concurrent commit might use it before the commits are merged
                    # redis_client.delete(deleted_file_path)
                    logger.warning(
                        f'no cached contents for file {modified_file.old_path}. the file was probably renamed'
                        f'at some point and its cached contents are no longer retrievable')

                    logger.info(f'computing zero entropy metrics for deleted file {modified_file.new_path} commit {commit.hash}')
                    entropy_metrics = calculate_entropy_metrics(project_context, None)
                    project_data = update_project_data(project_data, entropy_metrics, metadata)
                    redis_client.delete(deleted_file_path)
                    continue

                logger.debug(f'finished updating project context for deleted file {modified_file.old_path} commit {commit.hash}')
                entropy_metrics = calculate_entropy_metrics(project_context, None)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue
            # Same location, file contents changed. Need parsing to update. ew files can fall here too. apparently
            # new_path == old_path if it is not in the first commit. Files that were deleted in previous commits, then
            # reintroduced later on, end up falling here.
            if modified_file.new_path == modified_file.old_path:
                logger.info(f'file updated - old path {modified_file.old_path} new path {modified_file.new_path} commit {commit.hash}')
                new_or_updated_file_path = project_full_path + os.sep + modified_file.new_path
                new_or_updated_file_context = create_file_context(new_or_updated_file_path)
                # Empty file
                if not new_or_updated_file_context:
                    logger.warning(f'no file context available for {modified_file.new_path}, skipping')
                    continue
                # As soon as a context is available and non-empty, add it to project context
                project_context = add_to_context(project_context, new_or_updated_file_context)
                # if the contents have not been cached yet, the file is new. if the file is new, we cache its context,
                # add to the project context, cache it, and bail.
                cached_file_object = redis_client.get(new_or_updated_file_path)
                if cached_file_object is None:
                    logger.debug(f'file is not in cache, so it is new')
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))
                    entropy_metrics = calculate_entropy_metrics(project_context, new_or_updated_file_context)
                    project_data = update_project_data(project_data, entropy_metrics, metadata)
                    continue
                else:
                    cached_file_context = json.loads(cached_file_object)

                if cached_file_context is None:
                    logger.error('no cached context for updated file')

                if new_or_updated_file_context != cached_file_context:
                    logger.debug(f'context changed for file {modified_file.new_path} commit {commit.hash}')
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))
                    logger.info(f'finished updating project context for updated file {modified_file.new_path} commit {commit.hash}')
                else:
                    logger.info(f'unchanged context for file {modified_file.new_path} commit {commit.hash}')
                    redis_client.set(new_or_updated_file_path, json.dumps(new_or_updated_file_context))

                logger.debug(f'finished updating project context for updated file {modified_file.old_path} commit {commit.hash}')
                entropy_metrics = calculate_entropy_metrics(project_context, new_or_updated_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue
            # location changed. need to parse, diff with cached, add to project context
            if modified_file.new_path != modified_file.old_path:
                logger.info(f'file was moved from {modified_file.old_path} to {modified_file.new_path} commit {commit.hash}')
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
                    logger.info(f'file {modified_file.old_path} was renamed to {modified_file.new_path}')
                    logger.info(
                        f'no cached version found for file {modified_file.new_path}, adding fresh to context')
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
                    logger.info(f'different context between cached and built context for file {modified_file.filename}. caching updated context commit {commit.hash}')
                    redis_client.set(new_file_path, json.dumps(moved_file_context))
                    redis_client.set(old_file_path, json.dumps(moved_file_context))
                    redis_client.delete(old_file_path)
                else:
                    logger.debug(f'contexts were the same, file {modified_file.new_path} was just moved commit {commit.hash}')

                logger.info(f'finished updating project context for deleted file {modified_file.old_path} commit {commit.hash}')
                entropy_metrics = calculate_entropy_metrics(project_context, moved_file_context)
                project_data = update_project_data(project_data, entropy_metrics, metadata)
                continue

        previous_commit = commit.hash

    history_df = pd.DataFrame({k: v for k, v in project_data.items()})
    history_path = entropy_history_path + os.sep + 'commit-entropy_historical' + '-' + project_name
    history_df.to_csv(f'{history_path}.csv')

    files_per_commit_df = pd.DataFrame({
        'commit_sha': commits,
        'file_count': file_count
    })
    files_per_commit_df.to_csv(f'{history_path}-file-count.csv')

    # redis_client.flushall()
    # generalise me to main branch
    github.checkout(default_branch)
    logger.info(f'finished processing project {project_name}')


if __name__ == '__main__':
    # project_paths = ['/home/adriano/Projects/phd/code-java-projects/googlecontainertools/jib/jib']
    repo_path = sys.argv[1]
    default_branch = sys.argv[2]
    repo_name = repo_path.split('/')[-1]
    projects_root = '/home/adriano/Projects/phd/code-java-projects'
    project_root = projects_root + os.sep + repo_path + os.sep + repo_name
    calculate_historical_entropy(project_root, default_branch)
