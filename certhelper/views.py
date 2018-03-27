from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.db.models import Case, When, Value, BooleanField
from django.db.models import Sum, Q, F
from django_tables2 import RequestConfig, SingleTableView
from django.contrib.auth import logout
from django.db.models.expressions import RawSQL

from .models import *
from .forms import *
from .tables import *

from terminaltables import AsciiTable

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
        table = RunInfoTable(RunInfo.objects.filter(userid=request.user))
    else:
        table = READONLYRunInfoTable(RunInfo.objects.all())

    RequestConfig(request).configure(table)

    return render(request, 'certhelper/list.html', {'table': table})


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

class SummaryView(generic.ListView):
    """ Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """
    template_name = 'certhelper/summary.html'
    context_object_name = 'runs'

    def get_queryset(self):
        return RunInfo.objects.filter(userid=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)

        """Retrieve all runs from the current user"""
        CurrentUserRunInfos = RunInfo.objects.filter(userid=self.request.user)

        ids = CurrentUserRunInfos.values_list('reference_run').distinct()

        context['refs'] = ReferenceRun.objects.filter(id__in=ids)

        context['sorted_by_type'] = CurrentUserRunInfos.order_by('type')

        tmpsorted = CurrentUserRunInfos.order_by('type')
        good_runs = tmpsorted.filter(pixel="Good",sistrip="Good",tracking="Good")
        bad_runs = tmpsorted.filter(Q(pixel="Bad") | Q(sistrip="Bad") | Q(tracking="Bad"))

        userRunInfoTypes = RunInfo \
            .objects \
            .filter(userid=self.request.user) \
            .values('type') \
            .order_by('type', 'run_number') \
            .distinct()

        columnDescription = ["Run", "Reference Run", "Number of LS", "Int. Luminosity", "Pixel", "Strip", "Tracking",
                             "Comment"]

        """ Get a list of unique type ids (for cosmics, prompt, etc.)"""
        type_id_list = []
        for entry in userRunInfoTypes:
            if entry['type'] not in type_id_list:
                type_id_list.append(entry['type'])

        """ Create one AsciiTable per Type and fill it with the appropriate data"""
        ascii_tables = []
        for type_id in type_id_list:
            userRunInfosPerType = CurrentUserRunInfos.filter(type_id=type_id).order_by("run_number")

            """Extract the type from the first element, all types in that list are the same"""
            the_type = userRunInfosPerType[0].type
            """Create a AsciiTable with just the column descriptions as the first row"""
            ascii_tables.append(SummaryAsciiTable(the_type, columnDescription))
            for run in userRunInfosPerType:
                """ add a new row to the lastly created AsciiTable"""
                ascii_tables[-1].add_row([
                    run.run_number,
                    run.reference_run.reference_run,
                    run.number_of_ls,
                    run.int_luminosity,
                    run.pixel,
                    run.sistrip,
                    run.tracking,
                    run.comment
                ])

        """Provide the context for the summary template"""
        context["ascii_tables"] = ascii_tables

        # ====================================================================================================================
         
        context['sums'] = RunInfo.objects.raw("""SELECT *,
        case runtype
            when 'Collisions' then  ((pixel='Good' or pixel='Lowstat') and (sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
            when 'Cosmics' then                                           ((sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
        end as good, 
        SUM(number_of_ls) as sum_number_of_ls,
        SUM(int_luminosity) as sum_int_luminosity 
        FROM certhelper_runinfo a 
        inner join certhelper_type b 
        on a.type_id = b.ID
        where userid_id = %s  
        group by b.ID, good
        order by type_id, -good""", [self.request.user.id]) 

        # ====================================================================================================================

        context['tkmap'] = CurrentUserRunInfos.order_by('type_id', 'trackermap')

        # ====================================================================================================================

        # When is a RUN marked as 'Good'?
        # Depends on runtype:
        # | - - - - - - - - - - - - - - - - - - - - - - - - - - |
        # |-(Collisions) pixel    = (Good OR Lowstat)   AND     |      
        # |              sistrip  = (Good OR Lowstat)   AND     |
        # |              tracking = (Good OR Lowstat)           |
        # | - - - - - - - - - - - - - - - - - - - - - - - - - - |
        # |-(Cosmics)    sistrip  = (Good OR Lowstat)   AND     |   
        # |              tracking = (Good OR Lowstat)           |
        #  - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        context['certified'] = RunInfo.objects.raw('''SELECT *,
        case runtype
            when 'Collisions' then  ((pixel='Good' or pixel='Lowstat') and (sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
            when 'Cosmics' then                                           ((sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
        end as good
        from certhelper_runinfo a
	    inner join certhelper_type b
	    on a.type_id = b.ID
        where userid_id = %s
        order by type_id, -good''', [self.request.user.id])          
        # ====================================================================================================================
        
        return context

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
