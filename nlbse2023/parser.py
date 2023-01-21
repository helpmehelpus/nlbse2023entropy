import logging
import sys

logger = logging.getLogger('file-string-manager')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def get_file_string(file_path):
    file_string = ''
    with open(file_path, 'r') as file:
        try:
            raw_file_string = file.read()
            file_string += raw_file_string.replace('\n', ' ')
        except:
            logger.error(f'unable to parse symbol in the token stream. continuing without token')
        finally:
            file.close()

    return file_string
