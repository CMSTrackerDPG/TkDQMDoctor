import django_filters
from django import forms
from django.utils import timezone

from certhelper.models import RunInfo


class RunInfoFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        'date',
        label='Date',
        lookup_expr='contains',
        widget=forms.SelectDateWidget(years=range(2018, timezone.now().year + 1)),
        initial=timezone.now
    )

    class Meta:
        model = RunInfo
        fields = ['date']
