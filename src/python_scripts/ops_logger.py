import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, logs_path='./models/logs', script_name=os.path.basename(__name__), level='INFO'):
        self.logs_path = logs_path
        self.script_name = script_name
        self.level = level

    def get_level(self):
        lower_level = self.level.lower()
        if lower_level.startswith('critical'):
            l = logging.CRITICAL
        elif lower_level.startswith('error'):
            l = logging.ERROR
        elif lower_level.startswith('warning'):
            l = logging.WARNING
        elif lower_level.startswith('info'):
            l = logging.INFO
        elif lower_level.startswith('debug'):
            l = logging.DEBUG
        else:
            l = logging.INFO

        return l

    def create_logger(self):
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)

        datetime_for_name = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        file_name = os.path.join(self.logs_path, f'{self.script_name}_{datetime_for_name}.log')

        self.logger = logging.getLogger(self.script_name)

        while len(self.logger.handlers) > 0:
            h = self.logger.handlers[0]
            self.logger.removeHandler(h)

        l = self.get_level()

        formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.setLevel(l)
        self.logger.debug('Log created properly.')

    def update_level(self, level):
        self.level = level
        l = self.get_level()
        self.logger.setLevel(l)

    def shutdown_logger(self):
        self.logger.debug('Logger shutdown.')
        logging.shutdown()