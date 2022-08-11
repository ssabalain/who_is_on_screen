import logging
import os
from datetime import datetime

def create_logger(logs_path,script_name,level='INFO'):

    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    datetime_for_name = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    file_name = os.path.join(logs_path, f'{script_name}_{datetime_for_name}.log')

    global logger
    logger = logging.getLogger(__name__)

    while len(logger.handlers) > 0:
        h = logger.handlers[0]
        logger.removeHandler(h)

    if level.lower().startswith('critical'):
        l = logging.CRITICAL
    elif level.lower().startswith('error'):
        l = logging.ERROR
    elif level.lower().startswith('warning'):
        l = logging.WARNING
    elif level.lower().startswith('info'):
        l = logging.INFO
    elif level.lower().startswith('debug'):
        l = logging.DEBUG
    else:
        l = logging.INFO

    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    fh = logging.FileHandler(file_name)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(l)
    logger.info('Log created properly.')

    return logger

def shutdown_logger(logger):
    logger.info('Logger shutdown.')
    logging.shutdown()