import datetime


def is_valid_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except:
        return False


def get_date_string(year, month, day):
    """"
    returns empty string if date is invalid
    returns YYYY-MM-DD if date is valid
    """

    datestring = None

    if year and month and day:  # if attributes exist
        if int(year) in range(1900, 3000) and int(month) in range(1, 13) and int(day) in range(1, 32):
            if len(month) == 1: month = "0" + month
            if len(day) == 1: day = "0" + day
            datestring = year + "-" + month + "-" + day

    if is_valid_date(datestring):
        return datestring
    return ""


def get_filters_from_request_GET(request):
    filter_candidates = [
        'category',
        'subcategory',
        'subsubcategory',
        'date_range_0',
        'date_range_1',
        'runs_0',
        'runs_1',
        'type',
    ]
    applied_filters = {}
    for candidate in filter_candidates:
        tmp = request.GET.get(candidate, '')
        if tmp != '' and tmp != 0:
            if not candidate.startswith('date_range') or candidate.startswith('date_range') and is_valid_date(tmp):
                applied_filters[candidate] = tmp

    year = request.GET.get('date_year', '')
    month = request.GET.get('date_month', '')
    day = request.GET.get('date_day', '')

    the_date = get_date_string(year, month, day)
    if (the_date):
        applied_filters['date'] = the_date

    return applied_filters


def is_valid_id(id, Classname):
    try:
        if Classname.objects.filter(pk=id):
            return True
    except:
        return False
    return False
