import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo

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
