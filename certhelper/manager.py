from decimal import Decimal

from django.db import models

from certhelper.query import SoftDeletionQuerySet, RunInfoQuerySet
from certhelper.utilities.utilities import uniquely_sorted


class SoftDeletionManager(models.Manager):
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        :return:
        * QuerySet with the list of all objects that are not marked as deleted
        * QuerySet with all objects (including deleted) when alive_only argument is
          set to False on SoftDeletionManager
        """
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def dead(self):
        """
        :return: QuerySet containing all instances that have been deleted
        """
        return self.get_queryset().dead()

    def alive(self):
        """
        :return: QuerySet containing all instances that have not been deleted
        """
        return self.get_queryset().alive()

    # TODO check if this is necessarry
    def hard_delete(self):
        return self.get_queryset().hard_delete()


class RunInfoManager(SoftDeletionManager):
    def get_queryset(self):
        if self.alive_only:
            return RunInfoQuerySet(self.model).filter(deleted_at=None)
        return RunInfoQuerySet(self.model)

    def good(self):
        return RunInfoQuerySet(self.model).good()

    def bad(self):
        return RunInfoQuerySet(self.model).bad()

    def check_if_certified(self, list_of_run_numbers):
        list_of_run_numbers = uniquely_sorted(list_of_run_numbers)

        # TODO use self.get_queryset() instead of RunInfoQuerySet(self.model).filter
        runs = RunInfoQuerySet(self.model).filter(deleted_at=None)
        runs = runs.filter(run_number__in=list_of_run_numbers).annotate_status()

        def do_check(runs):
            flags = {
                "good": [],
                "bad": [],
                "missing": [],
                "prompt_missing": [],
                "changed_good": [],  # Express Bad -> Prompt Good
                "changed_bad": [],  # Express Good -> Prompt Bad
            }

            prompt_runs = runs.prompt()
            good_runs = prompt_runs.good()
            bad_runs = prompt_runs.bad()

            flags["good"] = good_runs.run_numbers()
            flags["bad"] = bad_runs.run_numbers()

            # TODO The backslash is redundant between brackets
            non_missing_prompt_run_numbers = [
                run["run_number"] for run in prompt_runs \
                    .order_by("run_number") \
                    .values("run_number") \
                    .distinct()
            ]

            non_missing_run_numbers = [
                run["run_number"] for run in runs \
                    .order_by("run_number") \
                    .values("run_number") \
                    .distinct()
            ]

            flags["prompt_missing"] = list(
                set(non_missing_run_numbers) - set(non_missing_prompt_run_numbers))

            express_runs = runs.express().filter(run_number__in=non_missing_run_numbers)
            good_express = express_runs.good().run_numbers()
            bad_express = express_runs.bad().run_numbers()

            for run in good_express:
                if run in flags["bad"]:
                    flags["bad"].remove(run)
                    flags["changed_bad"].append(run)

            for run in bad_express:
                if run in flags["good"]:
                    flags["good"].remove(run)
                    flags["changed_good"].append(run)

            for d in flags.values():
                d.sort()
            return flags

        check_dictionary = {
            "collisions": do_check(runs.collisions()),
            "cosmics": do_check(runs.cosmics())
        }

        non_missing_run_numbers = []

        for key, dic in check_dictionary.items():
            for key, value in dic.items():
                for run_number in value:
                    non_missing_run_numbers.append(run_number)

        check_dictionary["missing"] = list(
            (set(list_of_run_numbers) - set(non_missing_run_numbers))
        )

        return check_dictionary

    def check_integrity_of_run(self, run):
        """
        Checks if the given run is consistent with existing runs.

        For example, if a collisions express run with the run number 333333 was
        certified then the collisions prompt run with the same run number should have
        the same runtype, bfield, energy, number_of_ls, int_lumi, ...

        Also in most cases the components pixel, sistrip, tracking should match,
        but can vary from time to time. If they vary then the shifter should double
        check that this is what he intended.

        :param run: RunInfo instance
        :return: dictionary containing the mismatches and the counterpart value.
        empty means no mismatch.
        """

        from .models import RunInfo, Type
        try:
            if run.type.reco == "reReco":
                return {}
        except Type.DoesNotExist:
            # No Type selected yet
            return {}

        type_attributes_to_be_checked = [
            "runtype", "bfield", "beamtype",  # "beamenergy",
        ]
        run_attributes_to_be_checked = [
            "number_of_ls",
            "pixel",
            "sistrip",
            "tracking",
            "pixel_lowstat",
            "sistrip_lowstat",
            "tracking_lowstat"
        ]
        decimal_attributes_to_be_checked = [
            "int_luminosity",
        ]

        mismatches = {}

        try:
            counterpart_reco = "Express" if run.type.reco == "Prompt" else "Prompt"

            counterpart_run = self.get_queryset().get(
                run_number=run.run_number,
                type__reco=counterpart_reco
            )

            counterpart_type = counterpart_run.type
            assert counterpart_run.type.reco != run.type.reco

            mismatches.update({
                attribute: getattr(counterpart_type, attribute)
                for attribute in type_attributes_to_be_checked
                if getattr(run.type, attribute) is not None and
                   getattr(counterpart_type, attribute) != getattr(run.type, attribute)
            })

            mismatches.update({
                attribute: getattr(counterpart_run, attribute)
                for attribute in run_attributes_to_be_checked
                if getattr(run, attribute) is not None and
                   getattr(counterpart_run, attribute) != getattr(run, attribute)
            })

            mismatches.update({
                attribute: getattr(counterpart_run, attribute)
                for attribute in decimal_attributes_to_be_checked
                if getattr(run, attribute) is not None and
                    abs(
                        getattr(counterpart_run, attribute) - getattr(run, attribute)
                    ) > Decimal("0.1")
            })

            return mismatches
        except RunInfo.DoesNotExist:
            # No counterpart means no mismatch
            return {}
