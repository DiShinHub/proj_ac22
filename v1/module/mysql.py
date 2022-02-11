
from config.config import Config


class Mysql:

    def __init__(self):
        config = Config()
        conn = config.set_mysql()

        self.conn = conn
        self.cursor = conn.cursor()
        self.fetch_result = None

    def defense_xxs(self, bind):
        """ def description : xxs 방어 

        Parameters : 
        bind : 바인드(tuple)

        Returns
        -------
        bind: 방어 적용 된 bind (tuple)
        """
        bind_new = ()
        for val in bind:
            val = val.replace("<", "&lt")
            val = val.replace(">", "&gt")
            bind_new += (val,)

        return bind_new

    def format_read_one(self):
        """ def description : read_one 포멧팅

        Returns
        -------
        row_dict: 포멧 데이터 (dict) 
        """

        row_dict = {}
        for idx, row in enumerate(self.fetch_result):
            row_dict[self.cursor.description[idx][0]] = row

        return row_dict

    def read_one(self, query, bind):
        """ def description : 데이터 단일 조회 

        Parameters : 
        query: 쿼리문(str) 
        bind : 바인드(tuple)

        Returns
        -------
        response_object : 결과 오브젝트 (dict)
        """

        try:
            # 쿼리 실행
            self.cursor.execute(query, self.defense_xxs(bind))

            # 데이터 조회 및 결과 리턴
            self.fetch_result = self.cursor.fetchone()
            if self.fetch_result != None:
                response_object = {
                    "status": "success",
                    "message": "success",
                    "row": self.format_read_one()
                }
                return response_object

            else:
                response_object = {
                    "status": "no_data",
                    "message": "no_data",
                    "row": None
                }
                return response_object

        except Exception as ex:
            self.conn.rollback()
            self.conn.close()
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object

        finally:
            self.fetch_result = None

    def format_read_all(self):
        """ def description : read_all 포멧팅

        Returns
        -------
        row_list : 포멧 데이터(list)
        """

        row_list = []
        for idx, rows in enumerate(self.fetch_result):

            row_dict = {}
            for idx2, row in enumerate(rows):
                row_dict[self.cursor.description[idx2][0]] = row

            row_list.append(row_dict)

        return row_list

    def read_all(self, query, bind):
        """ def description : 데이터 복수 조회 

        Parameters : 
        query : 쿼리문(str) 

        Returns
        -------
        response_object : 결과 오브젝트(dict)
        """

        try:
            self.cursor.execute(query, self.defense_xxs(bind))

            # 데이터 조회 및 결과 리턴
            self.fetch_result = self.cursor.fetchall()
            if self.fetch_result != None:
                response_object = {
                    "status": "success",
                    "message": "success",
                    "rows": self.format_read_all()
                }
                return response_object

            else:
                response_object = {
                    "status": "no_data",
                    "message": "no_data",
                    "rows": None
                }
                return response_object

        except Exception as ex:
            self.conn.rollback()
            self.conn.close()
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object

        finally:
            self.fetch_result = None

    def excute_query(self, query=None, query_bulk=None):
        """ def description : 쿼리 실행

        Parameters : 
        query : 쿼리문 단일(str)
        query_bulk : 쿼리문 배열(list)

        Returns
        -------
        response_object(dict) : 결과 오브젝트 
        """

        try:

            if not query and not query_bulk:
                response_object = {
                    "status": "fail",
                    "message": "param should have query or query_bulk"
                }
                return response_object

            # 단일 케이스
            if query:
                self.cursor.execute(query)

            # 복수 케이스
            elif query_bulk:
                for query in query_bulk:
                    self.cursor.execute(query)

            response_object = {
                "status": "success",
                "message": "success"
            }
            return response_object

        except Exception as ex:
            self.conn.rollback()
            self.conn.close()
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object

    def excute_query_with_commit(self, query=None, query_bulk=None):
        """ def description : 쿼리 실행 (커밋 포함)

        Parameters : 
        query : 쿼리문 단일(str)
        query_bulk : 쿼리문 배열(list)

        Returns
        -------
        response_object(dict) : 결과 오브젝트 
            ㄴlastrowids : 인서트 된 pk 배열(list)
        """

        try:

            if not query and not query_bulk:
                response_object = {
                    "status": "fail",
                    "message": "param should have query or query_bulk"
                }
                return response_object

            lastrowids = []

            # 단일 케이스
            if query:
                self.cursor.execute(query)
                if str(query.lower()).find("insert") >= 0:
                    lastrowids.append(self.cursor.lastrowid)

            # 복수 케이스
            elif query_bulk:
                for query in query_bulk:
                    self.cursor.execute(query)

                    if str(query.lower()).find("insert") >= 0:
                        lastrowids.append(self.cursor.lastrowid)

            self.conn.commit()

            response_object = {
                "status": "success",
                "message": "success",
                "lastrowids": lastrowids
            }
            return response_object

        except Exception as ex:
            self.conn.rollback()
            self.conn.close()
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object

    def commit(self):
        """ def description : 커밋 (호출용)

        Returns
        -------
        result : 결과 (boolean)
        """

        try:
            self.conn.commit()
            return True

        except Exception as ex:
            return False

    def roll_back(self):
        """ def description : 롤백 (호출용)

        Returns
        -------
        result : 결과 (boolean)
        """

        try:
            self.conn.rollback()
            return True

        except Exception as ex:
            return False

    def close_conn(self):
        """ def description : 커넥션 종료 (호출용)

        Returns
        -------
        result : 결과 (boolean)
        """

        try:
            self.conn.close()
            return True

        except Exception as ex:
            return False
