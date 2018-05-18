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

from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm, TextInput, Textarea
from .models import *
from django.utils import timezone


class DateInput(forms.DateInput):
    input_type = 'date'


class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = ['reference_run', 'reco', 'runtype', 'bfield', 'beamtype', 'beamenergy', 'dataset', ]


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
            'category',
            'subcategory',
            'subsubcategory',
        ]

        widgets = {
            'int_luminosity': TextInput(attrs={'placeholder': "Unit: /pb "}),
            # 'date': DateInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """" Initialize the Subcategories empty, only the subcategories corresponding
        to the particular category should be shown, when selected"""
        self.fields['subcategory'].queryset = SubCategory.objects.none()
        self.fields['subsubcategory'].queryset = SubSubCategory.objects.none()

        if 'category' in self.data and self.data['category']:  # if category is set in RunInfo Form
            try:
                category_id = self.data.get('category')
                self.fields['subcategory'].queryset = SubCategory.objects.filter(parent_category=category_id)
                if 'subcategory' in self.data and self.data['subcategory']:
                    subcategory_id = self.data.get('subcategory')
                    self.fields['subsubcategory'].queryset = SubSubCategory.objects.filter(
                        parent_category=subcategory_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:  # if a RunInfo model instance already exists, (edit button pressed)
            if self.instance.category:  # if category is not empty
                self.fields['subcategory'].queryset = self.instance.category.subcategory_set
                if self.instance.subcategory:
                    self.fields['subsubcategory'].queryset = self.instance.subcategory.subsubcategory_set

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_pixel_good = cleaned_data.get('pixel') == 'Good'
        is_pixel_bad = cleaned_data.get('pixel') == 'Bad'
        is_sistrip_good = cleaned_data.get('sistrip') == 'Good'
        is_sistrip_bad = cleaned_data.get('sistrip') == 'Bad'
        is_tracking_good = cleaned_data.get('tracking') == 'Good'
        comment_string = cleaned_data.get('comment')
        # is_cosmic_run = (cleaned_data.get('Type')).get('runtype')=='Cosmics'

        # if not (is_sistrip_good and is_tracking_good ) :#and comment_string=="":
        #   self.add_error(None, ValidationError("Tracking can not be GOOD if SiStrip is BAD. Please correct."))

        # if not (is_sistrip_good and is_tracking_good ) :#and comment_string=="":
        #   self.add_error(None, ValidationError("Tracking can not be GOOD if SiStrip is BAD. Please correct."))

        if is_sistrip_bad and is_tracking_good:  # and comment_string=="":
            self.add_error(None, ValidationError("Tracking can not be GOOD if SiStrip is BAD. Please correct."))

        return cleaned_data


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ["reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]
        widgets = {
            'dataset': TextInput(
                attrs={'placeholder': "e.g. /Cosmics/Run2017F-PromptReco-v1/DQMIO", 'class': "form-control"}),
        }
