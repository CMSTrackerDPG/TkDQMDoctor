import django_tables2 as tables

from certhelper.utilities.utilities import (
    render_component,
    render_trackermap,
    render_boolean_cell,
)
from utilities.luminosity import format_integrated_luminosity
from .models import RunInfo, ReferenceRun


class SimpleRunInfoTable(tables.Table):
    userid = tables.Column(verbose_name="Shifter")
    run_number = tables.Column()
    type = tables.Column()
    reference_run = tables.Column()
    trackermap = tables.Column()
    number_of_ls = tables.Column()
    int_luminosity = tables.Column()
    pixel = tables.Column()
    sistrip = tables.Column(verbose_name="SiStrip")
    tracking = tables.Column()
    comment = tables.Column()
    date = tables.Column()

    class Meta:
        model = RunInfo
        fields = ()
        attrs = {"class": "table table-hover table-bordered"}

    def render_reference_run(self, record):
        return record.reference_run.reference_run

    def render_int_luminosity(self, value):
        return format_integrated_luminosity(value)

    def render_pixel(self, record):
        return render_component(record.pixel, record.pixel_lowstat)

    def render_sistrip(self, record):
        return render_component(record.sistrip, record.sistrip_lowstat)

    def render_tracking(self, record):
        return render_component(record.tracking, record.tracking_lowstat)

    def render_trackermap(self, value):
        return render_trackermap(value)


class RunInfoTable(SimpleRunInfoTable):
    edit_run = tables.TemplateColumn(
        '<div align="center"><a href="{% url \'certhelper:update\' record.id%}">'
        '<span class="glyphicon glyphicon-pencil"></a></div>',
        orderable=False,
        verbose_name="Edit",
    )

    class Meta:
        attrs = {"class": "table table-hover table-bordered"}


class ShiftleaderRunInfoTable(RunInfoTable):
    delete_run = tables.TemplateColumn(
        '<div align="center"><a href="{% url \'certhelper:delete\' record.id%}">'
        '<span class="glyphicon glyphicon-trash"></a></div>',
        orderable=False,
        verbose_name="Delete",
    )

    class Meta:
        attrs = {"class": "table table-hover table-bordered"}


class ReferenceRunTable(tables.Table):
    class Meta:
        model = ReferenceRun
        fields = [
            "id",
            "reference_run",
            "reco",
            "runtype",
            "bfield",
            "beamtype",
            "beamenergy",
            "dataset",
        ]
        attrs = {"class": "table table-hover table-bordered"}


class DeletedRunInfoTable(tables.Table):
    restore_run = tables.TemplateColumn(
        '<div align="center"><a href="{% url \'certhelper:restore_run\' record.id%}">'
        '<span class="glyphicon glyphicon-repeat"></a></div>',
        orderable=False,
    )

    delete_forever = tables.TemplateColumn(
        '<div align="center"><a href="{% url \'certhelper:hard_delete_run\' record.id%}">'
        '<span class="glyphicon glyphicon-trash " style="color:red"></a></div>',
        orderable=False,
    )

    class Meta:
        model = RunInfo
        fields = (
            "id",
            "deleted_at",
            "userid",
            "run_number",
            "type",
            "reference_run.reference_run",
            "date",
        )
        attrs = {"class": "table table-hover table-bordered"}


class RunRegistryTable(tables.Table):
    shifter = tables.Column()
    run_number = tables.Column()
    run_class = tables.Column()
    dataset = tables.Column()
    # lumi_sections = tables.Column()
    state = tables.Column()
    pixel = tables.Column()
    sistrip = tables.Column()
    tracking = tables.Column()

    class Meta:
        attrs = {"class": "table table-hover table-bordered"}

    def render_pixel(self, record):
        return render_component(record.get("pixel"), record.get("pixel_lowstat"))

    def render_sistrip(self, record):
        return render_component(record.get("sistrip"), record.get("sistrip_lowstat"))

    def render_tracking(self, record):
        return render_component(record.get("tracking"), record.get("tracking_lowstat"))


class RunRegistryLumiSectionTable(tables.Table):
    run_number = tables.Column()
    lhcfill = tables.Column()
    dataset = tables.Column()
    section_from = tables.Column()
    section_to = tables.Column()
    section_count = tables.Column()
    cms_active = tables.Column()
    beam1_stable = tables.Column()
    beam2_stable = tables.Column()
    beam1_present = tables.Column()
    beam2_present = tables.Column()
    tibtid = tables.Column()
    tob = tables.Column()
    tecp = tables.Column()
    tecm = tables.Column()
    bpix = tables.Column()
    fpix = tables.Column()

    class Meta:
        attrs = {"class": "table table-hover table-bordered"}

    def render_cms_active(self, value):
        return render_boolean_cell(value)

    def render_beam1_stable(self, value):
        return render_boolean_cell(value)

    def render_beam2_stable(self, value):
        return render_boolean_cell(value)

    def render_beam1_present(self, value):
        return render_boolean_cell(value)

    def render_beam2_present(self, value):
        return render_boolean_cell(value)

    def render_tibtid(self, value):
        return render_boolean_cell(value)

    def render_tob(self, value):
        return render_boolean_cell(value)

    def render_tecp(self, value):
        return render_boolean_cell(value)

    def render_tecm(self, value):
        return render_boolean_cell(value)

    def render_bpix(self, value):
        return render_boolean_cell(value)

    def render_fpix(self, value):
        return render_boolean_cell(value)


class RunRegistryComparisonTable(tables.Table):
    run_number = tables.Column()
    type__runtype = tables.Column()
    type__reco = tables.Column()
    pixel = tables.Column()
    sistrip = tables.Column()
    tracking = tables.Column()

    class Meta:
        attrs = {"class": "table table-hover table-bordered"}

    def render_pixel(self, record):
        return render_component(record.get("pixel"), record.get("pixel_lowstat"))

    def render_sistrip(self, record):
        return render_component(record.get("sistrip"), record.get("sistrip_lowstat"))

    def render_tracking(self, record):
        return render_component(record.get("tracking"), record.get("tracking_lowstat"))
