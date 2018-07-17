import re
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin

from certhelper.filters import RunInfoFilter, ShiftLeaderRunInfoFilter
from certhelper.utilities.RunInfoTypeList import RunInfoTypeList
from certhelper.utilities.ShiftLeaderReport import ShiftLeaderReport
from certhelper.utilities.utilities import is_valid_date, get_filters_from_request_GET, is_valid_id, \
    request_contains_filter_parameter, get_this_week_filter_parameter, get_today_filter_parameter
from .forms import *
from .tables import *


@method_decorator(login_required, name="dispatch")
class CreateRun(generic.CreateView):
    """Form which allows for creation of a new entry in RunInfo
    """

    model = RunInfo
    form_class = RunInfoForm
    template_name_suffix = '_form'
    success_url = '/'

    def form_valid(self, form_class):
        form_class.instance.userid = self.request.user
        return super(CreateRun, self).form_valid(form_class)


def listruns(request):
    """passes all RunInfo objects to list.html
    """

    if not request_contains_filter_parameter(request):
        return HttpResponseRedirect("/%s" % get_today_filter_parameter())

    # We make sure that the logged in user can only see his own runs
    # In case the user is not logged in we show all objects
    # but remove the edit and remove buttons from the tableview.
    if request.user.is_authenticated:
        run_info_list = RunInfo.objects.filter(userid=request.user)
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = RunInfoTable(run_info_filter.qs)
    else:
        run_info_list = RunInfo.objects.all()
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = READONLYRunInfoTable(run_info_filter.qs)

    RequestConfig(request).configure(table)

    applied_filters = get_filters_from_request_GET(request)

    filter_parameters = ""
    for key, value in applied_filters.items():
        filter_parameters += '&' if filter_parameters.startswith('?') else '?'
        filter_parameters += key + "=" + value

    return render(request, 'certhelper/list.html', {
        'table': table,
        'filter': run_info_filter,
        'filter_parameters': filter_parameters,
    })


@method_decorator(login_required, name="dispatch")
class ListReferences(SingleTableView):
    """Display ReferenceRuns in a tableview
    !!! USES DJANGO-TABLES2 !!! 
    """

    model = ReferenceRun
    table_class = ReferenceRunTable


def same_user_or_shiftleader_check(user):
    pass


@method_decorator(login_required, name="dispatch")
class UpdateRun(generic.UpdateView):
    """Updates a specific Run from the RunInfo table
    """

    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name = 'certhelper/runinfo_form.html'

    # def form_valid(self, form_class):
    # form_class.instance.userid = self.request.user # not neccessary to update
    #    return super(UpdateRun, self).form_valid(form_class)

    def same_user_or_shiftleader(self, user):
        """
        checks if the user trying to edit the run is the same user that created the run,
        has at least shift leader rights or is a super user (admin)
        """
        try:
            return self.get_object().userid == user or \
                   user.is_superuser or \
                   user.userprofile.has_shift_leader_rights
        except UserProfile.DoesNotExist:
            return False

    def dispatch(self, request, *args, **kwargs):
        if self.same_user_or_shiftleader(request.user):
            return super(UpdateRun, self).dispatch(request, *args, **kwargs)
        return redirect_to_login(request.get_full_path(), login_url=reverse('admin:login'))


@method_decorator(login_required, name="dispatch")
class DeleteRun(generic.DeleteView):
    """Deletes a specific Run from the RunInfo table    
    """

    model = RunInfo
    form_class = RunInfoForm
    success_url = '/shiftleader/'
    template_name_suffix = '_delete_form'


@method_decorator(login_required, name="dispatch")
class CreateType(generic.CreateView):
    """Form to create a new Type (RunType)
    """

    model = Type
    form_class = TypeForm
    template_name_suffix = '_form'
    success_url = '/create'


# TODO clean up this mess

@login_required
def summaryView(request):
    """ Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """
    runs = RunInfo.objects.filter(userid=request.user)

    date_filter_value = request.GET.get('date', None)

    date_from = request.GET.get('date_range_0', None)
    date_to = request.GET.get('date_range_1', None)
    runs_from = request.GET.get('runs_0', None)
    runs_to = request.GET.get('runs_1', None)
    type_id = request.GET.get('type', None)

    alert_errors = []
    alert_infos = []
    alert_filters = []

    if date_filter_value:
        if is_valid_date(date_filter_value):
            runs = runs.filter(date=date_filter_value)
            alert_filters.append("Date: " + str(date_filter_value))

        else:
            alert_errors.append("Invalid Date: " + str(date_filter_value))
            runs = RunInfo.objects.none()

    if date_from:
        if is_valid_date(date_from):
            runs = runs.filter(date__gte=date_from)
            alert_filters.append("Date from: " + str(date_from))
        else:
            alert_errors.append("Invalid Date: " + str(date_from))
            runs = RunInfo.objects.none()

    if date_to:
        if is_valid_date(date_to):
            runs = runs.filter(date__lte=date_to)
            alert_filters.append("Date to: " + str(date_to))
        else:
            alert_errors.append("Invalid Date: " + str(date_to))
            runs = RunInfo.objects.none()

    if runs_from:
        try:
            runs = runs.filter(run_number__gte=runs_from)
            alert_filters.append("Runs from: " + str(runs_from))
        except:
            alert_errors.append("Invalid Run Number: " + str(runs_from))
            runs = RunInfo.objects.none()

    if runs_to:
        try:
            runs = runs.filter(run_number__lte=runs_to)
            alert_filters.append("Runs to: " + str(runs_to))
        except:
            alert_errors.append("Invalid Run Number: " + str(runs_to))
            runs = RunInfo.objects.none()


    if type_id:
        if is_valid_id(type_id, Type):
            runs = runs.filter(type=type_id)
            alert_filters.append("Type: " + str(type_id))
        else:
            alert_errors.append("Invalid Type: " + str(type_id))
            runs = RunInfo.objects.none()

    if not date_filter_value and not type_id and not date_from and not date_to and not runs_from and not runs_to:
        alert_infos.append("No filters applied. Showing every run you have ever certified!")
    context = {}

    reference_run_ids = runs.values_list('reference_run').distinct()
    context['refs'] = ReferenceRun.objects.filter(id__in=reference_run_ids)

    runs = runs.order_by('type', 'run_number')  # Make sure runs are sorted by type

    runinfotypelists = []  # create one runinfotypelist per type

    for run in runs:
        if len(runinfotypelists) == 0 or run.type != runinfotypelists[-1].type:
            runinfotypelists.append(RunInfoTypeList(run.type, len(runinfotypelists) + 1))
        runinfotypelists[-1].add_run(run)

    context['runs'] = []
    context['tk_maps'] = []
    context['certified_runs'] = []
    context['sums'] = []

    for runinfotypelist in runinfotypelists:
        context['runs'].append(runinfotypelist.get_runinfo_ascii_table())
        context['tk_maps'].append(runinfotypelist.get_tracker_maps_info())
        context['certified_runs'].append(runinfotypelist.get_certified_runs_info())
        context['sums'].append(runinfotypelist.get_sums_ascii_table())

    context['alert_errors'] = alert_errors
    context['alert_infos'] = alert_infos
    context['alert_filters'] = alert_filters

    return render(request, 'certhelper/summary.html', context)


@login_required
def logout_view(request):
    """ Logout current user
    """
    if request.user.is_authenticated:
        logout(request)
        callback_url = 'https://login.cern.ch/adfs/ls/?wa=wsignout1.0&ReturnUrl=http%3A//'
        callback_url += request.META['HTTP_HOST']
        callback_url += reverse('certhelper:logout_status')
        return HttpResponseRedirect(callback_url)
    return HttpResponseRedirect('/')


def logout_status(request):
    logout_successful = False
    if not request.user.is_authenticated:
        logout_successful = True
    return render(request, 'certhelper/logout_status.html', {'logout_successful': logout_successful})


def load_subcategories(request):
    category_id = request.GET.get('categoryid')
    if category_id:
        subcategories = SubCategory.objects.filter(parent_category=category_id).order_by('name')
    else:
        subcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html', {'categories': subcategories})


def load_subsubcategories(request):
    subcategory_id = request.GET.get('subcategoryid')
    if subcategory_id:
        subsubcategories = SubSubCategory.objects.filter(parent_category=subcategory_id).order_by('name')
    else:
        subsubcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html', {'categories': subsubcategories})


# TODO make this faster, unneccessary databaes queries slows down page load when no filters are applied
def generate_summary(queryset):
    runs = queryset
    context = {}

    reference_run_ids = runs.values_list('reference_run').distinct()
    context['refs'] = ReferenceRun.objects.filter(id__in=reference_run_ids)

    runs = runs.order_by('type', 'run_number')  # Make sure runs are sorted by type

    runinfotypelists = []  # create one runinfotypelist per type

    for run in runs:
        if len(runinfotypelists) == 0 or run.type != runinfotypelists[-1].type:
            runinfotypelists.append(RunInfoTypeList(run.type, len(runinfotypelists) + 1))
        runinfotypelists[-1].add_run(run)

    context['runs'] = []
    context['tk_maps'] = []
    context['certified_runs'] = []
    context['sums'] = []

    for runinfotypelist in runinfotypelists:
        context['runs'].append(runinfotypelist.get_runinfo_ascii_table())
        context['tk_maps'].append(runinfotypelist.get_tracker_maps_info())
        context['certified_runs'].append(runinfotypelist.get_certified_runs_info())
        context['sums'].append(runinfotypelist.get_sums_ascii_table())

    return context


@staff_member_required
def shiftleader_view(request):
    """
    if no filter parameters are specified than every run from every user will be listed
    to prevent this we make sure that at least one filter is applied.

    if someone wants to list all runs form all users then he has to specify that explicitly
    in the filter (setting everything to nothing)
    """
    if request_contains_filter_parameter(request):
        return ShiftLeaderView.as_view()(request=request)
    return HttpResponseRedirect("/shiftleader/%s" % get_this_week_filter_parameter())


# TODO lazy load summary
@method_decorator(staff_member_required, name="dispatch")
class ShiftLeaderView(SingleTableMixin, FilterView):
    table_class = ShiftleaderRunInfoTable
    model = RunInfo
    template_name = "certhelper/shiftleader.html"
    filterset_class = ShiftLeaderRunInfoFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['summary'] = generate_summary(self.filterset.qs)
        context['slreport'] = ShiftLeaderReport(self.filterset.qs).get_context()
        context['deleted_runs'] = DeletedRunInfoTable(RunInfo.all_objects.dead().order_by('-run_number'))
        return context


# TODO superuser required
@staff_member_required
def hard_deleteview(request, run_number):
    try:
        run = RunInfo.all_objects.get(run_number=run_number)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the runnumber {} doesnt exist".format(run_number))
    except RunInfo.MultipleObjectsReturned:
        raise Http404("Multiple certifications with the runnumber {} exist".format(run_number))

    if request.method == "POST":
        run.hard_delete()
        return HttpResponseRedirect('/')

    return render(request, 'certhelper/hard_delete.html', {'run': run})


@staff_member_required
def hard_delete_run_view(request, pk):
    try:
        run = RunInfo.all_objects.get(pk=pk)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the id {} doesnt exist".format(pk))

    if request.method == "POST":
        run.hard_delete()
        return HttpResponseRedirect('/shiftleader/')

    return render(request, 'certhelper/hard_delete.html', {'run': run})


@staff_member_required
def restore_run_view(request, pk):
    try:
        run = RunInfo.all_objects.get(pk=pk)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the id {} doesnt exist".format(pk))

    if request.method == "POST":
        run.restore()
        return HttpResponseRedirect('/shiftleader/')

    return render(request, 'certhelper/restore.html', {'run': run})


def validate_central_certification_list(request):
    text = request.GET.get('text', None)
    run_numbers = re.sub('[^0-9]', ' ', text).split()  # only run_numbers
    run_numbers = set(run_numbers)  # remove duplicates
    data = RunInfo.objects.all().compare_list_if_certified(run_numbers)
    return JsonResponse(data)
