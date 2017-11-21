from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

from .models import RunInfo


def detail(request, runinfo_id):
    runinfo = get_object_or_404(RunInfo, pk=runinfo_id)
    return render(request, 'certhelper/detail.html', {'runinfo': runinfo})

def list(request):
    l = RunInfo.objects.all()
    template = loader.get_template('certhelper/list.html')
    context = {'list': l, }
    return HttpResponse(template.render(context, request))

def helper(request):
    return render(request, 'certhelper/helper.html')

def index(request):
    return render(request, 'certhelper/index.html')