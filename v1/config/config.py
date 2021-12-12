import os
import logging
import pymysql
import pymongo
import pyupbit

from common.function.common_function import *

from dotenv import load_dotenv
load_dotenv()


class Config:

    def __init__(self):
        self.logger = None
        self.mysql_db = None
        self.mongo_db = None
        self.upbit = None

    def set_log(self):

        # 로그 생성
        self.logger = logging.getLogger()

        # 로그의 출력 기준 설정
        self.logger.setLevel(logging.INFO)

        return self.logger

    def set_mysql(self):

        mysql_db = pymysql.connect(
            user=os.getenv("MYSQL_DB_USER"),
            passwd=os.getenv("MYSQL_DB_PASSWROD"),
            host=os.getenv("MYSQL_DB_HOST"),
            port=3306,
            db=os.getenv("MYSQL_DB_DATABASE"),
            charset='utf8'
        )

        self.mysql_db = mysql_db

        return self.mysql_db

    def set_mongo(self):

        self.mongo_db = pymongo.MongoClient(
            host=os.getenv("MONGO_HOST"),
            port=27017
        )
        return self.mongo_db

    def set_upbit(self):

        upbit = pyupbit.Upbit(
            os.getenv("UPBIT_ACCESS_KEY"),
            os.getenv("UPBIT_SECRET_KEY")
        )
        self.upbit = upbit

        return self.upbit
