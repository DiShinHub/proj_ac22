from module.upbit import *
from module.slack import *
from module.log import *
from common.function.common_function import *

import time


class AcBoll:

    def __init__(self):

        # 개발 중
        self.upbit = Upbit()
        self.slack = Slack()
        self.log = Log()

        self.ticker = None                  # 티커
        self.current_price = 0              # 현재가
        self.bollinger_state = None         # 볼린저 현 상태
        self.bollinger_state_prev = None    # 볼린저 이전 상태
        self.is_now_five = False            # 체크되는 시간이 5분봉인지 확인

        self.action_state = None            # 매수 / 매도 상태

        # 상단 볼린저 브레이크
        self.tb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.tb_emergency_list = []         # 이머전시 상황에서 가격 리스트
        self.is_TB = False                  # 상단 볼린저 브레이크 확정

        # 하단 볼린저 브레이크
        self.lb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.lb_emergency_list = []         # 이머전시 상황에서 가격 리스트
        self.is_LB = False                  # 하단 볼린저 브레이크 확정

    def init_tb(self):
        self.tb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.tb_emergency_list = []         # 이머전시 상황에서 가격 리스트
        self.is_TB = False                  # 상단 볼린저 브레이크 확정
        self.is_now_five = False

    def init_lb(self):
        self.lb_emergency_flag = False
        self.lb_emergency_list = []
        self.is_LB = False
        self.is_now_five = False

    def start(self, ticker="KRW-BTC"):

        # 데이터 셋팅
        self.ticker = ticker

        # start 메세지 전송
        msg_s = f"fbtt_start start!, ticker : {self.ticker}, started at : {datetime.datetime.now()}"
        self.slack.post_to_slack(msg_s)

        # log 생성
        log_path = f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}"
        self.log.create_log(log_path)
        self.log.write_log(msg_s)

        # 티커 셋팅
        self.upbit.set_ticker(self.ticker)

        while True:
            self.current_price = self.upbit.get_current_price()
            response = self.upbit.get_bollinger_state(interval="minute5")

            self.bollinger_state = response["bollinger_state"]
            self.top_bb = response["top_bb"]
            self.mid_bb = response["mid_bb"]
            self.bot_bb = response["bot_bb"]

            print(f"current_price : {self.current_price}")
            print(f"bollinger_state : {self.bollinger_state}")

            # bollinger 상태 변경 체크
            if self.bollinger_state != self.bollinger_state_prev:

                # 볼린저 브레이크 초기발생 셋팅
                self.emergency_early_setter()

            # 비상 대응
            self.emergency_handler()

            # end init
            self.bollinger_state_prev = self.bollinger_state
            time.sleep(0.5)

        # end
        return

    def emergency_early_setter(self):

        # TB 초기발생 셋팅
        if self.action_state != "buy":
            if self.bollinger_state == "TB":
                self.emergency_TB_early_set()

        # LB 초기발생 셋팅
        if self.action_state == "buy":
            if self.bollinger_state == "LB":
                self.emergency_LB_early_set()

    def emergency_handler(self):

        # TB 비상처리
        if self.action_state != "buy":
            if self.tb_emergency_flag == True:
                self.emergency_TB()

        # LB 비상처리
        if self.action_state == "buy":
            if self.lb_emergency_flag == True:
                self.emergency_LB()

    def emergency_TB_early_set(self):
        """
        def description : LB 비상 조기 대응 셋

        """

        # 5분전 종가와 현재가를 입력.
        if self.tb_emergency_flag == False:
            self.tb_emergency_list.append(self.current_price)
            self.tb_emergency_list.append(
                self.upbit.get_target_interval_price("minute5"))

            # flag 셋팅
            self.tb_emergency_flag = True

            # 현재 분이 5의 배수인지 확인
            now_min = generate_now_min()
            if now_min % 5 == 0:
                self.is_now_five = True

    def emergency_TB(self):
        """
        def description : TB 비상 코어

        """
        # 현재 분이 5의 배수가 아닐 때 시행
        if self.is_now_five == False:

            # 5분 봉이 갱신 될 때 마다 가격 체크
            now_min = generate_now_min()
            if now_min % 5 == 0:
                if self.emergency_TB_decider() == True:
                    msg = f" ticker : {self.ticker}, 천장인거 같은데 사는게 어때?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.action_state = "buy"
                    self.init_tb()  # 초기화

                else:
                    msg = f" ticker : {self.ticker}, 에이 상승인줄 알았네, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.init_tb()  # 초기화

        # 현재 분이 5의 배수일 때, 1분을 흘려버리고 flag 업데이트
        else:
            now_min = generate_now_min()
            if now_min % 5 != 0:
                self.is_now_five = False

    def emergency_TB_decider(self):
        """
        def description : TB 비상 결정

        """

        time.sleep(1)
        five_min_bp = self.upbit.get_target_interval_price("minute5")
        self.tb_emergency_list.append(five_min_bp)

        # 5분 전종가, TB 발생시 현재가, 5분 뒤 종가가 정렬 되었는지 확인
        self.is_TB = True
        for idx in range(0, len(self.tb_emergency_list)-1):

            p1 = self.tb_emergency_list[idx]
            p2 = self.tb_emergency_list[idx + 1]

            # 중간에 상승이 있으면
            if p1 > p2:
                self.is_LB = False
                break

        return self.is_LB

    def emergency_LB_early_set(self):
        """
        def description : LB 비상 조기 대응 셋

        """

        # 5분전 종가와 현재가를 입력.
        if self.lb_emergency_flag == False:
            self.lb_emergency_list.append(self.current_price)
            self.lb_emergency_list.append(
                self.upbit.get_target_interval_price("minute5"))

            # flag 셋팅
            self.lb_emergency_flag = True

            # 현재 분이 5의 배수인지 확인
            now_min = generate_now_min()
            if now_min % 5 == 0:
                self.is_now_five = True

    def emergency_LB(self):
        """
        def description : LB 비상 코어

        """

        # 현재 분이 5의 배수가 아닐 때 시행
        if self.is_now_five == False:

            # 5분 봉이 갱신 될 때 마다 가격 체크
            now_min = generate_now_min()
            if now_min % 5 == 0:
                if self.emergency_LB_decider() == True:
                    msg = f" ticker : {self.ticker}, 바닥인거 같은데 파는게 어때?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.init_lb()  # 초기화
                    self.action_state = "sell"

                else:
                    self.init_lb()  # 초기화
                    msg = f" ticker : {self.ticker}, 에이 바닥인줄 알았네, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

        # 현재 분이 5의 배수일 때, 1분을 흘려버리고 flag 업데이트
        else:
            now_min = generate_now_min()
            if now_min % 5 != 0:
                self.is_now_five = False

    def emergency_LB_decider(self):
        """
        def description : LB 비상 결정

        """

        time.sleep(1)
        five_min_bp = self.upbit.get_target_interval_price("minute5")
        self.lb_emergency_list.append(five_min_bp)

        # 5분 봉들이 하락세인지 체크
        self.is_LB = True
        for idx in range(0, len(self.lb_emergency_list)-1):

            p1 = self.lb_emergency_list[idx]
            p2 = self.lb_emergency_list[idx + 1]

            # 중간에 상승이 있으면
            if p1 < p2:
                self.is_LB = False
                break

        return self.is_LB
