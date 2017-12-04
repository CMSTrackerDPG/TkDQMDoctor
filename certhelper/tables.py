import django_tables2 as tables
from django_tables2.utils import A
from .models import RunInfo, ReferenceRun

class RunInfoTable(tables.Table):
    edit   = tables.TemplateColumn('<a href="{% url \'certhelper:update\' record.id%}"><span class="glyphicon glyphicon-pencil"></a>', orderable=False)
    delete = tables.TemplateColumn('<a href="{% url \'certhelper:update\' record.id%}"><span class="glyphicon glyphicon-trash"></a>', orderable=False)

    class Meta:
        model = RunInfo
        fields = ('run_number', 
        'type',
        'reference_run.reference_run',
        'trackermap',
        'number_of_ls',
        'int_luminosity',
        'pixel',
        'sistrip',
        'tracking',
        'comment')
        attrs = {'class': 'table table table-hover table-bordered'}



class ReferenceRunTable(tables.Table):
    class Meta:
        model = ReferenceRun
        attrs = {'class': 'table table table-hover table-bordered'}