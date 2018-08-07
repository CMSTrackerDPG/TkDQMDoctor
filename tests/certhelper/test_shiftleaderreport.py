import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo
from certhelper.utilities.ShiftLeaderReport import ShiftLeaderReport
from certhelper.utilities.utilities import to_weekdayname

pytestmark = pytest.mark.django_db


class TestShiftLeaderReport:
    def test_shiftleaderreport(self):
        conditions = [
            ["Cosmics", "Express", 0.1234, 72, "2018-05-14", "Good"],
            ["Collisions", "Prompt", 1.234, 5432, "2018-05-14", "Bad"],  #######
            ["Cosmics", "Prompt", 0, 25, "2018-05-14", "Bad"],  ########
            ["Collisions", "Express", 423.24, 2, "2018-05-15", "Good"],
            ["Collisions", "Express", 0, 72, "2018-05-14", "Good"],
            ["Cosmics", "Express", 0, 12, "2018-05-17", "Good"],
            ["Cosmics", "Express", 0, 72, "2018-05-17", "Bad"],
            ["Cosmics", "Express", 0, 42, "2018-05-14", "Bad"],  #######
            ["Collisions", "Express", 124.123, 72, "2018-05-18", "Good"],
            ["Cosmics", "Express", 0, 1242, "2018-05-14", "Good"],
            ["Cosmics", "Express", 0, 72, "2018-05-20", "Good"],
            ["Collisions", "Express", 999, 142, "2018-05-20", "Good"],
            ["Collisions", "Prompt", 0, 72, "2018-05-20", "Bad"],  #######
            ["Collisions", "Prompt", 123132.32, 4522, "2018-05-20", "Bad"],  #######
            ["Collisions", "Express", 0, 72, "2018-05-20", "Good"],
            ["Collisions", "Express", -1, 71232, "2018-05-14", "Good"],
            ["Cosmics", "Express", 0, 712, "2018-05-17", "Good"],
            ["Collisions", "Express", 5213, 142, "2018-05-14", "Good"],
            ["Collisions", "Express", 154543, 72, "2018-05-18", "Good"],
        ]

        for condition in conditions:
            mixer.blend(
                'certhelper.RunInfo',
                type=mixer.blend('certhelper.Type', runtype=condition[0], reco=condition[1]),
                int_luminosity=condition[2],
                number_of_ls=condition[3],
                date=condition[4],
                pixel=condition[5],
                sistrip=condition[5],
                tracking=condition[5],
            )

        runs = RunInfo.objects.all()
        report = ShiftLeaderReport(runs)

        assert report.number_of_runs("Collisions", "Express") == 8
        assert report.number_of_runs("Collisions", "Prompt") == 3
        assert report.number_of_runs("Cosmics", "Express") == 7
        assert report.number_of_runs("Cosmics", "Prompt") == 1

        assert report.sum_int_lum("Collisions", "Express") == 161301.36
        assert report.sum_int_lum("Collisions", "Prompt") == 123133.55
        assert report.sum_int_lum("Cosmics", "Express") == 0.12
        assert report.sum_int_lum("Cosmics", "Prompt") == 0

        assert report.number_of_runs("Collisions", "Express", bad_only=True) == 0
        assert report.number_of_runs("Collisions", "Prompt", bad_only=True) == 3
        assert report.number_of_runs("Cosmics", "Express", bad_only=True) == 2
        assert report.number_of_runs("Cosmics", "Prompt", bad_only=True) == 1

        assert report.sum_int_lum("Collisions", "Express", bad_only=True) == 0
        assert report.sum_int_lum("Collisions", "Prompt", bad_only=True) == 123133.55
        assert report.sum_int_lum("Cosmics", "Express", bad_only=True) == 0
        assert report.sum_int_lum("Cosmics", "Prompt", bad_only=True) == 0

        assert report.number_of_runs("Collisions", "Express", day="2018-05-14") == 3
        assert report.number_of_runs("Collisions", "Prompt", day="2018-05-14") == 1
        assert report.number_of_runs("Cosmics", "Express", day="2018-05-14") == 3
        assert report.number_of_runs("Cosmics", "Prompt", day="2018-05-14") == 1

        assert report.sum_int_lum("Collisions", "Express", day="2018-05-14") == 5212
        assert report.sum_int_lum("Collisions", "Prompt", day="2018-05-14") == 1.23
        assert report.sum_int_lum("Cosmics", "Express", day="2018-05-14") == 0.12
        assert report.sum_int_lum("Cosmics", "Prompt", day="2018-05-14") == 0

        assert report.number_of_runs("Collisions", "Express", bad_only=True, day="2018-05-14") == 0
        assert report.number_of_runs("Collisions", "Prompt", bad_only=True, day="2018-05-14") == 1
        assert report.number_of_runs("Cosmics", "Express", bad_only=True, day="2018-05-14") == 1
        assert report.number_of_runs("Cosmics", "Prompt", bad_only=True, day="2018-05-14") == 1

        assert report.sum_int_lum("Collisions", "Express", bad_only=True, day="2018-05-14") == 0
        assert report.sum_int_lum("Collisions", "Prompt", bad_only=True, day="2018-05-14") == 1.23
        assert report.sum_int_lum("Cosmics", "Express", bad_only=True, day="2018-05-14") == 0
        assert report.sum_int_lum("Cosmics", "Prompt", bad_only=True, day="2018-05-14") == 0

        assert len(report.get_active_days_list()) == 5
        day_list = report.get_active_days_list()

        assert day_list[0] == "2018-05-14"
        assert day_list[1] == "2018-05-15"
        assert day_list[2] == "2018-05-17"
        assert day_list[3] == "2018-05-18"
        assert day_list[4] == "2018-05-20"

        assert to_weekdayname(day_list[0]) == "Monday"
        assert to_weekdayname(day_list[4]) == "Sunday"

        context = report.get_context()

        assert context["Bad"]["Collisions"]["Express"]["int_lum"] == 0
        assert context["Bad"]["Collisions"]["Prompt"]["int_lum"] == 123133.55
        assert context["day"][0]["name"] == "Monday"
        assert context["day"][0]["date"] == "2018-05-14"

        assert context["day"][3]["name"] == "Friday"
        assert context["day"][3]["date"] == "2018-05-18"

        length = len(context["day"])
        assert length == 5
        assert context["day"][length - 1]["name"] == "Sunday"
        assert context["day"][length - 1]["date"] == "2018-05-20"

        assert context["day"][1]["date"] == "2018-05-15"
        assert context["day"][1]["Collisions"]["Express"]["int_lum"] == 423.24
        assert context["day"][1]["Collisions"]["Express"]["number_of_runs"] == 1
        assert context["Collisions"]["Express"]["number_of_runs"] == 8

    def test_changed_flags(self, some_certified_runs):
        runs = RunInfo.objects.all()

        for run in runs:
            run.date = "2018-02-28"
            run.save()

        report = ShiftLeaderReport(runs)

        assert "4, 5, 14" == report.get_context()["day"][0]["runs_with_changed_flags"]
        assert 3 == report.get_context()["day"][0]["number_of_changed_flags"]