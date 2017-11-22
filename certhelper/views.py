from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from .models import RunInfo

def index(request):
    return render(request, 'certhelper/index.html')

class DetailView(generic.DetailView):
    model = RunInfo
    template_name = 'certhelper/detail.html'

class ListView(generic.ListView):
    template_name = 'certhelper/list.html'
    context_object_name = 'list'

    def get_queryset(self):
        return RunInfo.objects.all()

class CreateRun(generic.CreateView):
    model = RunInfo
    fields = '__all__'
    template_name_suffix = '_form'
    success_url = '/list'

class UpdateRun(generic.UpdateView):
    model = RunInfo
    fields = '__all__'
    success_url = '/list'
    template_name_suffix = '_update_form'

class DeleteRun(generic.DeleteView):
    model = RunInfo
    success_url = '/list'
    template_name_suffix = '_delete_form'
