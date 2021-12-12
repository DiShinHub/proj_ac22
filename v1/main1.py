from service.KRW_ALL import *


if __name__ == "__main__":

    monitoring(
        ticker="KRW-SAND",
        report_term=720,
        sudden_term=5,
        sudden_per=1,
        sudden_init_term=30
    )
