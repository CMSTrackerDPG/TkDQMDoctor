"""
These forms are used to display data contained in models
of the corresponding name found in
TkDQMDoctor/dqmsite/certhelper/models.py

i.e.

FORM               |  MODEL
====================================
ReferenceRunForm   |  ReferenceRun
RunInfoForm        |  RunInfo
TypeForm           |  Type


======== Validity of the form  ========

If you want to check if a form is valid you need to add the clean(self) method.
For a sample implementation look at     RunInfoModelForm::clean(self)
It throws an error if some conditions on pixel, sistrip, tracking are not met and shows an errormessage
that you can set.
If everything is ok on the other hand, it returns the cleaned data which is then written to the db

======== Passing additional information to HTML from the from ========
Option 1)

Additional form information such as
        widgets = {                         vvvvvvvvvvvvvvvvvvvvvvvvvvvvv
            'int_luminosity': TextInput(attrs={ 'placeholder': "Unit: pb⁻¹ "})
        }
is needed so that in HTML when the form is displayed additional information is displayed.
In this instance it is used to display the placeholdertag in the int_luminosity textbox.
(greyed out text so that the user knows what SI-Unit to input)


Option 2)
The other option to add tags in html is through myfilters:
See /TkDQMDoctor/dqmsite/certhelper/templatetags/myfilters.py

for that to work, add in html:
                          vvvvvvvvvvvvvvvvvvvvvvv
    {{form.int_luminosity|addclass:'form-control'}}
This sets 'addclass="form-control"' in html for {{form.int_luminosity}}


Remarks:

It should be obvious that Option 1 produces easier to read code if you have a model
that has lots of attributes and you want to modify only a few of them.

Option2 on the other hand is prefered if you want to add styling (bootstrap classes for instance)
to a lot of you attributes of the Model.
"""
from categories.models import Category
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CheckboxSelectMultiple
from django.utils import timezone

from .models import RunInfo, Checklist, ReferenceRun, Type


class DateInput(forms.DateInput):
    input_type = 'date'


class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = ['reference_run', 'reco', 'runtype', 'bfield', 'beamtype',
                  'beamenergy', 'dataset', ]


class ChecklistFormMixin(forms.Form):
    """
    Adds mandatory Checklist checkboxes to the form
    E.g. general, trackermap, sistrip, pixel, tracking

    Form can only be submitted when all the checkboxes have been ticked

    Whether the checkbox is ticked or not is just checked client-side (html)
    and NOT server-side.

    Example Usage:
    form.checklist_sistrip -> renders the SiStrip Checklist checkbox
    """

    def __init__(self, *args, **kwargs):
        super(ChecklistFormMixin, self).__init__(*args, **kwargs)
        for checklist in Checklist.objects.all():
            field_name = "checklist_{}".format(checklist.identifier)
            # required in HTML field, not required in server-side form validation
            self.fields[field_name] = forms.BooleanField(required=False)

    def checklists(self):
        """
        returns a dictionary containing the fields (checkboxes) created in the __init__
        method and the corresponding Checklist model instances

        Example Usage:
        form.checklists.pixel.field -> returns the rendered Checklist checkbox
        form.checklists.pixel.checklist -> returns the Checklist model instance
        """
        checklist_list = {}  # List of checklists containing their checkbox items
        for checklist in Checklist.objects.all():
            field_name = "checklist_{}".format(checklist.identifier)
            checklist_list.update({
                checklist.identifier: {
                    "checklist": checklist,
                    "field": self[field_name]
                }})
        return checklist_list


class RunInfoForm(ModelForm):
    next = forms.CharField(required=False)

    date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2017, timezone.now().year + 2)),
        initial=timezone.now
    )

    class Meta:
        model = RunInfo

        fields = [
            'type',
            'reference_run',
            'run_number',
            'trackermap',
            'number_of_ls',
            'int_luminosity',
            'pixel',
            'pixel_lowstat',
            'sistrip',
            'sistrip_lowstat',
            'tracking',
            'tracking_lowstat',
            'comment',
            'date',
            'problem_categories',
        ]

        widgets = {
            'int_luminosity': TextInput(attrs={'placeholder': "Unit: /pb "}),
        }

    def __init__(self, *args, **kwargs):
        super(RunInfoForm, self).__init__(*args, **kwargs)

        self.fields["problem_categories"].widget = CheckboxSelectMultiple()
        self.fields["problem_categories"].queryset = Category.objects.all()

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_sistrip_bad = cleaned_data.get('sistrip') == 'Bad'
        is_tracking_good = cleaned_data.get('tracking') == 'Good'

        if is_sistrip_bad and is_tracking_good:
            self.add_error(None, ValidationError(
                "Tracking can not be GOOD if SiStrip is BAD. Please correct."))

        run_type = cleaned_data.get('type')
        reference_run = cleaned_data.get('reference_run')

        if run_type and reference_run:
            if run_type.runtype != reference_run.runtype:
                self.add_error(None, ValidationError(
                    "Reference run is incompatible with selected Type. ({} != {})"
                        .format(run_type.runtype, reference_run.runtype)))

        return cleaned_data


class RunInfoWithChecklistForm(ChecklistFormMixin, RunInfoForm):
    pass


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ["reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]
        widgets = {
            'dataset': TextInput(
                attrs={'placeholder': "e.g. /Cosmics/Run2017F-PromptReco-v1/DQMIO",
                       'class': "form-control"}),
        }
