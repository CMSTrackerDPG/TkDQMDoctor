import django_tables2 as tables
from django_tables2.utils import A
from .models import RunInfo

class RunInfoTable(tables.Table):
    edit = tables.LinkColumn(
    viewname = 'certhelper:update', 
    args=[A('pk')],
    text="edit",
    accessor=A('__str__'),
    orderable=False)

    delete = tables.LinkColumn(
    viewname = 'certhelper:delete', 
    args=[A('pk')],
    text="delete",
    accessor=A('__str__'),
    orderable=False)

    class Meta:
        model = RunInfo
        fields = ('run_number', 
        'type',
        # 'type.runtype',
        # 'type.bfield',
        # 'type.beamtype',
        # 'type.dataset',
        'reference.reference_run',
        'trackermap',
        'number_of_ls',
        'int_luminosity',
        'pixel',
        'sistrip',
        'tracking',
        'comment')
        attrs = {'class': 'table table table-hover table-bordered'}