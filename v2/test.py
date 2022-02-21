from module.upbit import *


upbit = Upbit()

upbit.set_ticker("KRW-ETH")

cp = upbit.get_current_price()
print(cp)

bb = upbit.get_bollinger_bands("minute5")
print(bb)

bs = upbit.get_bollinger_state("minute5")
print(bs)
