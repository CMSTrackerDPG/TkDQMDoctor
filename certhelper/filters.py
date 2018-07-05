import django_filters
from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.forms.widgets import SelectDateWidget
from django.utils import timezone

from certhelper.models import RunInfo, Type


class RunInfoFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        'date',
        label='Date',
        lookup_expr='contains',
        widget=forms.SelectDateWidget(
            years=range(2018, timezone.now().year + 1),
            attrs={'class': 'form-control'},
        ),
    )

    date_range = django_filters.DateFromToRangeFilter(
        'date',
        widget=django_filters.widgets.RangeWidget(attrs={
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control',
            'size': 9,
            'maxlength': 10,
        })
    )

    runs = django_filters.RangeFilter(
        'run_number',
        widget=django_filters.widgets.RangeWidget(attrs={
            'placeholder': 'run number',
            'class': 'form-control',
            'size': 7,
            'maxlength': 10,
        })
    )
    type = django_filters.ModelChoiceFilter(queryset=Type.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
        'style': 'width: 500px;',
    }))

    class Meta:
        model = RunInfo
        fields = ['type', 'date', 'problem_categories']


class ShiftLeaderRunInfoFilter(django_filters.FilterSet):
    # userid = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all())
    userid = django_filters.filters.ModelMultipleChoiceFilter(
        name='userid',
        to_field_name='pk',
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '15',
        })
    )

    type = django_filters.ModelChoiceFilter(queryset=Type.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
        'style': 'width: 600px;',
    }))

    class Meta:
        model = RunInfo
        fields = {
            'date': ['gte', 'lte', ],
            'run_number': ['gte', 'lte', ],
            'problem_categories': ['exact'],
        }
        filter_overrides = {
            models.DateField: {
                'filter_class': django_filters.DateTimeFilter,
                'extra': lambda f: {
                    'widget': SelectDateWidget
                },
            },
        }