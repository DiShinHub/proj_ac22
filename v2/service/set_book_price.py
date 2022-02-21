
from module.upbit import *
from common.function.common_function import *

import time
import datetime

"""
오버 나잇 등 특정 상황에 매매
"""


def buy_at_target_price(target_price, krw_order, ticker="KRW-BTC"):
    """
    def description : 특정 가격에 매수

    Parameters
    ----------
    target_price : 특정 가격
    krw_order : 주문가
    ticker : 티커
    """

    upbit = Upbit()
    slack = Slack()
    log = Log()

    # start 메세지 전송
    msg_s = f"buy_at_target_price start!, ticker : {ticker}, started at : {datetime.datetime.now()}"
    slack.post_to_slack(msg_s)

    # log 생성
    log_path = f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}"
    log.create_log(log_path)
    log.write_log(msg_s)

    upbit.set_ticker(ticker)

    action_cnt = 0
    while True:

        try:
            # 현재가 산출
            current_price = upbit.get_current_price()
            print(f"{ticker} : {format(current_price, ',')}")

            if current_price > target_price:
                action_cnt += 1

                if action_cnt > 6:
                    result = upbit.buy_coin(krw_order)
                    if result == True:
                        msg = "buying_success"
                        log.write_log(msg)
                        slack.post_to_slack(msg)
                        break

            else:
                action_cnt = 0

        except Exception as ex:
            msg = str(ex)
            InternalServerException(
                ticker=ticker, msg=msg)

            log.write_log(msg)
            slack.post_to_slack(msg)
            time.sleep(3)

        time.sleep(0.5)

    return


def sell_at_target_price(target_price, krw_order, ticker="KRW-BTC"):
    """
    def description : 특정 가격에 매도

    Parameters
    ----------
    target_price : 특정 가격
    krw_order : 주문가
    ticker : 티커
    """

    upbit = Upbit()
    slack = Slack()
    log = Log()

    # start 메세지 전송
    msg_s = f"sell_at_target_price start!, ticker : {ticker}, started at : {datetime.datetime.now()}"
    slack.post_to_slack(msg_s)

    # log 생성
    log_path = f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}"
    log.create_log(log_path)
    log.write_log(msg_s)

    upbit.set_ticker(ticker)

    action_cnt = 0
    while True:

        try:
            # 현재가 산출
            current_price = upbit.get_current_price()
            print(f"{ticker} : {format(current_price, ',')}")

            if current_price < target_price:
                action_cnt += 1

                if action_cnt > 6:
                    result = upbit.buy_coin(krw_order)
                    if result == True:
                        msg = "selling_success"
                        log.write_log(msg)
                        slack.post_to_slack(msg)
                        break

            else:
                action_cnt = 0

        except Exception as ex:
            msg = str(ex)
            InternalServerException(
                ticker=ticker, msg=msg)

            log.write_log(msg)
            slack.post_to_slack(msg)
            time.sleep(3)

        time.sleep(0.5)

    return
