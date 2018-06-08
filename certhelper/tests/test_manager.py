import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo
from certhelper.utilities.utilities import get_from_summary

pytestmark = pytest.mark.django_db


class TestRunInfoManager:
    def test_good(self):
        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Bad")
        assert run.is_good() is False
        assert run.pk == 1

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Bad")
        assert run.is_good() is False
        assert run.pk == 2

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.pk == 3

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          sistrip="Bad")
        assert run.is_good() is False
        assert run.pk == 4

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Bad")
        assert run.is_good() is False
        assert run.pk == 5

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          tracking="Bad")
        assert run.is_good() is False
        assert run.pk == 6

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Good", sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.pk == 7

        assert len(RunInfo.objects.all()) == 7
        good_runs = RunInfo.objects.all().good().order_by("pk")
        assert len(good_runs) == 2
        assert good_runs[0].pk == 3
        assert good_runs[0].type.runtype == "Cosmics"
        assert good_runs[0].sistrip == "Good"
        assert good_runs[0].tracking == "Good"
        assert good_runs[1].pk == 7
        assert good_runs[1].type.runtype == "Collisions"
        assert good_runs[1].sistrip == "Good"
        assert good_runs[1].pixel == "Good"
        assert good_runs[1].tracking == "Good"

        bad_runs = RunInfo.objects.all().bad().order_by("pk")

        assert bad_runs[0].pk == 1
        assert bad_runs[1].pk == 2
        assert bad_runs[2].pk == 4
        assert bad_runs[3].pk == 5
        assert bad_runs[4].pk == 6

        assert len(bad_runs) == 5

        assert len(RunInfo.objects.bad()) == 5
        assert len(RunInfo.objects.good()) == 2

        assert len(RunInfo.objects.filter(id__gt=3).good()) == 1
        assert len(RunInfo.objects.filter(id__gt=2).good()) == 2

    def test_summary(self):
        conditions = [
            ["Cosmics", "Express", 0.1234, 72],
            ["Collisions", "Prompt", 1.234, 5432],
            ["Cosmics", "Prompt", 0, 25],
            ["Collisions", "Express", 423.24, 2],
            ["Collisions", "Express", 0, 72],
            ["Cosmics", "Express", 0, 12],
            ["Cosmics", "Express", 0, 72],
            ["Cosmics", "Express", 0, 42],
            ["Collisions", "Express", 124.123, 72],
            ["Cosmics", "Express", 0, 1242],
            ["Cosmics", "Express", 0, 72],
            ["Collisions", "Express", 999, 142],
            ["Collisions", "Prompt", 0, 72],
            ["Collisions", "Prompt", 123132.32, 4522],
            ["Collisions", "Express", 0, 72],
            ["Collisions", "Express", -1, 71232],
            ["Cosmics", "Express", 0, 712],
            ["Collisions", "Express", 5213, 142],
            ["Collisions", "Express", 154543, 72],
        ]

        runs = []

        for condition in conditions:
            runs.append(mixer.blend(
                'certhelper.RunInfo',
                type=mixer.blend('certhelper.Type', runtype=condition[0], reco=condition[1]),
                int_luminosity=condition[2],
                number_of_ls=condition[3]
            )
            )

        summary = RunInfo.objects.all().summary()

        a = [x for x in summary if x['type__runtype'] == 'Collisions' and x['type__reco'] == 'Express']

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 8
        assert a["int_luminosity"] == 161301.36
        assert a["number_of_ls"] == 71806

        a = get_from_summary(summary, "Cosmics", "Express")

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 7
        assert a["int_luminosity"] == 0.12
        assert a["number_of_ls"] == 2224

        a = [x for x in summary if x['type__runtype'] == 'Collisions' and x['type__reco'] == 'Prompt']

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 3
        assert a["int_luminosity"] == 123133.55
        assert a["number_of_ls"] == 10026

        a = [x for x in summary if x['type__runtype'] == 'Cosmics' and x['type__reco'] == 'Prompt']

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 1
        assert a["int_luminosity"] == 0
        assert a["number_of_ls"] == 25

        a = get_from_summary(summary, "Cosmics", "Prompt")
        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 1
        assert a["int_luminosity"] == 0
        assert a["number_of_ls"] == 25

    def test_summary_per_day(self):
        conditions = [
            ["Cosmics", "Express", 0.1234, 72, "2018-05-14"],
            ["Collisions", "Prompt", 1.234, 5432, "2018-05-14"],
            ["Cosmics", "Prompt", 0, 25, "2018-05-14"],
            ["Collisions", "Express", 423.24, 2, "2018-05-15"],
            ["Collisions", "Express", 0, 72, "2018-05-14"],
            ["Cosmics", "Express", 0, 12, "2018-05-17"],
            ["Cosmics", "Express", 0, 72, "2018-05-17"],
            ["Cosmics", "Express", 0, 42, "2018-05-14"],
            ["Collisions", "Express", 124.123, 72, "2018-05-18"],
            ["Cosmics", "Express", 0, 1242, "2018-05-14"],
            ["Cosmics", "Express", 0, 72, "2018-05-20"],
            ["Collisions", "Express", 999, 142, "2018-05-20"],
            ["Collisions", "Prompt", 0, 72, "2018-05-20"],
            ["Collisions", "Prompt", 123132.32, 4522, "2018-05-20"],
            ["Collisions", "Express", 0, 72, "2018-05-20"],
            ["Collisions", "Express", -1, 71232, "2018-05-14"],
            ["Cosmics", "Express", 0, 712, "2018-05-17"],
            ["Collisions", "Express", 5213, 142, "2018-05-14"],
            ["Collisions", "Express", 154543, 72, "2018-05-18"],
        ]

        runs = []

        for condition in conditions:
            runs.append(mixer.blend(
                'certhelper.RunInfo',
                type=mixer.blend('certhelper.Type', runtype=condition[0], reco=condition[1]),
                int_luminosity=condition[2],
                number_of_ls=condition[3],
                date=condition[4]
            )
            )

        summary = RunInfo.objects.all().summary_per_day()

        assert len(summary) == 10

        item = get_from_summary(summary, "Collisions", "Prompt", "2018-05-14")

        assert len(item) == 1

        assert len(get_from_summary(summary, date="2018-05-14")) == 4
        assert len(get_from_summary(summary, runtype="Collisions", date="2018-05-14")) == 2
        assert len(get_from_summary(summary, reco="Express", date="2018-05-14")) == 2
        assert len(get_from_summary(summary, "Collisions",  "Express", "2018-05-14")) == 1
        assert len(get_from_summary(summary, date="2018-05-15")) == 1
        assert len(get_from_summary(summary, date="2018-05-16")) == 0
        assert len(get_from_summary(summary, date="2018-05-17")) == 1
        assert len(get_from_summary(summary, date="2018-05-18")) == 1
        assert len(get_from_summary(summary, date="2018-05-19")) == 0
        assert len(get_from_summary(summary, date="2018-05-20")) == 3

        assert get_from_summary(summary, date="2018-05-18")[0]["int_luminosity"] == 154667.12
        assert get_from_summary(summary, date="2018-05-18")[0]["number_of_ls"] == 144
        assert get_from_summary(summary, date="2018-05-14")[2]["int_luminosity"] == 0.12
