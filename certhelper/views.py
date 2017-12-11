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
    model = RunInfo
    form_class = RunInfoForm
    template_name_suffix = '_form'
    success_url = '/'

def listruns(request):
    table = RunInfoTable(RunInfo.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'certhelper/list.html', {'table': table})

class ListReferences(SingleTableView):
    model = ReferenceRun
    table_class = ReferenceRunTable

class UpdateRun(generic.UpdateView):
    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name = 'certhelper/runinfo_form.html'

class DeleteRun(generic.DeleteView):
    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name_suffix = '_delete_form'


class CreateType(generic.CreateView):
    model = Type
    form_class = TypeForm
    template_name_suffix = '_form'
    success_url = '/create'

class SummaryView(generic.ListView):
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

        
        # context['sums'] = RunInfo.objects.raw("""SELECT *,((pixel='Good' or pixel='Lowstat') and (sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat')) as good, 
        #                                                    SUM(number_of_ls) as sum_number_of_ls,
        #                                                    SUM(int_luminosity) as sum_int_luminosity 
        #                                                    FROM certhelper_runinfo a 
        #                                                    inner join certhelper_type b 
        #                                                    on a.type_id = b.ID 
        #                                                    group by b.ID, good 
        #                                                    order by type_id, -good""")


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

# DOES NOT TAKE Lowstat into a ccoutn
        # context['certified'] = RunInfo.objects.raw("""SELECT *,((pixel='Good' or pixel='Lowstat') and (sistrip='Good' or sistrip='Lowstat') and (tracking='Good' or tracking='Lowstat')) as good
        #                                                         from certhelper_runinfo a
        #                                                         order by type_id, -good""")                                                          


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
    if request.method == 'POST':
        RunInfo.objects.all().delete()
        return HttpResponseRedirect('/')

    return render(request, 'certhelper/clearsession.html')



def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
