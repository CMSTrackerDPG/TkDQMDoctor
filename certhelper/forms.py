from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import *

class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = '__all__'

class RunInfoForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = '__all__'

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_pixel_good = cleaned_data.get('pixel')=='Good'

        if not is_pixel_good:
            self.add_error(None, ValidationError("pixel is false. THIS cant be because so and so"))

        return cleaned_data


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = '__all__'
