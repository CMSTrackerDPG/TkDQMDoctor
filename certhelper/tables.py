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
        'type.reco',
        'type.runtype',
        'type.bfield',
        'type.beamtype',
        'reference.reference_run',
        'trackermap',
        'number_of_ls',
        'integrated_luminosity',
        'pixel',
        'sistrip',
        'tracking',
        'comment')