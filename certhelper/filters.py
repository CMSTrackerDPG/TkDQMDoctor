import django_filters
from django import forms
from django.utils import timezone

from certhelper.models import RunInfo, SubCategory, SubSubCategory, Type


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
        fields = ['type', 'date', 'category', 'subcategory', 'subsubcategory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['subcategory'].queryset = SubCategory.objects.none()
        self.form.fields['subsubcategory'].queryset = SubSubCategory.objects.none()

        if 'category' in self.data and self.data['category']:  # if category is set in RunInfo Form
            try:
                category_id = self.data.get('category')
                self.form.fields['subcategory'].queryset = SubCategory.objects.filter(parent_category=category_id)
                if 'subcategory' in self.data and self.data['subcategory']:
                    subcategory_id = self.data.get('subcategory')
                    self.form.fields['subsubcategory'].queryset = SubSubCategory.objects.filter(parent_category=subcategory_id)
            except (ValueError, TypeError):
                pass
