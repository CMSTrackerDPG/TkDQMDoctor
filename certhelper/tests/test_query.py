import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo

pytestmark = pytest.mark.django_db


class TestRunInfoQuerySet:
    def test_compare_list_if_certified(self):
        t1 = mixer.blend("certhelper.Type")
        t2 = mixer.blend("certhelper.Type")
        mixer.blend("certhelper.RunInfo", run_number=1234, type=t1, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=8765, pixel="Good", sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=4321, type=t1, pixel="Good", sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=6543, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=6655, type=t1, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=9876, pixel="Good", sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=444, type=t1, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=444, type=t2, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=333, type=t1, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=333, type=t2, pixel="Good", sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=999)
        mixer.blend("certhelper.RunInfo", run_number=800, type=t2, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=4321, type=t2, pixel="Good", sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=1234, type=t2, pixel="Good", sistrip="Good", tracking="Good")

        d = RunInfo.objects.all().compare_list_if_certified([333, 1234, 6655, "800", 4321, 7777, 9876, "abde", 8765, 6543, 888, 444])

        assert set([1234, 6655, 6543, 444, "800"]) == set(d["good"])
        assert set([9876, 8765]) == set(d["bad"])
        assert set([7777, 888, "abde"]) == set(d["missing"])
        assert set([4321, 333]) == set(d["conflicting"])
