import time
import pyupbit

from config.config import Config
from module.exception import *


class Upbit():

    def __init__(self):
        config = Config()

        self.upbit = config.set_upbit()
        self.ticker = None

    def try_again(num):
        """ 
        def description : 재시도 wrapper

        Parameters
        ----------
        num : 재시도 카운트(int)
        """
        def deco(func):
            def wrapper(self, *args, **kwargs):
                for i in range(0, num):
                    try:
                        response = func(self, *args, **kwargs)
                        return response

                    except Exception as ex:
                        InternalServerException(ticker=self.get_ticker(), msg=str(ex))

                    time.sleep(0.1)

                return False

            return wrapper
        return deco

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

    @try_again(num=3)
    def get_my_balance(self):
        """ 
        def description : 특정 잔고 정보 조회

        Returns
        -------
        my_target_balance : 타겟 티커에 대한 잔고 정보
        """

        all_my_balance = self.get_all_my_balance()

        my_target_balance = 0
        for my_balance in all_my_balance:
            if my_balance["ticker"] == self.ticker:
                my_target_balance = float(my_balance['balance'])
                break

        return my_target_balance

    @try_again(num=3)
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

    @try_again(num=3)
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

    @try_again(num=3)
    def get_KRW_tickers(self):
        """ 
        def description : 원화로 매매 가능한 코인 리스트 

        Returns
        -------
        tickers : 티커 배열 (float)
        """

        tickers = pyupbit.get_tickers(fiat="KRW")
        return tickers

    @try_again(num=3)
    def get_current_price(self):
        """ 
        def description : 현재가 조회

        Returns
        -------
        current_price : 현재가 (float)
        """

        df = pyupbit.get_ohlcv(self.ticker, interval="minute1", count=1)

        current_price = df['close'][0]
        return current_price

    @try_again(num=3)
    def get_target_date_price(self, date):
        """ 
        def description : 특정 날짜의 가격 조회

        Parameters
        ----------
        date : 특정 날짜
        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval="minute1", to=date, count=1)

        close_price = df['close'][0]
        return close_price

    @try_again(num=3)
    def get_target_interval_price(self, interval):
        """ 
        def description : 특정 인터벌의 가격 조회

        Parameters
        ----------
        interval : 특정 인터벌

        minute1
        minute3
        minute5
        minute10
        minute15
        minute30
        minute60
        minute240
        day
        week
        month

        Returns
        -------
        close_price : 종가 (float)
        """
        df = pyupbit.get_ohlcv(self.ticker, interval=interval, count=2)

        close_price = df['close'][0]
        return close_price

    @try_again(num=3)
    def get_price_change_rate_by_price(self, from_price, to_price):
        """ 
        def description :가격 변화율 계산


        Parameters
        ----------
        from_price : 시작점 종가
        to_price : 종료점 종가

        Returns
        -------
        change_rate : 현재변화율 (float)
        """

        change_rate = ((to_price - from_price) / from_price) * 100
        change_rate = round(change_rate, 4)
        return change_rate

    @try_again(num=3)
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
        df = pyupbit.get_ohlcv(self.ticker, interval="day", count=target_term)
        ma = df['close'].rolling(target_term).mean().iloc[-1]
        time.sleep(0.15)
        return ma

    @try_again(num=3)
    def get_cross_state(self):
        """ 
        def description : 크로스 상태 조회

        Returns
        -------
        state : 크로스 상태 (str)
        """
        state = ""
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

        # 거래전 잔고 확인
        krw_my_balance = self.get_krw_balance()
        if krw_order > krw_my_balance:
            response_object = {
                "status": "fail",
                "msg": "KRW 잔고가 부족합니다."
            }
            return response_object

        # 주문 시도
        fees = 0.0005
        buy_result = self.upbit.buy_market_order(self.ticker, krw_order * (1-fees))

        # 성공
        if "uuid" in buy_result:
            response_object = {
                "status": "success",
                "msg": str(buy_result)
            }
            return response_object

        # 실패
        else:
            response_object = {
                "status": "fail",
                "msg": str(buy_result)
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
        org_ticker = self.ticker

        if krw_order:
            ticker_balance = krw_order

        else:
            self.ticker = self.ticker.replace("KRW-", "")
            ticker_balance = self.get_my_balance()
            self.ticker = org_ticker

        sell_result = self.upbit.sell_market_order(self.ticker, ticker_balance)

        # 성공
        if "uuid" in sell_result:
            response_object = {
                "status": "success",
                "message": str(sell_result)
            }
            return response_object

        # API 처리 실패
        if "error" in sell_result:
            response_object = {
                "status": "fail",
                "message": sell_result["message"]
            }
            return response_object

        # 기타 오류
        else:
            response_object = {
                "status": "fail",
                "message": str(sell_result)
            }
            return response_object
