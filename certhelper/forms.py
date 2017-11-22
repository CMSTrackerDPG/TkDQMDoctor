from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import RunInfo

class RunInfoForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = '__all__'

    def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_pixel_ok = cleaned_data.get('pixel')
        is_sistrip_ok = cleaned_data.get('sistrip')
        is_tracking_ok = cleaned_data.get('tracking')

        if not is_pixel_ok:
            self.add_error(None, ValidationError("pixel is false. THIS cant be because so and so"))

        return cleaned_data
