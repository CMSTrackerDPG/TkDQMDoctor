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

        d = RunInfo.objects.all().compare_list_if_certified(
            [333, 1234, 6655, "800", 4321, 7777, 9876, "abde", 8765, 6543, 888, 444])

        assert set([1234, 6655, 6543, 444, "800"]) == set(d["good"])
        assert set([9876, 8765]) == set(d["bad"])
        assert set([7777, 888, "abde"]) == set(d["missing"])
        assert set([4321, 333]) == set(d["different_flags"])

    def test_changed_flags(self, some_certified_runs):
        """
        run     type       reco    good
        1       Collisions Express True
        1       Collisions Prompt  True
        2       Collisions Express True
        3       Collisions Express True
        3       Collisions Prompt  True
        4       Collisions Express True
        4       Collisions Prompt  False
        5       Collisions Express False
        5       Collisions Prompt  True
        6       Collisions Express False
        6       Collisions Prompt  False
        7       Collisions Express False
        10      Cosmics    Express True
        11      Cosmics    Express True
        11      Cosmics    Prompt  True
        12      Cosmics    Express True
        13      Cosmics    Express True
        14      Cosmics    Express True
        14      Cosmics    Prompt  False
        """
        assert 3 == len(RunInfo.objects.all().changed_flags())
        assert {5, 4, 14} == set(RunInfo.objects.all().changed_flags())

    def test_no_changed_flags(self):
        assert 0 == len(RunInfo.objects.all().changed_flags())

    def test_new_flags_changed(self, some_certified_runs):
        runs = RunInfo.objects.all().order_by("type__runtype", "type__reco",
                                              "run_number")

        runs = runs.annotate_status().filter_flag_changed().order_by("run_number")

        # print(runs)
        for run in runs:
            print("{} {} {}".format(run.run_number, run.type.reco, run.status))

        assert True
