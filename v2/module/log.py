import logging
import os

from config.config import Config
from common.function.common_function import *


class Log():

    def __init__(self):
        config = Config()

        self.logger = config.set_log()

    def create_log(self, log_path):
        """ 
        def description : 로그 생성

        Parameters
        ----------
        log_path = 로그 경로
        """

        # log 출력 형식
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # log 출력
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        if not os.path.isdir(f'{log_path}/'):
            os.mkdir(f'{log_path}/')

        # log를 파일에 출력
        file_name = str(generate_micro_date()) + ".log"
        file_handler = logging.FileHandler(log_path + "/" + file_name)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def write_log(self, msg):
        """ 
        def description : 로그 작성

        Parameters
        ----------
        msg = 로그 메세지
        """
        self.logger.info(msg)
