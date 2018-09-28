import re

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin

from certhelper.filters import RunInfoFilter, ShiftLeaderRunInfoFilter, \
    ComputeLuminosityRunInfoFilter
from certhelper.models import UserProfile, SubSubCategory, SubCategory
from certhelper.runregistry import TrackerRunRegistryClient
from certhelper.utilities.ShiftLeaderReport import NewShiftLeaderReport
from certhelper.utilities.SummaryReport import SummaryReport
from certhelper.utilities.utilities import get_filters_from_request_GET, \
    request_contains_filter_parameter, get_this_week_filter_parameter, \
    get_today_filter_parameter, get_runs_from_request_filters, get_runinfo_from_request
from .forms import *
from .tables import *


@method_decorator(login_required, name="dispatch")
class CreateRun(generic.CreateView):
    """
    Form which allows for creation of a new entry in RunInfo
    """
    model = RunInfo
    form_class = RunInfoWithChecklistForm
    template_name = 'certhelper/runinfo_form.html'
    success_url = '/'

    def form_valid(self, form_class):
        form_class.instance.userid = self.request.user
        return super(CreateRun, self).form_valid(form_class)


def listruns(request):
    """
    passes all RunInfo objects to list.html
    """
    if not request_contains_filter_parameter(request):
        return HttpResponseRedirect("/%s" % get_today_filter_parameter())

    """
    Make sure that the logged in user can only see his own runs
    In case the user is not logged in show all objects,
    but remove the edit and remove buttons from the tableview.
    """
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
    """
    Display ReferenceRuns in a tableview
    !!! USES DJANGO-TABLES2 !!! 
    """
    model = ReferenceRun
    table_class = ReferenceRunTable


@method_decorator(login_required, name="dispatch")
class UpdateRun(generic.UpdateView):
    """
    Updates a specific Run from the RunInfo table
    """
    model = RunInfo
    form_class = RunInfoWithChecklistForm
    template_name = 'certhelper/runinfo_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checklist_not_required'] = True
        return context

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
        return redirect_to_login(request.get_full_path(),
                                 login_url=reverse('admin:login'))

    def get_success_url(self):
        is_same_user = self.get_object().userid == self.request.user
        return reverse('certhelper:shiftleader') if not is_same_user else "/"


@method_decorator(login_required, name="dispatch")
class DeleteRun(generic.DeleteView):
    """
    Deletes a specific Run from the RunInfo table
    """
    model = RunInfo
    form_class = RunInfoForm
    success_url = '/shiftleader/'
    template_name_suffix = '_delete_form'


@method_decorator(login_required, name="dispatch")
class CreateType(generic.CreateView):
    """
    Form to create a new Type (RunType)
    """
    model = Type
    form_class = TypeForm
    template_name_suffix = '_form'
    success_url = '/create'


@login_required
def summaryView(request):
    """ Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """

    alert_errors = []
    alert_infos = []
    alert_filters = []

    runs = get_runs_from_request_filters(request, alert_errors, alert_infos,
                                         alert_filters)

    summary = SummaryReport(runs)

    context = {"refs": summary.reference_runs(),
               "runs": summary.runs_checked_per_type(),
               "tk_maps": summary.tracker_maps_per_type(),
               "certified_runs": summary.certified_runs_per_type(),
               "sums": summary.sum_of_quantities_per_type(),
               'alert_errors': alert_errors, 'alert_infos': alert_infos,
               'alert_filters': alert_filters}

    return render(request, 'certhelper/summary.html', context)


@login_required
def logout_view(request):
    """
    Logout current user (also from CERN)
    """
    if request.user.is_authenticated:
        logout(request)
        callback_url = 'https://login.cern.ch/adfs/ls/?wa=wsignout1.0&ReturnUrl='
        callback_url += 'http%3A//'
        callback_url += request.META['HTTP_HOST']
        callback_url += reverse('certhelper:logout_status')
        return HttpResponseRedirect(callback_url)
    return HttpResponseRedirect('/')


def logout_status(request):
    logout_successful = not request.user.is_authenticated
    return render(request, 'certhelper/logout_status.html',
                  {'logout_successful': logout_successful})


def load_subcategories(request):
    category_id = request.GET.get('categoryid')
    if category_id:
        subcategories = SubCategory.objects.filter(
            parent_category=category_id).order_by('name')
    else:
        subcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html',
                  {'categories': subcategories})


def load_subsubcategories(request):
    subcategory_id = request.GET.get('subcategoryid')
    if subcategory_id:
        subsubcategories = SubSubCategory.objects.filter(
            parent_category=subcategory_id).order_by('name')
    else:
        subsubcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html',
                  {'categories': subsubcategories})


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
        context['summary'] = SummaryReport(self.filterset.qs)
        context['slreport'] = NewShiftLeaderReport(self.filterset.qs)
        context['deleted_runs'] = DeletedRunInfoTable(
            RunInfo.all_objects.dead().order_by('-run_number'))
        try:
            context['slchecklist'] = Checklist.objects.get(identifier='shiftleader')
        except Checklist.DoesNotExist:
            # shift leader checklist has not been created yet.
            pass

        return context


# TODO superuser required
@staff_member_required
def hard_deleteview(request, run_number):
    try:
        run = RunInfo.all_objects.get(run_number=run_number)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the runnumber {} doesnt exist".format(run_number))
    except RunInfo.MultipleObjectsReturned:
        raise Http404(
            "Multiple certifications with the runnumber {} exist".format(run_number))

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
    data = RunInfo.objects.check_if_certified(run_numbers)
    return JsonResponse(data)


# TODO update Checklist by Checklist model, return 404 if page doesnt exist
class ChecklistTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checklist_base_template_name"] = 'certhelper/checklists/base.html'
        return context


def check_integrity_of_run(request):
    """
    Checks if a run with the same number but different type already exists and checks
    if all the attributes (int. lumi, number of ls, pixel, sistrip, ...) match.

    :param request:
    :return: JsonResponse containing the attributes that do not match and their
    expected value
    """
    run = get_runinfo_from_request(request)
    data = RunInfo.objects.check_integrity_of_run(run)
    return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
class ComputeLuminosityView(FilterView):
    template_name = 'certhelper/compute_luminosity.html'
    filterset_class = ComputeLuminosityRunInfoFilter


@method_decorator(login_required, name="dispatch")
class RunRegistryView(TemplateView):
    template_name = 'certhelper/runregistry.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        run_min = request.POST.get("run_min")
        run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        run_registry = TrackerRunRegistryClient()
        if run_list:
            run_numbers = re.sub('[^0-9]', ' ', run_list).split()  # only run_numbers
            run_numbers = set(run_numbers)  # remove duplicates
            data = run_registry.get_runs_by_list(run_numbers)
        else:
            data = run_registry.get_runs_by_range(run_min, run_max)

        table = RunRegistryTable(data)

        return render(request, self.template_name, {'table': table})


class RunRegistryLumiSectionView(TemplateView):
    template_name = 'certhelper/lumisections.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # run_min = request.POST.get("run_min")
        # run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        run_registry = TrackerRunRegistryClient()
        if run_list:
            run_numbers = re.sub('[^0-9]', ' ', run_list).split()  # only run_numbers
            run_numbers = set(run_numbers)  # remove duplicates
            data = run_registry.get_lumi_sections_by_list(run_numbers)
            table = RunRegistryLumiSectionTable(data)
            return render(request, self.template_name, {'table': table})
        return render(request, self.template_name)


@method_decorator(login_required, name="dispatch")
class RunRegistryCompareView(TemplateView):
    template_name = 'certhelper/compare_runregistry.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """run_min = request.POST.get("run_min")
        run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        run_registry = TrackerRunRegistryClient()
        if run_list:
            run_numbers = re.sub('[^0-9]', ' ', run_list).split()  # only run_numbers
            run_numbers = set(run_numbers)  # remove duplicates
            data = run_registry.get_runs_with_lumi_section_sum_by_list(run_numbers)
        else:
            data = run_registry.get_runs_by_range(run_min, run_max)
        """
        runs = RunInfo.objects.all()

        deviating, corresponding = runs.compare_with_run_registry()
        deviating_run_table = RunRegistryComparisonTable(deviating)
        corresponding_run_table = RunRegistryComparisonTable(corresponding)

        return render(request, self.template_name, {
            "table": deviating_run_table,
            "corresponding_table": corresponding_run_table
        })
