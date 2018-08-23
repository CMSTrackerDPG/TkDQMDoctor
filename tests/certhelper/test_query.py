import pytest
from django.db.models import Count
from mixer.backend.django import mixer

from certhelper.models import RunInfo, ReferenceRun
from certhelper.utilities.utilities import to_date, to_weekdayname, uniquely_sorted
from tests.utils.utilities import create_runs

pytestmark = pytest.mark.django_db


class TestRunInfoQuerySet:
    def test_compare_list_if_certified(self):
        t1 = mixer.blend("certhelper.Type", runtype="Cosmics")
        t2 = mixer.blend("certhelper.Type", runtype="Collisions")
        mixer.blend("certhelper.RunInfo", run_number=1234, type=t1, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=8765, pixel="Good", sistrip="Good",
                    tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=4321, type=t1, pixel="Good",
                    sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=6543, pixel="Good", sistrip="Good",
                    tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=6655, type=t1, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=9876, pixel="Good", sistrip="Good",
                    tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=444, type=t1, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=444, type=t2, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=333, type=t1, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=333, type=t2, pixel="Good",
                    sistrip="Good", tracking="Bad")
        mixer.blend("certhelper.RunInfo", run_number=999)
        mixer.blend("certhelper.RunInfo", run_number=800, type=t2, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=4321, type=t2, pixel="Good",
                    sistrip="Good", tracking="Good")
        mixer.blend("certhelper.RunInfo", run_number=1234, type=t2, pixel="Good",
                    sistrip="Good", tracking="Good")

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

    def test_filter_flag_changed(self, some_certified_runs):
        runs = RunInfo.objects.all()
        runs_flag_changed = runs.filter_flag_changed()
        run_numbers = uniquely_sorted(runs_flag_changed.run_numbers())
        assert [4, 5, 14] == run_numbers
        assert True

    def test_collisions(self, some_certified_runs):
        assert 0 != len(RunInfo.objects.all())
        runs = RunInfo.objects.all().collisions()
        assert 0 != len(runs)

        for run in runs:
            assert "Collisions" == run.type.runtype

    def test_collisions_prompt(self):
        create_runs(5, 1, "Collisions", "Express")
        create_runs(3, 5, "Collisions", "Prompt")
        create_runs(5, 20, "Cosmics", "Express")
        create_runs(4, 26, "Cosmics", "Express")

        runs = RunInfo.objects.all().collisions()
        assert 8 == len(runs)

        for run in runs:
            assert "Collisions" == run.type.runtype

        runs = RunInfo.objects.all().collisions().prompt()
        assert 3 == len(runs)

        runs = RunInfo.objects.all().collisions().express()
        assert 5 == len(runs)

    def test_collisions_prompt_bad(self):
        create_runs(5, 1, "Collisions", "Express", good=True)
        create_runs(4, 6, "Collisions", "Express", good=False)
        create_runs(3, 10, "Collisions", "Prompt", good=True)
        create_runs(3, 15, "Collisions", "Prompt", good=False)
        create_runs(5, 21, "Cosmics", "Express", good=True)
        create_runs(4, 26, "Cosmics", "Express", good=False)
        create_runs(3, 30, "Cosmics", "Prompt", good=True)
        create_runs(3, 35, "Cosmics", "Prompt", good=False)

        runs = RunInfo.objects.all().collisions().prompt()
        assert 6 == len(runs)

    def test_cosmics(self, some_certified_runs):
        runs = RunInfo.objects.all().cosmics()
        assert 0 != len(runs)

        for run in runs:
            assert "Cosmics" == run.type.runtype

    def test_express(self, some_certified_runs):
        runs = RunInfo.objects.all().express()
        assert 0 != len(runs)

        for run in runs:
            assert "Express" == run.type.reco

    def test_prompt(self, some_certified_runs):
        runs = RunInfo.objects.all().prompt()
        assert 0 != len(runs)

        for run in runs:
            assert "Prompt" == run.type.reco

    def test_rereco(self, some_certified_runs):
        mixer.blend("certhelper.RunInfo", type__reco="ReReco")
        mixer.blend("certhelper.RunInfo", type__reco="ReReco")
        runs = RunInfo.objects.all().rereco()
        assert 0 != len(runs)

        for run in runs:
            assert "ReReco" == run.type.reco

    def test_run_numbers(self):
        mixer.blend("certhelper.RunInfo", run_number=123456)
        mixer.blend("certhelper.RunInfo", run_number=234567)
        mixer.blend("certhelper.RunInfo", run_number=345678)

        assert [123456, 234567, 345678] == RunInfo.objects.all().run_numbers()

    def test_int_luminosity(self):
        mixer.blend("certhelper.RunInfo", int_luminosity="13")
        mixer.blend("certhelper.RunInfo", int_luminosity="12.2")
        mixer.blend("certhelper.RunInfo", int_luminosity="0")
        mixer.blend("certhelper.RunInfo", int_luminosity="9")
        assert 34.2 == RunInfo.objects.all().integrated_luminosity()

    def test_total_number(self, some_certified_runs):
        assert 19 == RunInfo.objects.all().total_number()
        assert len(RunInfo.objects.all()) == RunInfo.objects.all().total_number()

    def test_slr(self, runs_for_slr):
        runs = RunInfo.objects.all()

        collisions_express = runs.collisions().express()
        collisions_prompt = runs.collisions().prompt()
        cosmics_express = runs.cosmics().express()
        cosmics_prompt = runs.cosmics().prompt()

        assert collisions_express.total_number() == 8
        assert collisions_prompt.total_number() == 3
        assert cosmics_express.total_number() == 7
        assert cosmics_prompt.total_number() == 1

        assert collisions_express.integrated_luminosity() == 161301.36
        assert collisions_prompt.integrated_luminosity() == 123133.55
        assert cosmics_express.integrated_luminosity() == 0.12
        assert cosmics_prompt.integrated_luminosity() == 0

        assert collisions_express.bad().total_number() == 0
        assert collisions_prompt.bad().total_number() == 3
        assert cosmics_express.bad().total_number() == 2
        assert cosmics_prompt.bad().total_number() == 1

        assert collisions_express.bad().integrated_luminosity() == 0
        assert collisions_prompt.bad().integrated_luminosity() == 123133.55
        assert cosmics_express.bad().integrated_luminosity() == 0
        assert cosmics_prompt.bad().integrated_luminosity() == 0

    def test_days(self, runs_for_slr):
        days = RunInfo.objects.all().days()
        assert 5 == len(days)
        assert '2018-05-14' == days[0]
        assert '2018-05-15' == days[1]
        assert '2018-05-17' == days[2]
        assert '2018-05-18' == days[3]
        assert '2018-05-20' == days[4]

    def test_slr_per_day(self, runs_for_slr):
        runs = RunInfo.objects.all()
        days = runs.days()

        runs = runs.filter(date=days[0])

        collisions_express = runs.collisions().express()
        collisions_prompt = runs.collisions().prompt()
        cosmics_express = runs.cosmics().express()
        cosmics_prompt = runs.cosmics().prompt()

        assert collisions_express.total_number() == 3
        assert collisions_prompt.total_number() == 1
        assert cosmics_express.total_number() == 3
        assert cosmics_prompt.total_number() == 1

        assert collisions_express.integrated_luminosity() == 5212
        assert collisions_prompt.integrated_luminosity() == 1.23
        assert cosmics_express.integrated_luminosity() == 0.12
        assert cosmics_prompt.integrated_luminosity() == 0

        assert collisions_express.bad().total_number() == 0
        assert collisions_prompt.bad().total_number() == 1
        assert cosmics_express.bad().total_number() == 1
        assert cosmics_prompt.bad().total_number() == 1

        assert collisions_express.bad().integrated_luminosity() == 0
        assert collisions_prompt.bad().integrated_luminosity() == 1.23
        assert cosmics_express.bad().integrated_luminosity() == 0
        assert cosmics_prompt.bad().integrated_luminosity() == 0

        assert to_weekdayname(days[0]) == "Monday"
        assert to_weekdayname(days[3]) == "Friday"
        assert to_weekdayname(days[4]) == "Sunday"

    def test_reference_run_ids(self, runs_with_three_refs):
        refs = RunInfo.objects.all().reference_run_numbers()
        assert 3 == len(refs)
        assert 1 == refs[0]
        assert 2 == refs[1]
        assert 3 == refs[2]

    def test_reference_runs(self, runs_with_three_refs):
        refs = RunInfo.objects.all().reference_runs()
        assert 3 == len(refs)
        assert ReferenceRun.objects.get(reference_run=1) == refs[0]
        assert ReferenceRun.objects.get(reference_run=2) == refs[1]
        assert ReferenceRun.objects.get(reference_run=3) == refs[2]

    def test_per_day(self, runs_for_slr):
        runs = RunInfo.objects.all().per_day()
        assert 5 == len(runs)

        for run in runs[0]:
            assert to_date('2018-05-14') == run.date
            assert "Monday" == to_weekdayname(run.date)

        for run in runs[1]:
            assert to_date('2018-05-15') == run.date
            assert "Tuesday" == to_weekdayname(run.date)

        for run in runs[2]:
            assert to_date('2018-05-17') == run.date
            assert "Thursday" == to_weekdayname(run.date)

        for run in runs[3]:
            assert to_date('2018-05-18') == run.date
            assert "Friday" == to_weekdayname(run.date)

        for run in runs[4]:
            assert to_date('2018-05-20') == run.date
            assert "Sunday" == to_weekdayname(run.date)
