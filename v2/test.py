import json
import time
import datetime

from module.upbit import *
from module.slack import *
from module.mysql import *
from module.mongo import *
from module.log import *

from common.function.common_function import *


upbit = Upbit()
upbit.set_ticker("KRW-BTC")

# p0 = upbit.get_current_price()
# print(p0)

# p1 = upbit.get_target_interval_price("minutes10")
# p2 = upbit.get_target_interval_price("minutes15")

# print(p1)
# print(p2)

# p3 = upbit.get_price_change_rate_by_price(p1, p2)
# print(p3)

# ma = upbit.get_ma(5)
# print(ma)

# cross_state = upbit.get_cross_state()
# print(cross_state)

# 전날 종가 구하기
# date = datetime.datetime.now()
# date = str(date)[0:19]

# yesterday_close_time = f"{date[0:10]} 09:00:00"
# print(yesterday_close_time)

# yesterday_close_price = upbit.get_target_date_price(yesterday_close_time)
# print(yesterday_close_price)
