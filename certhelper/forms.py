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

from django import forms
from django.forms import ModelForm, TextInput

from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = ['reference_run', 'reco', 'runtype', 'bfield', 'beamtype',
                  'beamenergy', 'dataset', ]


class ChecklistFormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChecklistFormMixin, self).__init__(*args, **kwargs)
        for checklist in Checklist.objects.all():
            for item in checklist.checklistitem_set.all():
                field_name = "checklist_{}_item_{}".format(checklist.pk, item.pk)
                self.fields[field_name] = \
                    forms.BooleanField(
                        label=item.short_description,
                        required=True,
                        help_text=item.description
                    )
                self[field_name].modal_name = item.modal_name if item.modal_name else ""

    def checklists(self):
        checklist_list = []  # List of checklists containing their checkbox items
        for checklist in Checklist.objects.all():
            tmp_list = {"name": checklist.name, "items": []}
            for name, field in self.fields.items():
                if name.startswith("checklist_{}_".format(checklist.pk)):
                    tmp_list["items"].append(self[name])
            checklist_list.append(tmp_list)
        return checklist_list


class RunInfoForm(ModelForm):
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
            'sistrip',
            'tracking',
            'comment',
            'date',
            'problem_categories',
        ]

        widgets = {
            'int_luminosity': TextInput(attrs={'placeholder': "Unit: /pb "}),
        }

    # TODO write dedicated clean_tracking, clean_... instead one single clean
    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_sistrip_bad = cleaned_data.get('sistrip') == 'Bad'
        is_tracking_good = cleaned_data.get('tracking') == 'Good'

        if is_sistrip_bad and is_tracking_good:  # and comment_string=="":
            self.add_error(None, ValidationError(
                "Tracking can not be GOOD if SiStrip is BAD. Please correct."))

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
