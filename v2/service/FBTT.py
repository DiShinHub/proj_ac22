from module.upbit import *
from common.function.common_function import *

from module.timer import *
import time

from threading import Timer

# 개발 중
upbit = Upbit()
slack = Slack()
log = Log()

close_price_list = []


def fbtt_action(target_price, krw_order, ticker):

    upbit.set_ticker(ticker)
    min5_pb = upbit.get_target_interval_price("minute5")
    print(min5_pb)

    # 종가리스트가 2개 이상일 때 시행
    if len(close_price_list) > 1:

        # 현재 쌓여 있는 종가 리스트의 각 변화율을 계산
        tmp_price_list = []
        tmp_diff_rate_list = []
        for idx, price in enumerate(close_price_list):

            tmp_price_list.append(price)

            pc = tmp_price_list[idx]
            pb = tmp_price_list[idx - 1]

            diff_rate = ((pc - pb) / pb * 100)
            tmp_diff_rate_list.append(diff_rate)

        print(tmp_diff_rate_list)

    close_price_list.append(min5_pb)
    print(close_price_list)


def fbtt_start(target_price, krw_order, ticker="KRW-BTC"):

    # # start 메세지 전송
    # msg_s = f"fbtt_start start!, ticker : {ticker}, started at : {datetime.datetime.now()}"
    # slack.post_to_slack(msg_s)

    # # log 생성
    # log_path = f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}"
    # log.create_log(log_path)
    # log.write_log(msg_s)

    fbtt_action(target_price, krw_order, ticker)

    action_flag = True
    loop_cnt = 0
    while True:

        if loop_cnt > 4:
            break

        now_min = generate_now_min()

        if now_min % 5 == 0:
            if action_flag == False:
                time.sleep(1.5)
                result = fbtt_action(target_price, krw_order, ticker)
                action_flag = True
                loop_cnt += 1

            else:
                action_flag = False

        time.sleep(0.5)

    return

# def action(target_price, krw_order, ticker="KRW-BTC"):
#     """
#     def description : 5분봉 3틱룰 시행

#     Parameters
#     ----------
#     target_price : 특정 가격
#     krw_order : 주문가
#     ticker : 티커
#     """

#     upbit = Upbit()
#     slack = Slack()
#     log = Log()

#     upbit.set_ticker(ticker)

#     #
#     current_price = upbit.get_current_price()
#     min5_pb = upbit.get_target_interval_price("minute5")
#     min10_pb = upbit.get_target_interval_price("minute10")
#     min15_pb = upbit.get_target_interval_price("minute15")
#     min20_pb = upbit.get_target_interval_price("minute20")
#     min25_pb = upbit.get_target_interval_price("minute25")

#     diff45 = min25_pb - min20_pb
#     diff34 = min20_pb - min15_pb
#     diff23 = min15_pb - min10_pb
#     diff12 = min10_pb - min5_pb

#     flag_time = None

#     action_cnt = 0
#     while True:

#         now_time = generate_now_time()
#         if flag_time == None:
#             flag_time = now_time

#         print(flag_time)
#         print(add_min(flag_time, 5))

#         return

#         try:
#             # 기존에
#             pass

#         except Exception as ex:
#             msg = str(ex)
#             InternalServerException(
#                 ticker=ticker, msg=msg)

#             log.write_log(msg)
#             slack.post_to_slack(msg)
#             time.sleep(3)

#         time.sleep(0.5)

#     return
