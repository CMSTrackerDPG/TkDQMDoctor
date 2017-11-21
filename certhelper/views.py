from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.views import generic

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

def helper(request):
    return render(request, 'certhelper/helper.html')

