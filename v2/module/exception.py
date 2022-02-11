
from module.slack import *
from module.log import *

import datetime
import logging

log = logging.getLogger()


class InternalServerException():
    """
    서버 오류
    """

    def __init__(self, ticker=None, msg=None):

        slack = Slack()
        status = "server_error"
        error_msg = "관리자에게 문의하세요"

        if msg:
            error_msg = msg

        self.status = status
        self.error_msg = error_msg

        msg_s = f"""삐빅, 애러 발생, 
status: {status}
ticker: {ticker}
error_msg: {error_msg} 
time at : {datetime.datetime.now()}
"""

        # 슬랙 전송
        slack.post_to_slack(msg_s)
