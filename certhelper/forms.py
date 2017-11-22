from django.forms import ModelForm
from .models import RunInfo

class RunInfoForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = '__all__'
