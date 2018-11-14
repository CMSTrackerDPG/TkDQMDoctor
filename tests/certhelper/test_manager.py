from decimal import Decimal

import pytest
from mixer.backend.django import mixer

from certhelper.models import RunInfo
from certhelper.utilities.utilities import get_from_summary

pytestmark = pytest.mark.django_db


class TestRunInfoManager:
    def test_good(self):
        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Cosmics"),
            sistrip="Bad",
        )
        assert run.is_good is False

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Cosmics"),
            sistrip="Good",
            tracking="Bad",
        )
        assert run.is_good is False

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Cosmics"),
            sistrip="Good",
            tracking="Good",
        )
        assert run.is_good is True

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Collisions"),
            sistrip="Bad",
        )
        assert run.is_good is False

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Collisions"),
            pixel="Bad",
        )
        assert run.is_good is False

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Collisions"),
            tracking="Bad",
        )
        assert run.is_good is False

        run = mixer.blend(
            "certhelper.RunInfo",
            type=mixer.blend("certhelper.Type", runtype="Collisions"),
            pixel="Good",
            sistrip="Good",
            tracking="Good",
        )
        assert run.is_good is True

        assert len(RunInfo.objects.all()) == 7
        good_runs = RunInfo.objects.all().good().order_by("pk")
        assert len(good_runs) == 2
        assert good_runs[0].type.runtype == "Cosmics"
        assert good_runs[0].sistrip == "Good"
        assert good_runs[0].tracking == "Good"
        assert good_runs[1].type.runtype == "Collisions"
        assert good_runs[1].sistrip == "Good"
        assert good_runs[1].pixel == "Good"
        assert good_runs[1].tracking == "Good"

        bad_runs = RunInfo.objects.all().bad().order_by("pk")

        assert len(bad_runs) == 5

        assert len(RunInfo.objects.bad()) == 5
        assert len(RunInfo.objects.good()) == 2

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
            runs.append(
                mixer.blend(
                    "certhelper.RunInfo",
                    type=mixer.blend(
                        "certhelper.Type", runtype=condition[0], reco=condition[1]
                    ),
                    int_luminosity=condition[2],
                    number_of_ls=condition[3],
                )
            )

        summary = RunInfo.objects.all().summary()

        a = [
            x
            for x in summary
            if x["type__runtype"] == "Collisions" and x["type__reco"] == "Express"
        ]

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 8
        assert 161301.363 == a["int_luminosity"]
        assert a["number_of_ls"] == 71806

        a = get_from_summary(summary, "Cosmics", "Express")

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 7
        assert a["int_luminosity"] == 0.1234
        assert a["number_of_ls"] == 2224

        a = [
            x
            for x in summary
            if x["type__runtype"] == "Collisions" and x["type__reco"] == "Prompt"
        ]

        assert len(a) == 1
        a = a[0]
        assert a["runs_certified"] == 3
        assert a["int_luminosity"] == 123133.554
        assert a["number_of_ls"] == 10026

        a = [
            x
            for x in summary
            if x["type__runtype"] == "Cosmics" and x["type__reco"] == "Prompt"
        ]

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
            runs.append(
                mixer.blend(
                    "certhelper.RunInfo",
                    type=mixer.blend(
                        "certhelper.Type", runtype=condition[0], reco=condition[1]
                    ),
                    int_luminosity=condition[2],
                    number_of_ls=condition[3],
                    date=condition[4],
                )
            )

        summary = RunInfo.objects.all().summary_per_day()

        assert len(summary) == 10

        item = get_from_summary(summary, "Collisions", "Prompt", "2018-05-14")

        assert len(item) == 1

        assert len(get_from_summary(summary, date="2018-05-14")) == 4
        assert (
            len(get_from_summary(summary, runtype="Collisions", date="2018-05-14")) == 2
        )
        assert len(get_from_summary(summary, reco="Express", date="2018-05-14")) == 2
        assert (
            len(get_from_summary(summary, "Collisions", "Express", "2018-05-14")) == 1
        )
        assert len(get_from_summary(summary, date="2018-05-15")) == 1
        assert len(get_from_summary(summary, date="2018-05-16")) == 0
        assert len(get_from_summary(summary, date="2018-05-17")) == 1
        assert len(get_from_summary(summary, date="2018-05-18")) == 1
        assert len(get_from_summary(summary, date="2018-05-19")) == 0
        assert len(get_from_summary(summary, date="2018-05-20")) == 3

        assert (
           154667.123 == get_from_summary(summary, date="2018-05-18")[0]["int_luminosity"]
        )
        assert get_from_summary(summary, date="2018-05-18")[0]["number_of_ls"] == 144
        assert get_from_summary(summary, date="2018-05-14")[2]["int_luminosity"] == 0.1234

    def test_get_queryset(self):
        mixer.blend("certhelper.RunInfo", run_number=123456)
        mixer.blend("certhelper.RunInfo", run_number=234567)

        assert len(RunInfo.objects.all()) == 2
        assert len(RunInfo.all_objects.all()) == 2
        RunInfo.objects.all().delete()
        assert RunInfo.objects.exists() is False
        assert RunInfo.all_objects.exists() is True

    def test_alive_only(self):
        mixer.blend("certhelper.RunInfo", run_number=123456)
        mixer.blend("certhelper.RunInfo", run_number=234567)
        mixer.blend("certhelper.RunInfo", run_number=345678)
        mixer.blend("certhelper.RunInfo", run_number=456789)
        mixer.blend("certhelper.RunInfo", run_number=567890)

        assert len(RunInfo.objects.all()) == 5

        RunInfo.objects.filter(run_number__gt=300000).delete()

        assert len(RunInfo.objects.all()) == 2
        assert len(RunInfo.objects.all().alive()) == 2
        assert len(RunInfo.objects.all().dead()) == 0
        assert len(RunInfo.all_objects.all()) == 5
        assert len(RunInfo.all_objects.all().alive()) == 2
        assert len(RunInfo.all_objects.all().dead()) == 3

        RunInfo.all_objects.filter(run_number__gt=300000).dead().restore()
        assert len(RunInfo.objects.all()) == 5
        assert len(RunInfo.all_objects.all()) == 5
        assert len(RunInfo.all_objects.all().alive()) == 5
        assert len(RunInfo.all_objects.all().dead()) == 0

    def test_check_if_certified(self, some_certified_runs):
        check = RunInfo.objects.check_if_certified(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15]
        )

        assert check["missing"] == [0, 8, 15]

        collisions = check["collisions"]
        cosmics = check["cosmics"]

        assert collisions["good"] == [1, 3]
        assert collisions["bad"] == [6]
        assert collisions["prompt_missing"] == [2, 7]
        assert collisions["changed_good"] == [5]
        assert collisions["changed_bad"] == [4]

        assert cosmics["good"] == [11]
        assert cosmics["bad"] == []
        assert cosmics["prompt_missing"] == [10, 12, 13]
        assert cosmics["changed_good"] == []
        assert cosmics["changed_bad"] == [14]

        check = RunInfo.objects.check_if_certified(
            [
                0,
                "1",
                "2",
                3,
                "4",
                5,
                "6",
                "hase",
                "7",
                8,
                "10",
                11,
                "12",
                "13",
                "14",
                "15",
                "abc",
            ]
        )

        collisions = check["collisions"]
        cosmics = check["cosmics"]

        assert collisions["good"] == [1, 3]
        assert collisions["bad"] == [6]
        assert collisions["prompt_missing"] == [2, 7]
        assert collisions["changed_good"] == [5]
        assert collisions["changed_bad"] == [4]

        assert cosmics["good"] == [11]
        assert cosmics["bad"] == []
        assert cosmics["prompt_missing"] == [10, 12, 13]
        assert cosmics["changed_good"] == []
        assert cosmics["changed_bad"] == [14]

    def test_check_integrity_of_run(self):
        """
        Checks if the given run has any inconsistencies with already certified runs.
        :return:
        """
        express_type = mixer.blend(
            "certhelper.Type", reco="Express", beamtype="HeavyIon-Proton"
        )

        prompt_type = mixer.blend(
            "certhelper.Type",
            reco="Prompt",
            runtype=express_type.runtype,
            bfield=express_type.bfield,
            beamtype=express_type.beamtype,
            beamenergy=express_type.beamenergy,
        )

        express_ref = mixer.blend("certhelper.ReferenceRun", reco="Express")
        prompt_ref = mixer.blend("certhelper.ReferenceRun", reco="Prompt")

        express_run = mixer.blend(
            "certhelper.RunInfo", type=express_type, reference_run=express_ref
        )

        # necessary because int_luminosity is buggy for some reason:
        # -4.654900146333296E+17 != -465490014633329600.00
        express_run.refresh_from_db()

        prompt_run = RunInfo.objects.get()
        prompt_run.pk = None
        prompt_run.type = prompt_type
        prompt_run.reference_run = prompt_ref

        assert {} == RunInfo.objects.check_integrity_of_run(prompt_run)

        prompt_run.type.beamtype = "Proton-Proton"

        assert not prompt_run.pk
        assert "beamtype" in RunInfo.objects.check_integrity_of_run(prompt_run)

        prompt_run.save()
        assert express_run.pk + 1 == prompt_run.pk

        assert "beamtype" in RunInfo.objects.check_integrity_of_run(prompt_run)

        express_run.pixel = "Good"
        express_run.save()
        prompt_run.pixel = "Lowstat"
        assert "beamtype" in RunInfo.objects.check_integrity_of_run(prompt_run)
        assert "pixel" in RunInfo.objects.check_integrity_of_run(prompt_run)

        prompt_run.type.beamtype = "HeavyIon-Proton"
        express_run.pixel = "Lowstat"
        check = RunInfo.objects.check_integrity_of_run(prompt_run)
        assert "pixel" in check
        assert "Good" == check["pixel"]
        assert "Good" != prompt_run.pixel
        express_run.save()
        prompt_run.save()

        assert {} == RunInfo.objects.check_integrity_of_run(prompt_run)
        assert {} == RunInfo.objects.check_integrity_of_run(express_run)

        express_run.type.runtype = "Cosmics"
        prompt_run.type.runtype = "Collisions"
        express_run.type.save()

        check = RunInfo.objects.check_integrity_of_run(prompt_run)
        assert {"runtype": "Cosmics"} == check
        prompt_run.type.runtype = "Cosmics"

        check = RunInfo.objects.check_integrity_of_run(prompt_run)
        assert {} == check

        express_run.int_luminosity = 3.1
        prompt_run.int_luminosity = Decimal("3.3")
        express_run.save()

        check = RunInfo.objects.check_integrity_of_run(prompt_run)
        assert {"int_luminosity": Decimal("3.1")} == check

        prompt_run.int_luminosity = Decimal("3.2")
        check = RunInfo.objects.check_integrity_of_run(prompt_run)
        assert {} == check
