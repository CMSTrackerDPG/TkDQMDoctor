from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from django.db.models import Sum, Q

from django_tables2 import RequestConfig

from .models import *
from .forms import *
from .tables import *

def index(request):
    return render(request, 'certhelper/index.html')

class CreateRun(generic.CreateView):
    model = RunInfo
    form_class = RunInfoForm
    template_name_suffix = '_form'
    success_url = '/'

def listruns(request):
    table = RunInfoTable(RunInfo.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'certhelper/list.html', {'table': table})

class ListBlocks(generic.ListView):
    template_name = 'certhelper/references.html'
    context_object_name = 'references'

    def get_queryset(self):
        return ReferenceRun.objects.all()

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
        
        context['sorted_by_type'] = RunInfo.objects.all().order_by('type')

        ids = RunInfo.objects.all().values_list('reference').distinct()
        context['refs'] = ReferenceRun.objects.filter(id__in=ids)

        tmpsorted = RunInfo.objects.all().order_by('type')
        context['group_luminosity'] = tmpsorted.values('type').annotate(total=Sum('int_luminosity'))
        context['group_numberls'] = tmpsorted.values('type').annotate(total=Sum('number_of_ls'))

        context['group_good'] = tmpsorted.filter(pixel="Good",sistrip="Good",tracking="Good")
        context['group_bad'] = tmpsorted.filter(Q(pixel="Bad") | Q(sistrip="Bad") | Q(tracking="Bad"))
        return context


def clearsession(request):
    if request.method == 'POST':
        RunInfo.objects.all().delete()
        return HttpResponseRedirect('/')

    return render(request, 'certhelper/clearsession.html')