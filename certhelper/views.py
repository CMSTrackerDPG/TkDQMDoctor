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

from certhelper.filters import (
    RunInfoFilter,
    ShiftLeaderRunInfoFilter,
    ComputeLuminosityRunInfoFilter,
    RunsFilter,
)
from certhelper.models import UserProfile
from certhelper.utilities.ShiftLeaderReport import ShiftLeaderReport
from certhelper.utilities.SummaryReport import SummaryReport
from certhelper.utilities.utilities import (
    get_filters_from_request_GET,
    request_contains_filter_parameter,
    get_this_week_filter_parameter,
    get_today_filter_parameter,
    get_runs_from_request_filters,
    get_runinfo_from_request,
    number_string_to_list,
    integer_or_none,
    convert_run_registry_to_runinfo,
)
from runregistry.client import TrackerRunRegistryClient
from .forms import *
from .tables import *


@method_decorator(login_required, name="dispatch")
class CreateRun(generic.CreateView):
    """
    Class based view to create new RunInfo instances.

    Used by shifters to certify new runs.
    """

    model = RunInfo
    form_class = RunInfoWithChecklistForm
    template_name = "certhelper/runinfo_form.html"
    success_url = "/"

    def form_valid(self, form_class):
        """
        Adds the logged in user into the form data, when the form is valid.
        """
        form_class.instance.userid = self.request.user
        return super(CreateRun, self).form_valid(form_class)


def listruns(request):
    """
    View to list all certified runs
    """
    if not request_contains_filter_parameter(request):
        return HttpResponseRedirect("/%s" % get_today_filter_parameter())

    context = {}

    """
    Make sure that the logged in user can only see his own runs
    In case the user is not logged in show all objects,
    but remove the edit and remove buttons from the tableview.
    """
    if request.user.is_authenticated:
        run_info_list = RunInfo.objects.filter(userid=request.user)
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = RunInfoTable(run_info_filter.qs)

        mismatching_runs, mismatching_run_registy_runs = (
            run_info_filter.qs.compare_with_run_registry()
        )
        if len(mismatching_runs) != 0:
            context["mismatching_runs"] = [
                run["run_number"] for run in mismatching_runs
            ]
    else:
        run_info_list = RunInfo.objects.all()
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = SimpleRunInfoTable(run_info_filter.qs)

    RequestConfig(request).configure(table)

    applied_filters = get_filters_from_request_GET(request)
    filter_parameters = ""
    for key, value in applied_filters.items():
        filter_parameters += "&" if filter_parameters.startswith("?") else "?"
        filter_parameters += key + "=" + value

    context["filter_parameters"] = filter_parameters
    context["table"] = table
    context["filter"] = run_info_filter
    context["run_registry_online"] = TrackerRunRegistryClient().connection_possible()
    return render(request, "certhelper/list.html", context)


@method_decorator(login_required, name="dispatch")
class ListReferences(SingleTableView):
    """
    Displays all ReferenceRuns
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
    template_name = "certhelper/runinfo_form.html"

    def get_context_data(self, **kwargs):
        """
        Add extra data for the template
        """
        context = super().get_context_data(**kwargs)
        context["checklist_not_required"] = True
        return context

    def same_user_or_shiftleader(self, user):
        """
        Checks if the user trying to edit the run is the same user
        that created the run, has at least shift leader rights
        or is a super user (admin)
        """
        try:
            return (
                self.get_object().userid == user
                or user.is_superuser
                or user.userprofile.has_shift_leader_rights
            )
        except UserProfile.DoesNotExist:
            return False

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user that tries to update the run has the necessary rights
        """
        if self.same_user_or_shiftleader(request.user):
            return super(UpdateRun, self).dispatch(request, *args, **kwargs)
        return redirect_to_login(
            request.get_full_path(), login_url=reverse("admin:login")
        )

    def get_success_url(self):
        """
        return redirect url after updating a run
        """
        is_same_user = self.get_object().userid == self.request.user
        return reverse("certhelper:shiftleader") if not is_same_user else "/"


@method_decorator(login_required, name="dispatch")
class DeleteRun(generic.DeleteView):
    """
    Deletes a specific Run from the RunInfo table
    """

    model = RunInfo
    form_class = RunInfoForm
    success_url = "/shiftleader/"
    template_name_suffix = "_delete_form"


@method_decorator(login_required, name="dispatch")
class CreateType(generic.CreateView):
    """
    Class based view to create a new Type (RunType)
    """

    model = Type
    form_class = TypeForm
    template_name_suffix = "_form"
    success_url = "/create"


@login_required
def summaryView(request):
    """
    Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """

    alert_errors = []
    alert_infos = []
    alert_filters = []

    runs = get_runs_from_request_filters(
        request, alert_errors, alert_infos, alert_filters
    )

    summary = SummaryReport(runs)

    context = {
        "refs": summary.reference_runs(),
        "runs": summary.runs_checked_per_type(),
        "tk_maps": summary.tracker_maps_per_type(),
        "certified_runs": summary.certified_runs_per_type(),
        "sums": summary.sum_of_quantities_per_type(),
        "alert_errors": alert_errors,
        "alert_infos": alert_infos,
        "alert_filters": alert_filters,
    }

    return render(request, "certhelper/summary.html", context)


@login_required
def logout_view(request):
    """
    Logout current user (also from CERN)
    """
    if request.user.is_authenticated:
        logout(request)
        callback_url = "https://login.cern.ch/adfs/ls/?wa=wsignout1.0&ReturnUrl="
        callback_url += "http%3A//"
        callback_url += request.META["HTTP_HOST"]
        callback_url += reverse("certhelper:logout_status")
        return HttpResponseRedirect(callback_url)
    return HttpResponseRedirect("/")


def logout_status(request):
    """
    Simple status page which should help determining
    if the logout was successful or not
    """
    logout_successful = not request.user.is_authenticated
    return render(
        request,
        "certhelper/logout_status.html",
        {"logout_successful": logout_successful},
    )


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
        context["summary"] = SummaryReport(self.filterset.qs)
        context["slreport"] = ShiftLeaderReport(self.filterset.qs)
        context["deleted_runs"] = DeletedRunInfoTable(
            RunInfo.all_objects.dead().order_by("-run_number")
        )
        try:
            context["slchecklist"] = Checklist.objects.get(identifier="shiftleader")
        except Checklist.DoesNotExist:
            # shift leader checklist has not been created yet.
            pass

        deviating, corresponding = self.filterset.qs.compare_with_run_registry()

        if deviating:
            context["runinfo_comparison_table"] = RunRegistryComparisonTable(deviating)
            context["run_registry_comparison_table"] = RunRegistryComparisonTable(
                corresponding
            )

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
            "Multiple certifications with the runnumber {} exist".format(run_number)
        )

    if request.method == "POST":
        run.hard_delete()
        return HttpResponseRedirect("/")

    return render(request, "certhelper/hard_delete.html", {"run": run})


@staff_member_required
def hard_delete_run_view(request, pk):
    try:
        run = RunInfo.all_objects.get(pk=pk)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the id {} doesnt exist".format(pk))

    if request.method == "POST":
        run.hard_delete()
        return HttpResponseRedirect("/shiftleader/")

    return render(request, "certhelper/hard_delete.html", {"run": run})


@staff_member_required
def restore_run_view(request, pk):
    try:
        run = RunInfo.all_objects.get(pk=pk)
    except RunInfo.DoesNotExist:
        raise Http404("The run with the id {} doesnt exist".format(pk))

    if request.method == "POST":
        run.restore()
        return HttpResponseRedirect("/shiftleader/")

    return render(request, "certhelper/restore.html", {"run": run})


@login_required
def validate_central_certification_list(request):
    text = request.GET.get("text", None)
    run_numbers = re.sub("[^0-9]", " ", text).split()  # only run_numbers
    run_numbers = set(run_numbers)  # remove duplicates
    data = RunInfo.objects.check_if_certified(run_numbers)
    return JsonResponse(data)


# TODO update Checklist by Checklist model, return 404 if page doesnt exist
class ChecklistTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checklist_base_template_name"] = "certhelper/checklists/base.html"
        return context


@login_required
def check_integrity_of_run(request):
    """
    Checks if a run with the same number but different type already exists and checks
    if all the attributes (int. lumi, number of ls, pixel, sistrip, ...) match.

    :param request:
    :return: JsonResponse containing the attributes that do not match and their
    expected value
    """
    try:
        assert integer_or_none(request.GET.get("run_number", None))
        run = get_runinfo_from_request(request)
        data = RunInfo.objects.check_integrity_of_run(run)
        return JsonResponse(data)
    except AssertionError:
        return JsonResponse({})


@method_decorator(login_required, name="dispatch")
class ComputeLuminosityView(FilterView):
    template_name = "certhelper/compute_luminosity.html"
    filterset_class = ComputeLuminosityRunInfoFilter


@method_decorator(login_required, name="dispatch")
class RunRegistryView(TemplateView):
    template_name = "certhelper/runregistry.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        run_min = request.POST.get("run_min")
        run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        run_registry = TrackerRunRegistryClient()

        if run_list:
            run_numbers = number_string_to_list(run_list)
            data = run_registry.get_runs_by_list(run_numbers)
        elif run_min and run_max:
            data = run_registry.get_runs_by_range(run_min, run_max)
        else:
            data = {}

        table = RunRegistryTable(data)

        return render(request, self.template_name, {"table": table})


@method_decorator(login_required, name="dispatch")
class RunRegistryLumiSectionView(TemplateView):
    template_name = "certhelper/lumisections.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        run_min = request.POST.get("run_min")
        run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        run_registry = TrackerRunRegistryClient()

        if run_list:
            run_numbers = number_string_to_list(run_list)
            data = run_registry.get_lumi_sections_by_list(run_numbers)
        elif run_min and run_max:
            data = run_registry.get_lumi_sections_by_range(run_min, run_max)
        else:
            data = {}

        table = RunRegistryLumiSectionTable(data)
        return render(request, self.template_name, {"table": table})


@method_decorator(login_required, name="dispatch")
class RunRegistryCompareView(TemplateView):
    template_name = "certhelper/compare_runregistry.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        run_min = request.POST.get("run_min")
        run_max = request.POST.get("run_max")
        run_list = request.POST.get("run_list")

        if run_list:
            run_numbers = number_string_to_list(run_list)
            runs = RunInfo.objects.filter(run_number__in=run_numbers)
        elif run_min and run_max:
            runs = RunInfo.objects.filter(
                run_number__gte=run_min, run_number__lte=run_max
            )
            runs.print()
        else:
            runs = RunInfo.objects.none()

        deviating, corresponding = runs.compare_with_run_registry()

        deviating_run_table = RunRegistryComparisonTable(deviating)
        run_registry_table = RunRegistryComparisonTable(corresponding)

        return render(
            request,
            self.template_name,
            {"table": deviating_run_table, "run_registry_table": run_registry_table},
        )


def runregistry(request, run_number):
    client = TrackerRunRegistryClient()
    if not client.connection_possible():
        return JsonResponse("Run Registry is unavailable.")
    response = client.get_runs_by_list([run_number])
    runs = convert_run_registry_to_runinfo(response)
    return JsonResponse(runs, safe=False, json_dumps_params={"indent": 2})


class RunsView(FilterView):
    model = RunInfo
    template_name = "certhelper/runsview.html"
    filterset_class = RunsFilter

    def get_context_data(self, **kwargs):
        """
        Add extra data for the template
        """
        context = super().get_context_data(**kwargs)

        context["run_numbers"] = self.filterset.qs.run_numbers()
        return context


@staff_member_required
def problems_json(request):
    # TODO improve this code
    categories_dict = Category.objects.all().values()
    for c in categories_dict:
        category = Category.objects.get(id=c["id"])
        c["full_display_name"] = str(category)
        c["runs"] = list(
            category.runinfo_set.all().values_list("run_number", "type__reco")
        )
    return JsonResponse(list(categories_dict), safe=False)


@staff_member_required
def runs_json(request):
    # Note: "problem_categories" have to be retrieved separately,
    # since there is no easy way to retrieve them inline

    runs = RunInfo.objects.all().values(
        "run_number",
        "type__reco",
        "type__runtype",
        "type__bfield",
        "type__beamtype",
        "type__beamenergy",
        "type__dataset",
        "reference_run__reference_run",
        "reference_run__reco",
        "reference_run__runtype",
        "reference_run__bfield",
        "reference_run__beamtype",
        "reference_run__beamenergy",
        "reference_run__dataset",
        "trackermap",
        "number_of_ls",
        "int_luminosity",
        "pixel",
        "sistrip",
        "tracking",
        "pixel_lowstat",
        "sistrip_lowstat",
        "tracking_lowstat",
        "comment",
        "date",
    )

    return JsonResponse(list(runs), safe=False)


@staff_member_required
def problem_runs_json(request):
    # TODO improve this horrible code

    problem_runs = RunInfo.objects.all().exclude(problem_categories=None)
    problem_runs_dict = problem_runs.values(
        "run_number",
        "type__reco",
        "type__runtype",
        "type__bfield",
        "type__beamtype",
        "type__beamenergy",
        "type__dataset",
        "reference_run__reference_run",
        "reference_run__reco",
        "reference_run__runtype",
        "reference_run__bfield",
        "reference_run__beamtype",
        "reference_run__beamenergy",
        "reference_run__dataset",
        "trackermap",
        "number_of_ls",
        "int_luminosity",
        "pixel",
        "sistrip",
        "tracking",
        "pixel_lowstat",
        "sistrip_lowstat",
        "tracking_lowstat",
        "comment",
        "date",
    )

    for run in problem_runs_dict:
        problem_categories = problem_runs.get(
            run_number=run["run_number"], type__reco=run["type__reco"]
        ).problem_categories
        run["problem_names"] = [str(problem) for problem in problem_categories.all()]
        run["problem_ids"] = [problem.id for problem in problem_categories.all()]

    return JsonResponse(list(problem_runs_dict), safe=False)
