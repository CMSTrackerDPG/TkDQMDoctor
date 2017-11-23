from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from .models import *
from .forms import *

def index(request):
    return render(request, 'certhelper/index.html')

class CreateRun(generic.CreateView):
    model = RunInfo
    form_class = RunInfoForm
    template_name_suffix = '_form'
    success_url = '/'

class ListRuns(generic.ListView):
    template_name = 'certhelper/list.html'
    context_object_name = 'list'

    def get_queryset(self):
        return RunInfo.objects.all().order_by('run_number')

class ListBlocks(generic.ListView):
    template_name = 'certhelper/references.html'
    context_object_name = 'references'

    def get_queryset(self):
        return ReferenceRun.objects.all()

class UpdateRun(generic.UpdateView):
    model = RunInfo
    form_class = RunInfoForm
    success_url = '/'
    template_name_suffix = '_update_form'

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
