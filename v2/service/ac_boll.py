from module.upbit import *
from module.slack import *
from module.log import *
from common.function.common_function import *

import time


class AcBoll:

    def __init__(self):

        self.upbit = Upbit()
        self.slack = Slack()
        self.log = Log()

        # 루프 활성화 상태
        self.loop_activate = True

        # 코인 기본 변수
        self.ticker = None                  # 티커
        self.current_price = 0              # 현재가
        self.bollinger_state = None         # 볼린저 현 상태
        self.bollinger_state_prev = None    # 볼린저 이전 상태
        self.is_now_five = False            # 체크되는 시간이 5분봉인지 확인

        self.action_state = None            # 매수 / 매도 상태

        # 상단 볼린저 브레이크
        self.tb_price = 0                   # tb 당시 가격
        self.tb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.is_TB = False                  # 상단 볼린저 브레이크 확정

        # 하단 볼린저 브레이크
        self.lb_price = 0                   # lb 당시 가격
        self.lb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.is_LB = False                  # 하단 볼린저 브레이크 확정

    def init_TB(self):
        """
        def description : tb 관련 변수 초기화

        """
        self.tb_price = 0
        self.tb_emergency_flag = False      # 이머전시 상황인지 체크하는 flag
        self.is_TB = False                  # 상단 볼린저 브레이크 확정
        self.is_now_five = False

    def init_LB(self):
        """
        def description : lb 관련 변수 초기화

        """
        self.lb_emergency_flag = False
        self.is_LB = False
        self.is_now_five = False

    def start(self, ticker="KRW-BTC", action_state=None):
        """
        def description : ac_boll 시작

        Parameters
        ----------
        ticker : 티커
        action_state : 매매 상태 

        buy : 매수 됨
        sell : 매도 됨
        None : 미보유

        """

        # 데이터 셋팅
        self.ticker = ticker
        self.action_state = action_state

        # start 메세지 전송
        msg_s = f"ac_boll start!, ticker : {self.ticker}, started at : {datetime.datetime.now()}"
        self.slack.post_to_slack(msg_s)

        # log 생성
        log_path = f"{os.path.abspath(os.curdir)}/log/{str(generate_now_day())}"
        self.log.create_log(log_path)
        self.log.write_log(msg_s)

        # 티커 셋팅
        self.upbit.set_ticker(self.ticker)

        while True:

            if self.loop_activate == False:
                break

            # 현재가 및 볼린저 상태 조회
            self.current_price = self.upbit.get_current_price()
            response = self.upbit.get_bollinger_state(interval="minute5")

            self.bollinger_state = response["bollinger_state"]
            self.top_bb = response["top_bb"]
            self.mid_bb = response["mid_bb"]
            self.bot_bb = response["bot_bb"]

            print(f"current_price : {self.current_price}")
            print(f"bollinger_state : {self.bollinger_state}")
            print(f"action_state : {self.action_state}")

            # bollinger 상태 변경 체크
            if self.bollinger_state != self.bollinger_state_prev:

                # 볼린저 브레이크 초기발생 셋팅
                self.emergency_early_discover()

            # 볼린저 브레이크 비상 대응
            self.emergency_observer()

            # 볼린저 브레이크 사후 로직
            if action_state != None:
                self.emergency_finisher()

            # end
            self.bollinger_state_prev = self.bollinger_state
            time.sleep(0.5)

        # end
        return

    """
    ===========================================================================
    Switch
    ===========================================================================
    """

    def emergency_early_discover(self):
        """
        def description : 비상상황 얼리 셋터

        """

        # TB 초기발생 셋팅
        if self.action_state != "buy":
            if self.bollinger_state == "TB":
                self.TB_early_discover()

        # LB 초기발생 셋팅
        if self.action_state == "buy":
            if self.bollinger_state == "LB":
                self.LB_early_discover()

    def emergency_observer(self):
        """
        def description : 비상상황 감시

        """

        # TB 비상처리
        if self.action_state != "buy":
            if self.tb_emergency_flag == True:
                self.TB_observer()

        # LB 비상처리
        if self.action_state == "buy":
            if self.lb_emergency_flag == True:
                self.LB_observer()

    def emergency_finisher(self):
        """
        def description : 비상상황 사후처리

        """
        # 볼린저 브레이크 사후 로직
        if self.action_state == "buy":
            self.TB_finisher()
            pass

        if self.action_state == "sell":
            # 바닥 짚어 사는 로직 개발 (위험할 수 있으니 보류)
            pass

    """
    ===========================================================================
    TB managing
    ===========================================================================
    """

    def TB_early_discover(self):
        """
        def description : TB 초기발견 대응로직

        """

        # 5분전 종가와 현재가를 입력
        if self.tb_emergency_flag == False:

            # tb_price 셋팅
            self.tb_price = self.current_price

            # flag 셋팅
            self.tb_emergency_flag = True

            # 현재 분이 5의 배수인지 확인
            now_min = generate_now_min()
            if now_min % 5 == 0:
                self.is_now_five = True

    def TB_observer(self):
        """
        def description : TB 감시로직

        """
        # 현재 분이 5의 배수가 아닐 때 시행
        if self.is_now_five == False:

            # 5분 봉이 갱신 될 때 마다 가격 체크
            now_min = generate_now_min()
            if now_min % 5 == 0:

                if self.TB_decider() == True:

                    msg = f" ticker : {self.ticker}, 천장인거 같은데 사는게 어때?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.action_state = "buy"
                    self.is_now_five = True

                else:
                    msg = f" ticker : {self.ticker}, 에이 상승인줄 알았네, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.init_TB()  # 초기화

        # 현재 분이 5의 배수일 때, 1분을 흘려버리고 flag 업데이트
        else:
            now_min = generate_now_min()
            if now_min % 5 != 0:
                self.is_now_five = False

    def TB_decider(self):
        """
        def description : TB 결정

        """
        time.sleep(1)

        five_min_bp = self.upbit.get_target_interval_price("minute5")
        ten_min_bp = self.upbit.get_target_interval_price("minute10")

        plus_cnt = 0
        minus_cnt = 0
        for i in range(0, 30):
            time.sleep(1)

            if self.current_price > self.tb_price:
                plus_cnt += 1

            else:
                minus_cnt += 1

        self.is_TB = False
        if five_min_bp > ten_min_bp and\
                self.current_price > self.tb_price:

            self.is_TB = True

        return self.is_TB

    def TB_finisher(self):
        """
        def description : TB 사후처리

        """
        # 현재 분이 5의 배수가 아닐 때 시행
        if self.is_now_five == False:

            # 5분 봉이 갱신 될 때 마다 가격 체크
            now_min = generate_now_min()
            if now_min % 5 == 0:

                five_min_bp = self.upbit.get_target_interval_price("minute5")
                ten_min_bp = self.upbit.get_target_interval_price("minute10")

                # CASE 1 . 현재가가 이전 5분봉 상승의 70퍼 지점보다 낮음
                if self.current_price < five_min_bp:
                    stand_price = (five_min_bp + ten_min_bp) * 0.7

                    if self.current_price < stand_price:
                        msg = f" ticker : {self.ticker}, 팔 때 된거 같은데?, dated at : {datetime.datetime.now()}"
                        self.slack.post_to_slack(msg)
                        self.action_state = "sell"

                        self.init_TB()  # 초기화

                # CASE 2 . 10분전 종가가 5분전 종가보다 낮음
                elif five_min_bp < ten_min_bp:
                    msg = f" ticker : {self.ticker}, 팔 때 된거 같은데?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)
                    self.action_state = "sell"

                    self.init_TB()  # 초기화

                else:
                    msg = f" ticker : {self.ticker}, 더오르네?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

        # 현재 분이 5의 배수일 때, 1분을 흘려버리고 flag 업데이트
        else:
            now_min = generate_now_min()
            if now_min % 5 != 0:
                self.is_now_five = False

    """
    ===========================================================================
    LB managing
    ===========================================================================
    """

    def LB_early_discover(self):
        """
        def description : LB 초기 감시 로직

        """

        # 5분전 종가와 현재가를 입력.
        if self.lb_emergency_flag == False:

            #
            self.lb_price = self.current_price

            # flag 셋팅
            self.lb_emergency_flag = True

            # 현재 분이 5의 배수인지 확인
            now_min = generate_now_min()
            if now_min % 5 == 0:
                self.is_now_five = True

    def LB_observer(self):
        """
        def description : LB 감시 로직

        """

        # 현재 분이 5의 배수가 아닐 때 시행
        if self.is_now_five == False:

            # 5분 봉이 갱신 될 때 마다 가격 체크
            now_min = generate_now_min()
            if now_min % 5 == 0:
                if self.LB_decider() == True:
                    msg = f" ticker : {self.ticker}, 바닥인거 같은데 파는게 어때?, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

                    self.init_LB()  # 초기화
                    self.action_state = "sell"

                else:
                    self.init_LB()  # 초기화
                    msg = f" ticker : {self.ticker}, 에이 바닥인줄 알았네, dated at : {datetime.datetime.now()}"
                    self.slack.post_to_slack(msg)

        # 현재 분이 5의 배수일 때, 1분을 흘려버리고 flag 업데이트
        else:
            now_min = generate_now_min()
            if now_min % 5 != 0:
                self.is_now_five = False

    def LB_decider(self):
        """
        def description : LB 비상 결정

        """

        time.sleep(1)
        five_min_bp = self.upbit.get_target_interval_price("minute5")
        ten_min_bp = self.upbit.get_target_interval_price("minute10")

        plus_cnt = 0
        minus_cnt = 0
        for i in range(0, 30):
            time.sleep(1)

            if self.current_price > self.tb_price:
                plus_cnt += 1

            else:
                minus_cnt += 1

        self.is_LB = False
        if ten_min_bp > five_min_bp and\
                self.current_price < self.lb_price:

            self.is_LB = True

        return self.is_LB
