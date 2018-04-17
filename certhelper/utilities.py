import datetime


def is_valid_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except:
        return False
    return False


def get_date_string(year, month, day):
    """"
    returns empty string if date is invalid
    returns YYYY-MM-DD if date is valid
    """

    datestring = None

    if year and month and day:  # if attributes exist
        if int(year) in range(1900, 3000) and int(month) in range(1, 12) and int(day) in range(1, 31):
            if len(month) == 1: month = "0" + month
            if len(day) == 1: day = "0" + day
            datestring =  year + "-" + month + "-" + day

    if is_valid_date(datestring):
        return datestring
    return ""
