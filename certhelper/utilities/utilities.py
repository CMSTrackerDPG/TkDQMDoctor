import datetime

from django.utils import timezone


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
        if int(year) in range(1900, 3000) and int(month) in range(1, 12) and int(day) in range(1, 31):
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
    if the_date:
        applied_filters['date'] = the_date

    return applied_filters


def is_valid_id(primary_key, Classname):
    try:
        if Classname.objects.filter(pk=primary_key):
            return True
    except:
        return False
    return False


def request_contains_filter_parameter(request):
    for candidate in ["date", "userid"]:
        for word in request.GET:
            if candidate in word:
                return True
    return False


def get_this_week_filter_parameter():
    start_of_week = timezone.now() - timezone.timedelta(timezone.now().weekday())
    end_of_week = start_of_week + timezone.timedelta(6)
    get_parameters = "?date__gte_day=" + str(start_of_week.day)
    get_parameters += "&date__gte_month=" + str(start_of_week.month)
    get_parameters += "&date__gte_year=" + str(start_of_week.year)
    get_parameters += "&date__lte_day=" + str(end_of_week.day)
    get_parameters += "&date__lte_month=" + str(end_of_week.month)
    get_parameters += "&date__lte_year=" + str(end_of_week.year)
    return get_parameters
