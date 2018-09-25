import datetime
from decimal import Decimal

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.utils.safestring import mark_safe
from terminaltables import AsciiTable

from certhelper.utilities.logger import get_configured_logger

logger = get_configured_logger(loggername=__name__, filename="utilities.log")


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
        if int(year) in range(1900, 3000) and int(month) in range(1, 13) and int(
                day) in range(1, 32):
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
            if not candidate.startswith('date_range') or candidate.startswith(
                    'date_range') and is_valid_date(tmp):
                applied_filters[candidate] = tmp

    year = request.GET.get('date_year', '')
    month = request.GET.get('date_month', '')
    day = request.GET.get('date_day', '')

    the_date = get_date_string(year, month, day)

    # TODO solve conflict between two dates set
    if request.GET.get('date', ''):
        the_date = request.GET.get('date', '')

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
    for candidate in [
        "options",
        "category",
        "runs",
        "type",
        "date",
        "userid",
        "run_number",
        "problem_categories"
    ]:
        for word in request.GET:
            if candidate in word:
                return True
    return False


def get_this_week_filter_parameter():
    start_of_week = timezone.now() - timezone.timedelta(timezone.now().weekday())
    end_of_week = start_of_week + timezone.timedelta(6)

    date_gte = str(start_of_week.year) + "-" + str(start_of_week.month) + "-" + str(
        start_of_week.day)
    date_lte = str(end_of_week.year) + "-" + str(end_of_week.month) + "-" + str(
        end_of_week.day)

    get_parameters = "?date__gte=" + str(date_gte)
    get_parameters += "&date__lte=" + str(date_lte)

    return get_parameters


def get_today_filter_parameter():
    return "?date={}".format(timezone.now().strftime('%Y-%m-%d'))


def get_from_summary(summary, runtype=None, reco=None, date=None):
    filtered = summary
    if runtype:
        filtered = [item for item in filtered if item['type__runtype'] == runtype]
    if reco:
        filtered = [item for item in filtered if item['type__reco'] == reco]
    if date:
        filtered = [item for item in filtered if item['date'] == to_date(date)]
    return filtered


def to_date(date, formatstring="%Y-%m-%d"):
    if isinstance(date, datetime.datetime):
        return date.date()
    if isinstance(date, datetime.date):
        return date
    return datetime.datetime.strptime(date, formatstring).date()


def to_weekdayname(date, formatstring="%Y-%m-%d"):
    return to_date(date, formatstring).strftime("%A")


def get_full_name(user):
    name = ""
    if user.first_name:
        name += str(user.first_name) + " "
    if user.last_name:
        name += str(user.last_name) + " "

    if name:
        name += "(" + str(user.username) + ")"
    else:
        name += str(user.username)

    return name


def extract_numbers_from_list(list_of_elements):
    return [int(i) for i in list_of_elements
            if type(i) == int or i.isdigit()]


def uniquely_sorted(list_of_elements):
    new_list = list(set(extract_numbers_from_list(list_of_elements)))
    new_list.sort()
    return new_list


def extract_egroups(json_data):
    """
    Returns the E-Groups in a JSON Dictionary
    """
    return json_data.get("groups")


def get_highest_privilege_from_egroup_list(egroups, criteria_dict):
    """
    Compares every egroup in egroups with the criteria_dict
    and returns the highest criteria found
    """
    highest_privilege = 0
    for privilege, criteria_list in criteria_dict.items():
        if any(egroup in criteria_list for egroup in egroups):
            if privilege > highest_privilege:
                highest_privilege = privilege
    return highest_privilege


def get_or_create_shift_leader_group(group_name):
    try:
        g = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        user_permissions = Permission.objects.filter(
            content_type__model="user")
        certhelper_permissions = Permission.objects.filter(
            content_type__app_label="certhelper")
        categories_permissions = Permission.objects.filter(
            content_type__app_label="categories")
        g = Group.objects.create(
            name=group_name)
        for permission in user_permissions:
            g.permissions.add(permission)
        for permission in certhelper_permissions:
            g.permissions.add(permission)
        for permission in categories_permissions:
            g.permissions.add(permission)
        g.save()
    return g


def create_userprofile(user):
    from certhelper.models import UserProfile
    try:
        userprofile = UserProfile.objects.get(user=user)
        logger.info("UserProfile with id {} for User {} already exists"
                    .format(userprofile.id, user))
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=user)
        logger.info("New UserProfile with id {} for User {} has been created"
                    .format(userprofile.id, user))
    return userprofile


def update_userprofile(user):
    from certhelper.models import UserProfile
    if user.pk:  # Only already existing users
        try:
            socialaccount = SocialAccount.objects.get(user=user)
            try:
                userprofile = user.userprofile
            except UserProfile.DoesNotExist:
                userprofile = create_userprofile(user)

            if userprofile.extra_data != socialaccount.extra_data:
                userprofile.extra_data = socialaccount.extra_data
                userprofile = userprofile.update_privilege()
                user.userprofile = userprofile
                logger.info("Extra data have been updated for {}".format(user))
        except SocialAccount.DoesNotExist:
            logger.warning("No SocialAccount exists for User {}".format(user))
    else:
        logger.info("Cannot update UserProfile for non existing User {}".format(user))


def get_ascii_table(column_description, data):
    table = AsciiTable([column_description] + data)
    table.inner_row_border = True
    return table.table


def get_runs_from_request_filters(request, alert_errors, alert_infos, alert_filters):
    from certhelper.models import RunInfo, Type

    runs = RunInfo.objects.filter(userid=request.user)

    date_filter_value = request.GET.get('date', None)

    date_from = request.GET.get('date_range_0', None)
    date_to = request.GET.get('date_range_1', None)
    runs_from = request.GET.get('runs_0', None)
    runs_to = request.GET.get('runs_1', None)
    type_id = request.GET.get('type', None)

    if date_filter_value:
        if is_valid_date(date_filter_value):
            runs = runs.filter(date=date_filter_value)
            alert_filters.append("Date: " + str(date_filter_value))

        else:
            alert_errors.append("Invalid Date: " + str(date_filter_value))
            return RunInfo.objects.none()

    if date_from:
        if is_valid_date(date_from):
            runs = runs.filter(date__gte=date_from)
            alert_filters.append("Date from: " + str(date_from))
        else:
            alert_errors.append("Invalid Date: " + str(date_from))
            return RunInfo.objects.none()

    if date_to:
        if is_valid_date(date_to):
            runs = runs.filter(date__lte=date_to)
            alert_filters.append("Date to: " + str(date_to))
        else:
            alert_errors.append("Invalid Date: " + str(date_to))
            return RunInfo.objects.none()

    if runs_from:
        try:
            runs = runs.filter(run_number__gte=runs_from)
            alert_filters.append("Runs from: " + str(runs_from))
        except:
            alert_errors.append("Invalid Run Number: " + str(runs_from))
            return RunInfo.objects.none()

    if runs_to:
        try:
            runs = runs.filter(run_number__lte=runs_to)
            alert_filters.append("Runs to: " + str(runs_to))
        except:
            alert_errors.append("Invalid Run Number: " + str(runs_to))
            return RunInfo.objects.none()

    if type_id:
        if is_valid_id(type_id, Type):
            runs = runs.filter(type=type_id)
            alert_filters.append("Type: " + str(type_id))
        else:
            alert_errors.append("Invalid Type: " + str(type_id))
            return RunInfo.objects.none()

    if not date_filter_value and not type_id and not date_from and not date_to and not runs_from and not runs_to:
        alert_infos.append(
            "No filters applied. Showing every run you have ever certified!")

    return runs


def render_component(component, component_lowstat):
    """
    Renders the component (Pixel/ SiStrip/ Tracking) for the RuninfoTable

    If lowstat is checked then "Lowstat" is displayed instead of Good/Bad/Excluded
    If the Component is good, then the color will be green, otherwise red.

    This should lead to a similar behavior as in the RunRegistry
    """
    component_rating = component.lower()
    css_class = None

    if component_rating == "good" or component_rating == "lowstat":
        css_class = "good-component"
    elif component_rating == "bad":
        css_class = "bad-component"
    elif component_rating == "excluded":
        css_class = "excluded-component"

    component_value = component

    if component_lowstat is True and component_rating != "excluded":
        component_value = "Lowstat"

    if css_class:
        return mark_safe('<div class="{}">{}</div>'.format(css_class, component_value))
    return component_lowstat


def render_trackermap(trackermap):
    if trackermap == "Missing":
        return mark_safe('<div class="bad-component">{}</div>'.format(trackermap))
    return trackermap


def get_runinfo_from_request(request):
    """
    :return: RunInfo instance filled with attributes from the request
    """
    from certhelper.models import RunInfo, ReferenceRun, Type

    type_id = request.GET.get('type', None)
    type_ = Type.objects.get(pk=type_id) if type_id is not None and type_id != "" else None
    reference_run_id = request.GET.get('reference_run', None)
    reference_run = ReferenceRun.objects.get(pk=reference_run_id) if reference_run_id is not None and reference_run_id != "" else None
    run_number = request.GET.get('run_number', None)
    int_luminosity = request.GET.get('int_luminosity', None)
    number_of_ls = request.GET.get('number_of_ls', None)
    pixel = request.GET.get('pixel', None)
    pixel_lowstat = request.GET.get('pixel_lowstat', False)
    sistrip = request.GET.get('sistrip', None)
    sistrip_lowstat = request.GET.get('sistrip_lowstat', False)
    tracking = request.GET.get('tracking', None)
    tracking_lowstat = request.GET.get('tracking_lowstat', False)

    run = RunInfo(
        type=type_,
        reference_run=reference_run,
        run_number=run_number,
        pixel=pixel,
        sistrip=sistrip,
        tracking=tracking,
    )
    if int_luminosity is not None and int_luminosity != "":
        run.int_luminosity = Decimal(int_luminosity)

    if number_of_ls is not None and number_of_ls != "":
        try:
            run.number_of_ls = int(number_of_ls)
        except ValueError:
            run.number_of_ls = int(float(number_of_ls))  # to allow "12.0" as input

    if pixel_lowstat is not None and pixel_lowstat != "":
        run.pixel_lowstat = pixel_lowstat == "true"

    if sistrip_lowstat is not None and sistrip_lowstat != "":
        run.sistrip_lowstat = sistrip_lowstat == "true"

    if tracking_lowstat is not None and tracking_lowstat != "":
        run.tracking_lowstat = tracking_lowstat == "true"

    return run
