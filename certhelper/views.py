from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django_tables2 import RequestConfig, SingleTableView
from terminaltables import AsciiTable

from certhelper.filters import RunInfoFilter
from certhelper.utilities.RunInfoTypeList import RunInfoTypeList
from certhelper.utilities.utilities import get_date_string, is_valid_date
from .forms import *
from .tables import *


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

    # We make sure that the logged in user can only see his own runs
    # In case the user is not logged in we show all objects
    # but remove the edit and remove buttons from the tableview.
    if request.user.is_authenticated():
        run_info_list = RunInfo.objects.filter(userid=request.user)
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = RunInfoTable(run_info_filter.qs)
    else:
        run_info_list = RunInfo.objects.all()
        run_info_filter = RunInfoFilter(request.GET, queryset=run_info_list)
        table = READONLYRunInfoTable(run_info_filter.qs)

    RequestConfig(request).configure(table)

    year = request.GET.get('date_year', '')
    month = request.GET.get('date_month', '')
    day = request.GET.get('date_day', '')

    the_date = get_date_string(year, month, day)

    category = request.GET.get('category', '')
    subcategory = request.GET.get('subcategory', '')
    subsubcategory = request.GET.get('subsubcategory', '')

    filter_parameters = ""

    if the_date:
        filter_parameters += "?date=" + str(the_date)
    if category:
        if not filter_parameters:
            filter_parameters += "?"
        else:
            filter_parameters += "&"
        filter_parameters += "category=" + category
        if subcategory:
            filter_parameters += "&subcategory=" + subcategory
            if subsubcategory:
                filter_parameters += "&subsubcategory=" + subsubcategory

    return render(request, 'certhelper/list.html', {
        'table': table,
        'filter': run_info_filter,
        'the_date': the_date,
        'filter_parameters': filter_parameters,
    })


class ListReferences(SingleTableView):
    """Display ReferenceRuns in a tableview
    !!! USES DJANGO-TABLES2 !!! 
    """

    model = ReferenceRun
    table_class = ReferenceRunTable


class UpdateRun(generic.UpdateView):
    """Updates a specific Run from the RunInfo table
    """

    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name = 'certhelper/runinfo_form.html'

    def form_valid(self, form_class):
        form_class.instance.userid = self.request.user
        return super(UpdateRun, self).form_valid(form_class)


class DeleteRun(generic.DeleteView):
    """Deletes a specific Run from the RunInfo table    
    """

    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name_suffix = '_delete_form'


class CreateType(generic.CreateView):
    """Form to create a new Type (RunType)
    """

    model = Type
    form_class = TypeForm
    template_name_suffix = '_form'
    success_url = '/create'


class SummaryAsciiTable:
    """
    Used to print the AsciiTables in the summary view
    """

    def __init__(self, thetype, tableColumnDescriptions):
        self.mytype = thetype.__str__()
        self.data = [tableColumnDescriptions]

    def add_row(self, row):
        self.data.append(row)

    def print(self):
        print(self.mytype)
        table = AsciiTable(self.data)
        table.inner_row_border = True
        print(table.table)

    def get_type(self):
        return self.mytype

    def get_table(self):
        table = AsciiTable(self.data)
        table.inner_row_border = True
        return table.table


def is_valid_id(id, Classname):
    try:
        if Classname.objects.filter(pk=id):
            return True
    except:
        return False
    return False


def summaryView(request):
    """ Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """
    runs = RunInfo.objects.filter(userid=request.user)

    date_filter_value = request.GET.get('date', None)
    category_id = request.GET.get('category', None)
    subcategory_id = request.GET.get('subcategory', None)
    subsubcategory_id = request.GET.get('subsubcategory', None)
    alert_errors = []
    alert_infos = []

    if date_filter_value:
        if is_valid_date(date_filter_value):
            runs = runs.filter(date=date_filter_value)
        else:
            alert_errors.append("Invalid Date: " + str(date_filter_value))
            runs = RunInfo.objects.none()

    if category_id:
        if is_valid_id(category_id, Category):
            runs = runs.filter(category=category_id)
            if subcategory_id:
                if is_valid_id(subcategory_id, SubCategory):
                    runs = runs.filter(subcategory=subcategory_id)

                    if subsubcategory_id:
                        if is_valid_id(subsubcategory_id, SubSubCategory):
                            runs = runs.filter(subsubcategory=subsubcategory_id)
                        else:
                            alert_errors.append("Invalid SubSubCategory ID: " + str(subsubcategory_id))
                            runs = RunInfo.objects.none()
                else:
                    alert_errors.append("Invalid SubCategory ID: " + str(subcategory_id))
                    runs = RunInfo.objects.none()
        else:
            alert_errors.append("Invalid Category ID: " + str(category_id))
            runs = RunInfo.objects.none()

    if not date_filter_value and not category_id:
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

    return render(request, 'certhelper/summary.html', context)


def clearsession(request):
    """Deletes all the entries in the RunInfo table and redicrets to '/'.
    """

    if request.method == 'POST':
        RunInfo.objects.filter(userid=request.user).delete()
        return HttpResponseRedirect('/')

    return render(request, 'certhelper/clearsession.html')


def logout_view(request):
    """ Logout current user
    """

    logout(request)
    return HttpResponseRedirect('/')


def load_subcategories(request):
    category_id = request.GET.get('categoryid')
    if (category_id):
        subcategories = SubCategory.objects.filter(parent_category=category_id).order_by('name')
    else:
        subcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html', {'categories': subcategories})


def load_subsubcategories(request):
    subcategory_id = request.GET.get('subcategoryid')
    if (subcategory_id):
        subsubcategories = SubSubCategory.objects.filter(parent_category=subcategory_id).order_by('name')
    else:
        subsubcategories = SubCategory.objects.none()
    return render(request, 'certhelper/dropdowns/category_dropdown_list_options.html', {'categories': subsubcategories})
