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
from django.forms import ModelForm, TextInput, Textarea
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = '__all__'

class RunInfoForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = '__all__'
        widgets = {
            'int_luminosity': TextInput(attrs={ 'placeholder': "Unit: pb⁻¹ "}),
            'date': DateInput()
        }

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_pixel_good = cleaned_data.get('pixel')=='Good'
        is_sistrip_good = cleaned_data.get('sistrip')=='Good'
        is_tracking_good = cleaned_data.get('tracking')=='Good'
        comment_string = cleaned_data.get('comment')

        if not (is_pixel_good and is_sistrip_good and is_tracking_good) :#and comment_string=="":
            self.add_error(None, ValidationError("Pixel, SiStrip & Tracking are not logically consistent, you dummy.."))

        return cleaned_data


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ["reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]
        widgets = {
            'dataset': TextInput(attrs={ 'placeholder': "e.g. /Cosmics/Run2017F-PromptReco-v1/DQMIO", 'class': "form-control"}),
        }
