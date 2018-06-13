import datetime
import pytest
from django.contrib.auth.models import User
from mixer.backend.django import mixer

from certhelper import forms

pytestmark = pytest.mark.django_db


class TestRunInfoForm:
    def test_runinfoform(self):
        form = forms.RunInfoForm(data={})
        assert form.is_valid() is False
        user = mixer.blend(User)

        type = mixer.blend("certhelper.Type")
        reference_run = mixer.blend("certhelper.ReferenceRun")

        data = {
            'type': type.pk,
            'reference_run': reference_run.pk,
            'run_number': 123456,
            'trackermap': "Exists",
            'number_of_ls': 42,
            'int_luminosity': 12.2,
            'pixel': "Good",
            'sistrip': "Good",
            'tracking': "Good",
            'date': datetime.datetime.now().date(),
        }

        form = forms.RunInfoForm(data=data)
        form.instance.userid = user

        assert form.errors == {}
        assert form.is_valid() is True
        form.instance.userid = user
        form.save()

        form = forms.RunInfoForm(data=data)
        assert "already certified" in form.errors.get("__all__")[0]
        assert form.is_valid() is False, "No Duplicate certifications allowed"

        newdata = data.copy()
        newdata["run_number"] = 234567

        form = forms.RunInfoForm(data=newdata)
        assert form.errors == {}
        assert form.is_valid() is True, "Different (run_number, type, ref) tuples are allowed"

        newdata["sistrip"] = "Bad"
        form = forms.RunInfoForm(data=newdata)
        assert "Tracking can not be GOOD if SiStrip is BAD. Please correct." in form.errors.get("__all__")[0]
        assert form.is_valid() is False

    def test_categories(self):
        type = mixer.blend("certhelper.Type")
        reference_run = mixer.blend("certhelper.ReferenceRun")

        data = {
            'type': type.pk,
            'reference_run': reference_run.pk,
            'run_number': 123456,
            'trackermap': "Exists",
            'number_of_ls': 42,
            'int_luminosity': 12.2,
            'pixel': "Good",
            'sistrip': "Good",
            'tracking': "Good",
            'date': datetime.datetime.now().date(),
        }

        form = forms.RunInfoForm(data=data)

        newdata = data

        assert len(form.fields['category'].queryset) == 0
        subsubcat = mixer.blend("certhelper.SubSubCategory",
                                parent_category=mixer.blend("certhelper.SubCategory",
                                                            parent_category=mixer.blend("certhelper.Category")))

        form = forms.RunInfoForm(data=newdata)
        assert len(form.fields['category'].queryset) == 1
        assert len(form.fields['subcategory'].queryset) == 0
        assert len(form.fields['subsubcategory'].queryset) == 0
        mixer.blend("certhelper.Category")
        form = forms.RunInfoForm(data=newdata)
        assert len(form.fields['category'].queryset) == 2
        assert len(form.fields['subcategory'].queryset) == 0
        assert len(form.fields['subsubcategory'].queryset) == 0

        newdata["sistrip"] = "Good"
        newdata["category"] = subsubcat.parent_category.parent_category.id
        form = forms.RunInfoForm(data=newdata)

        assert len(form.fields['category'].queryset) == 2
        assert len(form.fields['subcategory'].queryset) == 1
        assert len(form.fields['subsubcategory'].queryset) == 0
        assert form.is_valid() is True

        newdata["subcategory"] = subsubcat.parent_category.id
        newdata["subsubcategory"] = subsubcat.id
        form = forms.RunInfoForm(data=newdata)

        assert len(form.fields['category'].queryset) == 2
        assert len(form.fields['subcategory'].queryset) == 1
        assert len(form.fields['subsubcategory'].queryset) == 1
        assert form.is_valid() is True
        form.instance.userid = mixer.blend(User)
        form.save()
