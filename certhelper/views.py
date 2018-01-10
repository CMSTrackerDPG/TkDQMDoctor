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

from .models import *
from .forms import *
from .tables import *

class CreateRun(generic.CreateView):
    """Form which allows for creation of a new entry in RunInfo
    """

    model = RunInfo
    form_class = RunInfoForm
    template_name_suffix = '_form'
    success_url = '/'

def listruns(request):
    """passes all RunInfo objects to list.html
    """

    table = RunInfoTable(RunInfo.objects.all())
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

class SummaryView(generic.ListView):
    """ Accumulates information that is needed in the Run Summary
    stores it in the 'context' object and passes that object to summary.html
    where it is then displayed.
    """

    template_name = 'certhelper/summary.html'
    context_object_name = 'runs'

    def get_queryset(self):
        return RunInfo.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)

        ids = RunInfo.objects.all().values_list('reference_run').distinct()
        context['refs'] = ReferenceRun.objects.filter(id__in=ids)

        context['sorted_by_type'] = RunInfo.objects.all().order_by('type')

        tmpsorted = RunInfo.objects.all().order_by('type')
        good_runs = tmpsorted.filter(pixel="Good",sistrip="Good",tracking="Good")
        bad_runs = tmpsorted.filter(Q(pixel="Bad") | Q(sistrip="Bad") | Q(tracking="Bad"))

        # General Remark:
        # These are SQL queries that you can copy paste into your dbtool.
        # Using the inbuilt Django functions is safer but does not give you as much control
 
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
        group by b.ID, good 
        order by type_id, -good""")        


        context['tkmap'] = RunInfo.objects.raw("""SELECT  *
                                                          from certhelper_runinfo a
                                                          order by type_id, trackermap""")


        context['certified'] = RunInfo.objects.raw("""SELECT *,  
        case runtype
            when 'Collisions' then  ((pixel='Good' or pixel='Lowstat') and (sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
            when 'Cosmics' then                                           ((sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat'))
        end as good
        from certhelper_runinfo a
	    inner join certhelper_type b
	    on a.type_id = b.ID 
        order by type_id, -good""")               

        return context


def clearsession(request):
    """Deletes all the entries in the RunInfo table and redicrets to '/'.
    """

    if request.method == 'POST':
        RunInfo.objects.all().delete()
        return HttpResponseRedirect('/')

    return render(request, 'certhelper/clearsession.html')



def logout_view(request):
    """ Logout current user
    """
        
    logout(request)
    return HttpResponseRedirect('/')
