from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea
from .models import *

class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = '__all__'

class RunInfoForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = '__all__'
        widgets = {
            'int_luminosity': TextInput(attrs={ 'placeholder': "Unit: pb⁻¹ "})
        }

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_pixel_good = cleaned_data.get('pixel')=='Good'
        is_sistrip_good = cleaned_data.get('sistrip')=='Good'
        is_tracking_good = cleaned_data.get('tracking')=='Good'
        comment_string = cleaned_data.get('comment')

        if not (is_pixel_good and is_sistrip_good and is_tracking_good) and comment_string=="":
            self.add_error(None, ValidationError("Pixel/SiStrip/Tracking is set to Bad. You need to add a comment."))

        return cleaned_data


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ["reco", "runtype", "bfield", "beamtype", "dataset"]
        widgets = {
            'dataset': TextInput(attrs={ 'placeholder': "e.g. /Cosmics/Run2017F-PromptReco-v1/DQMIO", 'class': "form-control"}),
        }