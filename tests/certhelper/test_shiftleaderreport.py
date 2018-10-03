import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo
from certhelper.utilities.ShiftLeaderReport import (
    ShiftLeaderReport,
    NewShiftLeaderReport,
)
from certhelper.utilities.utilities import to_weekdayname, to_date
from tests.utils.utilities import create_runs

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
                "certhelper.RunInfo",
                type=mixer.blend(
                    "certhelper.Type", runtype=condition[0], reco=condition[1]
                ),
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

        assert (
            report.number_of_runs(
                "Collisions", "Express", bad_only=True, day="2018-05-14"
            )
            == 0
        )
        assert (
            report.number_of_runs(
                "Collisions", "Prompt", bad_only=True, day="2018-05-14"
            )
            == 1
        )
        assert (
            report.number_of_runs("Cosmics", "Express", bad_only=True, day="2018-05-14")
            == 1
        )
        assert (
            report.number_of_runs("Cosmics", "Prompt", bad_only=True, day="2018-05-14")
            == 1
        )

        assert (
            report.sum_int_lum("Collisions", "Express", bad_only=True, day="2018-05-14")
            == 0
        )
        assert (
            report.sum_int_lum("Collisions", "Prompt", bad_only=True, day="2018-05-14")
            == 1.23
        )
        assert (
            report.sum_int_lum("Cosmics", "Express", bad_only=True, day="2018-05-14")
            == 0
        )
        assert (
            report.sum_int_lum("Cosmics", "Prompt", bad_only=True, day="2018-05-14")
            == 0
        )

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


class TestNewShiftLeaderReport:
    def test_weekly_certification(self, runs_for_slr):
        runs = RunInfo.objects.all()
        report = NewShiftLeaderReport(runs)

        assert report.collisions().express().total_number() == 8
        assert report.collisions().prompt().total_number() == 3
        assert report.cosmics().express().total_number() == 7
        assert report.cosmics().prompt().total_number() == 1

        assert report.collisions().express().integrated_luminosity() == 161301.36
        assert report.prompt().collisions().integrated_luminosity() == 123133.55
        assert report.express().cosmics().integrated_luminosity() == 0.12
        assert report.cosmics().prompt().integrated_luminosity() == 0

        assert report.bad().collisions().express().total_number() == 0
        assert report.prompt().bad().collisions().total_number() == 3
        assert report.cosmics().bad().express().total_number() == 2
        assert report.bad().prompt().cosmics().total_number() == 1

        assert report.bad().collisions().express().integrated_luminosity() == 0
        assert report.bad().collisions().prompt().integrated_luminosity() == 123133.55
        assert report.bad().cosmics().express().integrated_luminosity() == 0
        assert report.bad().cosmics().prompt().integrated_luminosity() == 0

    def test_day_by_day(self, runs_for_slr):
        runs = RunInfo.objects.all()
        report = NewShiftLeaderReport(runs)
        runs = runs.order_by("date", "type__runtype", "type__reco")

        day_by_day = report.day_by_day()

        assert day_by_day[0].name() == "Monday"
        assert day_by_day[1].name() == "Tuesday"
        assert day_by_day[2].name() == "Thursday"
        assert day_by_day[3].name() == "Friday"
        assert day_by_day[4].name() == "Sunday"

        assert to_date("2018-05-14") == day_by_day[0].date()
        assert day_by_day[1].date() == to_date("2018-05-15")
        assert day_by_day[2].date() == to_date("2018-05-17")
        assert day_by_day[3].date() == to_date("2018-05-18")
        assert day_by_day[4].date() == to_date("2018-05-20")

        day = day_by_day[0]

        assert day.collisions().express().total_number() == 3
        assert day.collisions().prompt().total_number() == 1
        assert day.cosmics().express().total_number() == 3
        assert day.cosmics().prompt().total_number() == 1

        assert day.collisions().express().integrated_luminosity() == 5212
        assert day.prompt().collisions().integrated_luminosity() == 1.23
        assert day.express().cosmics().integrated_luminosity() == 0.12
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 1
        assert day.cosmics().bad().express().total_number() == 1
        assert day.bad().prompt().cosmics().total_number() == 1

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 1.23
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

        assert 5 == len(report.day_by_day())

        day = day_by_day[1]

        assert day.collisions().express().total_number() == 1
        assert day.collisions().prompt().total_number() == 0
        assert day.cosmics().express().total_number() == 0
        assert day.cosmics().prompt().total_number() == 0

        assert day.collisions().express().integrated_luminosity() == 423.24
        assert day.prompt().collisions().integrated_luminosity() == 0
        assert day.express().cosmics().integrated_luminosity() == 0
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 0
        assert day.cosmics().bad().express().total_number() == 0
        assert day.bad().prompt().cosmics().total_number() == 0

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 0
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

        day = day_by_day[2]

        assert day.collisions().express().total_number() == 0
        assert day.collisions().prompt().total_number() == 0
        assert day.cosmics().express().total_number() == 3
        assert day.cosmics().prompt().total_number() == 0

        assert day.collisions().express().integrated_luminosity() == 0
        assert day.prompt().collisions().integrated_luminosity() == 0
        assert day.express().cosmics().integrated_luminosity() == 0
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 0
        assert day.cosmics().bad().express().total_number() == 1
        assert day.bad().prompt().cosmics().total_number() == 0

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 0
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

        day = day_by_day[3]

        assert day.collisions().express().total_number() == 2
        assert day.collisions().prompt().total_number() == 0
        assert day.cosmics().express().total_number() == 0
        assert day.cosmics().prompt().total_number() == 0

        assert day.collisions().express().integrated_luminosity() == 154543 + 124.12
        assert day.prompt().collisions().integrated_luminosity() == 0
        assert day.express().cosmics().integrated_luminosity() == 0
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 0
        assert day.cosmics().bad().express().total_number() == 0
        assert day.bad().prompt().cosmics().total_number() == 0

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 0
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

        day = day_by_day[3]

        assert day.collisions().express().total_number() == 2
        assert day.collisions().prompt().total_number() == 0
        assert day.cosmics().express().total_number() == 0
        assert day.cosmics().prompt().total_number() == 0

        assert day.collisions().express().integrated_luminosity() == 154543 + 124.12
        assert day.prompt().collisions().integrated_luminosity() == 0
        assert day.express().cosmics().integrated_luminosity() == 0
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 0
        assert day.cosmics().bad().express().total_number() == 0
        assert day.bad().prompt().cosmics().total_number() == 0

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 0
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

        day = day_by_day[4]

        assert day.collisions().express().total_number() == 2
        assert day.collisions().prompt().total_number() == 2
        assert day.cosmics().express().total_number() == 1
        assert day.cosmics().prompt().total_number() == 0

        assert day.collisions().express().integrated_luminosity() == 999
        assert day.prompt().collisions().integrated_luminosity() == 123132.32
        assert day.express().cosmics().integrated_luminosity() == 0
        assert day.cosmics().prompt().integrated_luminosity() == 0

        assert day.bad().collisions().express().total_number() == 0
        assert day.prompt().bad().collisions().total_number() == 2
        assert day.cosmics().bad().express().total_number() == 0
        assert day.bad().prompt().cosmics().total_number() == 0

        assert day.bad().collisions().express().integrated_luminosity() == 0
        assert day.bad().collisions().prompt().integrated_luminosity() == 123132.32
        assert day.bad().cosmics().express().integrated_luminosity() == 0
        assert day.bad().cosmics().prompt().integrated_luminosity() == 0

    def test_list_of_run_numbers(self):
        create_runs(5, 1, "Collisions", "Express", good=True)
        create_runs(4, 6, "Collisions", "Express", good=False)
        create_runs(3, 10, "Collisions", "Prompt", good=True)
        create_runs(3, 15, "Collisions", "Prompt", good=False)
        create_runs(5, 21, "Cosmics", "Express", good=True)
        create_runs(4, 26, "Cosmics", "Express", good=False)
        create_runs(3, 30, "Cosmics", "Prompt", good=True)
        create_runs(3, 35, "Cosmics", "Prompt", good=False)

        runs = RunInfo.objects.all().order_by("run_number")
        report = NewShiftLeaderReport(runs)

        assert [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
        ] == report.collisions().express().run_numbers()
        assert [10, 11, 12, 15, 16, 17] == report.collisions().prompt().run_numbers()
        assert [
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
        ] == report.cosmics().express().run_numbers()
        assert [30, 31, 32, 35, 36, 37] == report.cosmics().prompt().run_numbers()

        assert [1, 2, 3, 4, 5] == report.collisions().express().good().run_numbers()
        assert [10, 11, 12] == report.collisions().prompt().good().run_numbers()
        assert [21, 22, 23, 24, 25] == report.cosmics().express().good().run_numbers()
        assert [30, 31, 32] == report.cosmics().prompt().good().run_numbers()

        assert [6, 7, 8, 9] == report.collisions().express().bad().run_numbers()
        assert [15, 16, 17] == report.collisions().prompt().bad().run_numbers()
        assert [26, 27, 28, 29] == report.cosmics().express().bad().run_numbers()
        assert [35, 36, 37] == report.cosmics().prompt().bad().run_numbers()

    def test_list_of_run_certified(self):
        create_runs(2, 1, "Collisions", "Express", good=True, date="2018-05-14")
        create_runs(2, 6, "Collisions", "Express", good=False, date="2018-05-14")
        create_runs(2, 10, "Collisions", "Prompt", good=True, date="2018-05-15")
        create_runs(2, 15, "Collisions", "Prompt", good=False, date="2018-05-15")
        create_runs(2, 21, "Cosmics", "Express", good=True, date="2018-05-14")
        create_runs(2, 26, "Cosmics", "Express", good=False, date="2018-05-16")
        create_runs(2, 30, "Cosmics", "Prompt", good=True, date="2018-05-14")
        create_runs(2, 35, "Cosmics", "Prompt", good=False, date="2018-05-14")

        runs = RunInfo.objects.all().order_by("run_number")
        report = NewShiftLeaderReport(runs)

        days = report.day_by_day()

        assert [1, 2, 6, 7] == days[0].express().collisions().run_numbers()
        assert [21, 22] == days[0].express().cosmics().run_numbers()
        assert [26, 27] == days[2].express().cosmics().run_numbers()
        assert [10, 11, 15, 16] == days[1].prompt().collisions().run_numbers()
        assert [30, 31, 35, 36] == days[0].prompt().cosmics().run_numbers()
