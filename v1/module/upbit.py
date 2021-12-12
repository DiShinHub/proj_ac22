import time
import pyupbit

from config.config import Config


class Upbit():

    def __init__(self):
        config = Config()

        self.upbit = config.set_upbit()
        self.ticker = None

    def set_ticker(self, ticker):
        """ 
        def description : 티커 셋팅

        Parameters
        ----------
        ticker : 티커(string) 

        Returns
        -------
        Boolean 
        """

        self.ticker = ticker
        return True

    def get_ticker(self):
        """ 
        def description : 셋팅 된 티커 리턴

        Returns
        -------
        ticker : 티커(string)  
        """

        return self.ticker

    def get_my_balance(self):
        """ 
        def description : 특정 잔고 정보 조회

        Returns
        -------
        my_target_balance : 타겟 티커에 대한 잔고 정보
        """

        all_my_balance = self.get_all_my_balance()

        my_target_balance = None
        for my_balance in all_my_balance:
            if my_balance["ticker"] == self.ticker:
                my_target_balance = float(my_balance['balance'])
                break

        return my_target_balance

    def get_krw_balance(self):
        """ 
        def description : 원화 잔고 조회

        Returns
        -------
        krw_balances : 원화
        """

        krw_balances = self.upbit.get_balances()
        krw_balances = float(krw_balances[0]["balance"])
        return krw_balances

    def get_all_my_balance(self):
        """ 
        def description : 전체 잔고 정보 조회

        Returns
        -------
        balance_list : 잔고 딕셔너리 array 
        """

        balances = self.upbit.get_balances()

        balance_dict = {}
        balance_list = []
        for b in balances:
            if b['balance'] is not None:
                balance_dict = {
                    'ticker': b['currency'],
                    'balance': float(b['balance'])
                }
                balance_list.append(balance_dict)

        return balance_list

    def get_KRW_tickers(self):
        """ 
        def description : 원화로 매매 가능한 코인 리스트 

        Returns
        -------
        tickers : 티커 배열 (float)
        """

        tickers = pyupbit.get_tickers(fiat="KRW")
        return tickers

    def get_current_price(self):
        """ 
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """

        current_price = None
        if self.ticker:
            ticker = self.ticker
            current_price = pyupbit.get_orderbook(
                ticker=ticker)["orderbook_units"][0]["ask_price"]

        return current_price

    def get_target_min_price(self, target_min):
        """ 
        def description : 특정 시간의 가격 조회

        Parameters
        ----------
        target_min : 특정 이전 시간(min)

        Returns
        -------
        f_close : 특정 시간의 가격 (float)
        """

        # 총 3회 시도
        for i in range(0, 3):
            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute1", count=target_min + 1)

                f_close = df['close'][0]
                return f_close

            except Exception as ex:
                pass

        return None

    def get_target_hour_price(self, target_hour):
        """ 
        def description : 특정 시간의 가격 조회

        Parameters
        ----------
        target_min : 특정 이전 시간(hour))

        Returns
        -------
        f_close : 특정 시간의 가격 (float)
        """

        # 총 3회 시도
        for i in range(0, 3):
            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute60", count=target_hour + 1)

                f_close = df['close'][0]
                return f_close

            except Exception as ex:
                pass

        return None

    def get_min_changes(self, target_min):
        """ 
        def description : 현재시간 기준으로 타겟으로부터 분당 변화율 조회 


        Parameters
        ----------
        target_min : 타겟 구간의 시작 점(min, int)

        Returns
        -------
        current_price : 현재변화율 (float)
        """

        # 총 3회 시도
        for i in range(0, 3):
            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute1", count=target_min+1)

                f_close = df['close'][0]
                l_close = df['close'][-1]
                change_rate = ((l_close - f_close) / f_close) * 100
                change_rate = round(change_rate, 4)
                return change_rate

            except Exception as ex:
                time.sleep(0.25)
                pass

        return None

    def get_hour_changes(self, target_hour):
        """ 
        def description : 현재시간 기준으로 타겟으로부터 시간당 변화율 조회 

        Parameters
        ----------
        target_hour : 타겟 구간의 시작 점(hour, int)

        Returns
        -------
        current_price : 현재변화율 (float)
        """

        # 총 3회 시도
        for i in range(0, 3):
            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute60", count=target_hour+1)

                f_close = df['close'][0]
                l_close = df['close'][-1]
                change_rate = ((l_close - f_close) / f_close) * 100
                change_rate = round(change_rate, 4)

                return change_rate

            except Exception as ex:
                time.sleep(0.25)
                pass

        return None

    def get_ma(self, target_term):
        """ 
        def description : 이동 평균선 조회

        Parameters
        ----------
        target_term : 이동평균선 타겟 텀 (int)

        Returns
        -------
        없음

        explain sample
        -------

        df['close'].rolling(5).mean().iloc[-1] :
        종가 중 5개를 추출하여 각 평균을 내고 마지막 항목을 추출 ==> 5일 이동평균선

        - df['close'].rolling(5)
        종가 시리즈 객체에서 rolling(windows=5) 메서드를 통해 위에서부터 5개의 데이터 묶음을 추출

        - .mean()
        평균 계산

        - .iloc[-1] - 마지막 항목 추출
        """
        # 총 3회 시도
        for i in range(0, 3):
            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="day", count=target_term)
                ma = df['close'].rolling(target_term).mean().iloc[-1]
                time.sleep(0.15)
                return ma

            except Exception as ex:
                time.sleep(0.25)
                pass

    def get_cross_state(self):
        """ 
        def description : 크로스 상태 조회

        Returns
        -------
        state : 크로스 상태 (str)
        """
        state = None
        if self.is_super_golden_crossed():
            state = "SGC"

        elif self.is_golden_crossed():
            state = "GC"

        elif self.is_super_dead_crossed():
            state = "SDC"

        elif self.is_dead_crossed():
            state = "DC"

        return state

    def is_golden_crossed(self):
        """ 
        def description : 골든 크로스 상태인지 확인

        Returns
        -------
        boolean 
        """

        if self.get_ma(5) > self.get_ma(10):
            return True

        return False

    def is_dead_crossed(self):
        """ 
        def description : 데드 크로스 상태인지 확인

        Returns
        -------
        boolean 
        """

        if self.get_ma(5) < self.get_ma(10):
            return True

        return False

    def is_super_golden_crossed(self):
        """ 
        def description : 15일선까지 정렬 된 골든 크로스 상태인지 확인

        Returns
        -------
        boolean 
        """

        if self.get_ma(5) > self.get_ma(10):
            if self.get_ma(10) > self.get_ma(15):
                return True

        return False

    def is_super_dead_crossed(self):
        """ 
        def description : 15일선까지 정렬 된 데드 크로스 상태인지 확인

        Returns
        -------
        boolean 
        """

        if self.get_ma(5) < self.get_ma(10):
            if self.get_ma(10) < self.get_ma(15):
                return True

        return False

    def buy_coin(self, krw_order):
        """ 
        def description : 코인 매수

        Parameters
        ----------
        krw_order : 코인 원화 주문 가격 

        Returns
        -------
        boolean 
        """

        try:
            krw_my_balance = self.get_krw_balance()

            if krw_order > krw_my_balance:
                response_object = {
                    "status": "fail",
                    "message": "not enough krw balance"
                }
                return response_object

            fees = 0.0005
            buy_result = self.upbit.buy_market_order(
                self.ticker, krw_order * (1-fees))
            if "uuid" in buy_result:
                response_object = {
                    "status": "success",
                    "message": str(buy_result)
                }
                return response_object

            else:
                response_object = {
                    "status": "fail",
                    "message": str(buy_result)
                }
                return response_object

        except Exception as ex:
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object

    def sell_coin(self, krw_order=None):
        """ 
        def description : 코인 매도
        krw_order : 코인 원화 주문 가격 

        Returns
        -------
        response_object : 결과 오브젝트(dict) 
        """
        try:
            org_ticker = self.ticker

            if krw_order:
                ticker_balance = krw_order
            
            else: 
                self.ticker = self.ticker.replace("KRW-", "")
                ticker_balance = self.get_my_balance()
                self.ticker = org_ticker

            sell_result = self.upbit.sell_market_order(
                self.ticker, ticker_balance)

            if "uuid" in sell_result:
                response_object = {
                    "status": "success",
                    "message": str(sell_result)
                }
                return response_object

            if "error" in sell_result:
                response_object = {
                    "status": "fail",
                    "message": sell_result["message"]
                }
                return response_object

            # error case catching
            else:
                response_object = {
                    "status": "fail",
                    "message": str(sell_result)
                }
                return response_object

        except Exception as ex:
            response_object = {
                "status": "fail",
                "message": str(ex)
            }
            return response_object
        

    def get_target_hour_avg_price(self, target_hour, count=10):
        """ 
        def description : 타겟 시간 전 평균 가 산출 

        Parameters
        ----------
        target_hour : 타겟 시간
        count : 분단위 데이터 갯수

        Returns
        -------
        avg_close : 평균 종가
        """

        # 총 10회 시도
        for i in range(0, 10):
            target_min = int(target_hour * 60 + (count/2))

            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute1", count=target_min + 1)

                sum_close = 0
                for j in range(0, count):
                    sum_close += df['close'][j]

                avg_close = sum_close / count
                return avg_close

            except Exception as ex:
                pass

        return None

    def get_target_day_avg_price(self, target_day, count=4):
        """ 
        def description : 타겟 일 전 평균 가 산출 

        Parameters
        ----------
        target_hour : 타겟 시간
        count : 분단위 데이터 갯수

        Returns
        -------
        avg_close : 평균 종가
        """

        # 총 10회 시도
        for i in range(0, 10):
            target_hour = int(target_day * 24 + (count/2))

            try:
                df = pyupbit.get_ohlcv(
                    self.ticker, interval="minute60", count=target_hour+1)

                sum_close = 0
                for j in range(0, count):
                    sum_close += df['close'][j]

                avg_close = sum_close / count
                return avg_close

            except Exception as ex:
                pass

        return None
