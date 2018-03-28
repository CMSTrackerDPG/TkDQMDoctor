import django_tables2 as tables
from django_tables2.utils import A
from .models import RunInfo, ReferenceRun

class RunInfoTable(tables.Table):
    edit   = tables.TemplateColumn('<div align="center"><a href="{% url \'certhelper:update\' record.id%}"><span class="glyphicon glyphicon-pencil"></a></div>', orderable=False)
    delete = tables.TemplateColumn('<div align="center"><a href="{% url \'certhelper:delete\' record.id%}"><span class="glyphicon glyphicon-trash"></a></div>', orderable=False)

    class Meta:
        model = RunInfo
        fields = ('userid',
        'run_number', 
        'type',
        'reference_run.reference_run',
        'trackermap',
        'number_of_ls',
        'int_luminosity',
        'pixel',
        'sistrip',
        'tracking',
        'comment',
        'date')
        attrs = {'class': 'table table table-hover table-bordered'}


class READONLYRunInfoTable(tables.Table):

    class Meta:
        model = RunInfo
        fields = ('userid',
        'run_number', 
        'type',
        'reference_run.reference_run',
        'trackermap',
        'number_of_ls',
        'int_luminosity',
        'pixel',
        'sistrip',
        'tracking',
        'comment',
        'date')
        attrs = {'class': 'table table table-hover table-bordered'}



class ReferenceRunTable(tables.Table):
    class Meta:
        model = ReferenceRun
        attrs = {'class': 'table table table-hover table-bordered'}