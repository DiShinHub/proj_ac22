
#
# import service.set_book_price as sbp

# sbp.buy_at_target_price(
#     target_price=3315000.0,
#     krw_order=None,
#     ticker="KRW-ETH"
# )

# import service.FBTT as fbtt


# response = fbtt.fbtt_start(
#     target_price=3315000.0,
#     krw_order=None,
#     ticker="KRW-ETH"
# )

# print(response)


from service.ac_boll import *

ac_boll = AcBoll()
ac_boll.start(ticker="KRW-SOL")
