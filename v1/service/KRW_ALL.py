import json
import time
import datetime

from module.upbit import *
from module.slack import *
from module.mysql import *
from module.mongo import *
from module.log import *

from common.function.common_function import *


def cross_state_for_all_KRW():
    """
    def description : 모든 원화 상장 코인들의 cross state 출력
    """

    upbit = Upbit()
    log = Log()

    # log 생성
    log.create_log(
        f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}")

    KRW_tickers = upbit.get_KRW_tickers()

    SGC_list = []
    GC_list = []
    SDC_list = []
    DC_list = []
    for ticker in KRW_tickers:

        upbit.set_ticker(ticker)

        # get_cross_state
        current_price = upbit.get_current_price()
        cross_state = upbit.get_cross_state()

        if cross_state == "SGC":
            data_dict = {
                "ticker": ticker,
                "current_price": current_price,
                "cross_state": cross_state
            }
            SGC_list.append(data_dict)

        elif cross_state == "GC":
            data_dict = {
                "ticker": ticker,
                "current_price": current_price,
                "cross_state": cross_state
            }
            GC_list.append(data_dict)

        elif cross_state == "SDC":
            data_dict = {
                "ticker": ticker,
                "current_price": current_price,
                "cross_state": cross_state
            }
            SDC_list.append(data_dict)

        elif cross_state == "DC":
            data_dict = {
                "ticker": ticker,
                "current_price": current_price,
                "cross_state": cross_state
            }
            DC_list.append(data_dict)

    # 현재가 기준으로 sorting
    SGC_list = sort_by_current_price(SGC_list)
    GC_list = sort_by_current_price(GC_list)
    SDC_list = sort_by_current_price(SDC_list)
    DC_list = sort_by_current_price(DC_list)

    # 출력
    log.write_log("golden crossed list")
    log.write_log(json.dumps(GC_list, indent=4))
    log.write_log("dead crossed list")
    log.write_log(json.dumps(DC_list, indent=4))
    log.write_log("super golden crossed list")
    log.write_log(json.dumps(SGC_list, indent=4))
    log.write_log("super dead crossed list")
    log.write_log(json.dumps(SDC_list, indent=4))
    return


def monitoring(ticker="KRW-BTC", report_term=30, sudden_term=5, sudden_per=0.5, sudden_init_term=15):
    """

    def description : 모니터링

    Parameters
    ----------
    ticker : 티커 (string)
    report_term : 리포트 주기 (min, int)
    sudden_term : 서든 기준 텀 (min, int)
    sudden_per :  서든 기준 퍼센티지 (percent, float)
    sudden_init_term : 서든 상황 종료 후 서든 값 초기화 (min, int)

    Returns
    -------
    current_price : 현재변화율 (float)
    """

    # object init
    upbit = Upbit()
    log = Log()
    slack = Slack()
    mysql = Mysql()
    mongo = Mongo()

    # start 메세지 전송
    msg_s = f"monitoring start!, ticker : {ticker}, started at : {datetime.datetime.now()}"
    slack.post_to_slack(msg_s)

    # log 생성
    log.create_log(
        f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}")
    log.write_log(msg_s)

    # mongo DB 셋팅
    ticker_col = ticker.replace("-", "_")
    if ticker_col not in mongo.get_col_list():
        print("mongo DB Collection, needed")
        return False

    mongo.set_col(ticker.replace("-", "_"))

    # 변수 셋팅
    flag_time = time.time()                  # 시간 체커
    report_term = report_term * 60           # min to sec

    sudden_init_term = sudden_init_term * 60  # min to sec
    org_in_sudden_check = sudden_per        # 원본 인크리즈 체커 퍼센티지
    org_de_sudden_check = -(sudden_per)     # 원본 디크리즈 체커 퍼센티지
    in_sudden_check = org_in_sudden_check   # 인크리즈 체커
    de_sudden_check = org_de_sudden_check   # 디크리즈 체커

    upbit.set_ticker(ticker)

    loop_cnt = 0
    while True:
        try:

            # 현재가 산출
            current_price = upbit.get_current_price()
            print(f"{ticker} : {format(current_price, ',')}")

            # sudden in/de crease check by sudden_term
            changes_5min = upbit.get_min_changes(sudden_term)

            # sudden in/de crease check
            if changes_5min:
                if changes_5min > in_sudden_check:
                    msg = f"ticker : {ticker}, sudden increase, current_price : {current_price}"
                    slack.post_to_slack(msg)
                    log.write_log(msg)
                    in_sudden_check += 0.05

                if changes_5min < de_sudden_check:
                    msg = f"ticker : {ticker}, sudden decrease, current_price : {current_price}"
                    slack.post_to_slack(msg)
                    log.write_log(msg)
                    de_sudden_check -= 0.05

            # 주기별 서든 값 초기화
            if cal_time_changes(flag_time) > sudden_init_term:
                de_sudden_check = org_de_sudden_check
                in_sudden_check = org_in_sudden_check
                flag_time = time.time()

            # cross_state 변화 체크
            cross_state = upbit.get_cross_state()

            if cross_state:
                if loop_cnt != 0:
                    prev_cross_state = mongo.get_doc_one()["cross_state"]
                    if prev_cross_state != cross_state:
                        msg = f"ticker : {ticker}, cross changed, cross_state : {cross_state}, current_price : {current_price}"
                        slack.post_to_slack(msg)
                        log.write_log(msg)

            # 신규데이터 삽입
            post = {
                "ticker": ticker,
                "current_price": current_price,
                "cross_state": cross_state,
                "date": datetime.datetime.now()
            }
            mongo.insert_doc(post)

            # report_term 간격으로 보고
            if cal_time_changes(flag_time) > report_term:

                hour_12_before_price = upbit.get_target_hour_avg_price(12)
                if hour_12_before_price:
                    hour_12_change_rate = cal_price_changes(
                        hour_12_before_price, current_price)
                    hour_12_before_price = format(hour_12_before_price, ",")
                time.sleep(0.15)

                day_1_before_price = upbit.get_target_day_avg_price(1)
                if day_1_before_price:
                    day_1_before_rate = cal_price_changes(
                        day_1_before_price, current_price)
                    day_1_before_price = format(day_1_before_price, ",")
                time.sleep(0.15)

                day_3_before_price = upbit.get_target_day_avg_price(3)
                if day_3_before_price:
                    day_3_before_rate = cal_price_changes(
                        day_3_before_price, current_price)
                    day_3_before_price = format(day_3_before_price, ",")
                time.sleep(0.15)

                day_7_before_price = upbit.get_target_day_avg_price(7)
                if day_7_before_price:
                    day_7_before_rate = cal_price_changes(
                        day_7_before_price, current_price)
                    day_7_before_price = format(day_7_before_price, ",")

                time.sleep(0.15)
                msg = f"""
                    ticker : {ticker}
                    current_price : {current_price}
                    hour_12_before_price: {hour_12_change_rate}, {hour_12_change_rate}%
                    day_1_before_price: {day_1_before_price}, {day_1_before_rate}%
                    day_3_before_price: {day_3_before_price}, {day_3_before_rate}%
                    day_7_before_price: {day_7_before_price}, {day_7_before_rate}%
                    """
                time.sleep(0.15)
                pass

        except Exception as ex:
            log.write_log(str(ex))
            log.write_log("=====================")
            time.sleep(3)


def catch_krw_new_public():
    """
    원화 상장 먹는 로직
    """

    # init
    upbit = Upbit()
    slack = Slack()
    mysql = Mysql()
    log = Log()

    # log 생성
    log.create_log(
        f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}")

    # start 메세지 전송
    msg = f"catch_new_krw_public start!, started at : {datetime.datetime.now()}"
    slack.post_to_slack(msg)
    log.write_log(msg)

    # 기능 변수
    time_cut = 360
    buy_time = None
    try_flag = False
    balance_status = "keep"
    flag_time = time.time()                  # 시간 체커
    report_term = 86400

    # 기존 티커 리스트
    KRW_tickers_old = upbit.get_KRW_tickers()
    old_cnt = len(KRW_tickers_old)

    while True:

        try:
            # 매수 이전
            if balance_status == "keep":

                # 신규 티커 리스트
                KRW_tickers_new = upbit.get_KRW_tickers()
                new_cnt = len(KRW_tickers_new)

                # 신규 티커 확인 후, 신규 티커 존재하면 매수 시도 시간 갱신 후 매수 시도
                diff_ticker = set(KRW_tickers_new) - set(KRW_tickers_old)
                diff_ticker_cnt = len(diff_ticker)
                if diff_ticker_cnt > 0:
                    if new_cnt > old_cnt:

                        # 매수 시도
                        new_ticker = list(diff_ticker)[0]
                        upbit.set_ticker(new_ticker)
                        response = upbit.buy_coin(300000)
                        if response["status"] == "success":
                            balance_status == "buy"
                            msg = f"new_ticker : {new_ticker}, buying success"
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            log.write_log(msg)

                        # 매수 실패
                        else:
                            msg = f"new_ticker : {new_ticker}, buying fail"
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            slack.post_to_slack(msg)
                            log.write_log(msg)

                        # 매수 시도 시간 갱신
                        if try_flag == False:
                            buy_time = time.time()

                        try_flag = True

            # 매수 이후
            else:
                # 매수 시도 시점을 기점으로 타임 컷 실행
                if cal_time_changes(buy_time) > time_cut:

                    # 매도 시도
                    response = upbit.sell_coin()
                    if response["status"] == "success":
                        msg = f"new_ticker : {new_ticker}, selling success"
                        slack.post_to_slack(msg)
                        log.write_log(msg)
                        return

                    # 매도 실패
                    else:
                        msg = f"new_ticker : {new_ticker}, selling fail"
                        slack.post_to_slack(msg)
                        log.write_log(msg)

            # report_term 간격으로 변수 셋팅
            if cal_time_changes(flag_time) > report_term:
                KRW_tickers_old = upbit.get_KRW_tickers()
                old_cnt = len(KRW_tickers_old)
                flag_time = time.time()

                msg = f"no changes, time : {datetime.datetime.now()}"
                log.write_log(msg)

            time.sleep(0.05)

        except Exception as ex:
            log.write_log(str(ex))
            log.write_log("=====================")
            time.sleep(3)
