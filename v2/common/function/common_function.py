import datetime
import time


def check_required_value(data, required_list):
    """
    =======================================================================
    Def Decription          : 인풋 요청에서 필수데이터 체크
    Comments 

    - 각 define 참조
    =======================================================================
    """
    for required in required_list:
        if required not in data:
            response_object = {
                "status": "fail",
                "message": "request data validation failed, %s is required " % (required),
                "missing_value": required
            }
            return response_object

    response_object = {
        "status": "success",
        "message": "all required values are requested"
    }
    return response_object


def generate_now_date():
    """ 
    def description : 오늘 날짜 연월일 시분초 산출

    Parameters
    ----------
    없음 

    Returns
    -------
    datetime
        오늘 날짜 연월일 시분초
    """
    now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now_date


def generate_now_day():
    """ 
    def description : 오늘 날짜 연월일 산출

    Parameters
    ----------
    없음 

    Returns
    -------
    datetime
        오늘 날짜 연월일
    """
    now_day = datetime.datetime.now().strftime("%Y-%m-%d")
    return now_day


def generate_now_time():
    """ 
    def description : 오늘 날짜 시분초 산출

    Parameters
    ----------
    없음 

    Returns
    -------
    datetime
        오늘 날짜 시분초
    """
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    return now_time


def generate_now_min():
    """ 
    def description : 현재 분 산출

    Returns
    -------
    mm 분
    """
    mm = generate_now_time()[-5:-3]
    return int(mm)


def generate_now_sec():
    """ 
    def description : 현재 초 산출

    Returns
    -------
    ss 초
    """
    ss = generate_now_time()[-2:]
    return int(ss)


def generate_micro_date():
    """ 
    def description : 오늘 날짜 마이크로 세컨드까지 산출 

    Parameters
    ----------
    없음 

    Returns
    -------
    datetime
        오늘 날짜 마이크로 세컨드
    """
    now_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")

    return now_date


def cal_time_changes(flag_time):
    """ 
    def description : 시간변화 체크

    Parameters
    ----------
    start_time : 시작 시간 

    Returns
    -------
    float : 시작 시간으로부터 현재 시간 차이 (sec)
    """

    now_time = time.time()
    time_diff = (now_time - flag_time)
    return time_diff


def cal_price_changes(f_close, l_close):
    """ 
    def description : 가격 변화 산출 

    Parameters
    ----------
    f_close : 시가
    l_close : 종가

    Returns
    -------
    change_rate : 변화율
    """
    change_rate = round(((l_close - f_close) / f_close) * 100, 3)
    return change_rate


def sort_by_current_price(data_list):
    """ 
    def description : 현재가 기준으로 정렬 

    Parameters
    ----------
    data_list : 데이터 리스트 (list)

    Returns
    -------
    data_list : 데이터 리스트 (list)
    """
    arr = data_list
    for i in range(len(arr) - 1, 0, -1):
        for j in range(i):
            if arr[j]["current_price"] < arr[j + 1]["current_price"]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return data_list


def add_sec(target_time, sec):
    """ def description : 타겟 시간에 초 추가

    Parameters : 
    target_time : 타겟 시간 (str, 23:59:59)
    sec : 추가할 초(int)

    Returns
    -------
    Boolean
    """
    if abs(int(sec)) >= 60:
        return False

    hh = int(target_time[0:2])
    mm = int(target_time[3:5])
    ss = int(target_time[6:8])

    ss += sec
    if sec > 0:

        if ss >= 60:
            ss = ss - 60
            mm += 1

        if mm >= 60:
            mm = mm - 60
            hh += 1

        if hh >= 24:
            hh = hh - 24

    else:

        if ss < 0:
            ss = abs(ss + 60)
            mm += -1

        if mm < 0:
            mm = abs(mm + 60)
            hh += -1

        if hh < 0:
            hh = abs(hh + 24)

    hh = str(hh).zfill(2)
    mm = str(mm).zfill(2)
    ss = str(ss).zfill(2)

    result_time = f"{hh}:{mm}:{ss}"
    return result_time


def add_min(target_time, min):

    if abs(int(min)) >= 60:
        return False

    hh = int(target_time[0:2])
    mm = int(target_time[3:5])
    ss = int(target_time[6:8])

    mm += min
    if mm > 0:

        if mm >= 60:
            mm = mm - 60
            hh += 1

        if hh >= 24:
            hh = hh - 24

    else:

        if mm < 0:
            mm = abs(mm + 60)
            hh += -1

        if hh < 0:
            hh = abs(hh + 24)

    hh = str(hh).zfill(2)
    mm = str(mm).zfill(2)
    ss = str(ss).zfill(2)

    result_time = f"{hh}:{mm}:{ss}"
    return result_time
