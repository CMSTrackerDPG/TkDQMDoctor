import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer

from certhelper.models import ReferenceRun
from certhelper.models import RunInfo
from certhelper.models import Type

pytestmark = pytest.mark.django_db


class TestRuninfo:
    def test_init(self):
        run = mixer.blend('certhelper.RunInfo', run_number=42, number_of_ls=13, int_luminosity=7138641)
        assert run.__class__.__name__ == "RunInfo"
        assert run.pk == 1
        assert run.run_number == 42
        assert run.number_of_ls == 13
        assert run.int_luminosity == 7138641
        assert run.pixel in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.sistrip in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.pixel in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.trackermap in ("Exists", "Missing")
        assert run.type.reco in ("Express", "Prompt", "reReco")
        assert run.type.runtype in ("Cosmics", "Collisions")

    def test_is_good(self):
        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.is_bad() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          sistrip="Bad")
        assert run.is_good() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Bad")
        assert run.is_good() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          tracking="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Good", sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.is_bad() is False

        assert len(RunInfo.objects.all()) == 7

    def test_delete(self):
        run = mixer.blend('certhelper.RunInfo', run_number=123456)

        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert run.run_number == 123456
        run.delete()
        assert RunInfo.objects.filter(run_number=123456).exists() is False
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.get(run_number=123456).pk == run.pk
        run.restore()
        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True
        run.hard_delete()
        assert RunInfo.objects.filter(run_number=123456).exists() is False
        assert RunInfo.all_objects.filter(run_number=123456).exists() is False
        assert run.run_number == 123456
        run.save()
        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True

    def test_to_string(self):
        run = mixer.blend('certhelper.RunInfo',
                          run_number=123456,
                          type__runtype="Cosmics",
                          type__reco="Express",
                          reference_run__reference_run=654321,
                          reference_run__reco="Prompt",
                          reference_run__runtype="Collisions",
                          )
        assert run.run_number == 123456
        assert run.type.runtype == "Cosmics"
        assert run.type.reco == "Express"
        assert run.reference_run.reference_run == 654321
        assert run.reference_run.reco == "Prompt"
        assert run.reference_run.runtype == "Collisions"

        assert str(run) == "123456, Cosmics Express (ref: 654321, Collisions Prompt)"
        assert "654321 Prompt Collisions" in str(run.reference_run)
        assert "Express Cosmics" in str(run.type)

    def test_validate_unique(self):
        with pytest.raises(ValidationError):
            t = mixer.blend('certhelper.Type')
            ref = mixer.blend('certhelper.ReferenceRun')

            r1 = mixer.blend('certhelper.RunInfo',
                             run_number=123456,
                             type=t,
                             reference_run=ref
                             )

            r2 = mixer.blend('certhelper.RunInfo',
                             run_number=123456,
                             type=t,
                             reference_run=ref
                             )


class TestCategory:
    def test_category_str(self):
        assert str(mixer.blend("certhelper.Category", name="cat1")) == "cat1"
        assert str(mixer.blend("certhelper.SubCategory", name="subcat1")) == "subcat1"
        assert str(mixer.blend("certhelper.SubSubCategory", name="subsubcat1")) == "subsubcat1"