import collections

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import (
    QuerySet,
    Q,
    Count,
    Sum,
    FloatField,
    When,
    Case,
    Value,
    CharField,
    Min,
    Max,
)
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone

from certhelper.utilities.utilities import convert_run_registry_to_runinfo, chunks
from runregistry.client import TrackerRunRegistryClient


class SoftDeletionQuerySet(QuerySet):
    """
    QuerySet that marks objects as deleted rather than
    irrevocably deleting objects as default behavior
    """

    def delete(self):
        """
        only pretend to delete (mark as deleted)
        """
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        irrevocably delete all objects in the QuerySet
        """
        return super(SoftDeletionQuerySet, self).delete()

    def restore(self):
        """
        only pretend to delete (mark as deleted)
        """
        return super(SoftDeletionQuerySet, self).update(deleted_at=None)

    def alive(self):
        """
        return only objects that are not deleted
        """
        return self.filter(deleted_at=None)

    def dead(self):
        """
        return only objects that are marked as deleted
        """
        return self.exclude(deleted_at=None)


class RunInfoQuerySet(SoftDeletionQuerySet):
    def annotate_status(self):
        good_criteria = ("Good", "Lowstat")

        return self.annotate(
            status=Case(
                When(
                    (Q(type__runtype="Cosmics") | Q(pixel__in=good_criteria))
                    & Q(sistrip__in=good_criteria)
                    & Q(tracking__in=good_criteria),
                    then=Value("good"),
                ),
                default=Value("bad"),
                output_field=CharField(),
            )
        )

    def filter_flag_changed(self, until=None):
        """
        Filters the queryset to all runs where the flag has changed
        """
        from certhelper.models import RunInfo

        # Group by unique run_number, status pairs
        # if a run_number appears more than once, it means that the flag changed

        runs = RunInfo.objects.all()
        if until:
            runs = runs.filter(date__lte=until)

        run_number_list = [
            run["run_number"]
            for run in runs.annotate_status()
                .order_by("run_number")
                .values("run_number", "status")
                .annotate(times_certified=Count("run_number"))
        ]

        changed_flag_runs = [
            run
            for run, count in collections.Counter(run_number_list).items()
            if count > 1
        ]

        return self.filter(run_number__in=changed_flag_runs)

    def good(self):
        good_criteria = ("Good", "Lowstat")

        return (
            self.filter(sistrip__in=good_criteria)
                .filter(tracking__in=good_criteria)
                .filter(Q(type__runtype="Cosmics") | Q(pixel__in=good_criteria))
        )

    def bad(self):
        bad_criteria = ["Bad", "Excluded"]

        return self.filter(
            Q(sistrip__in=bad_criteria)
            | Q(tracking__in=bad_criteria)
            | (Q(pixel__in=bad_criteria) & Q(type__runtype="Collisions"))
        )

    # TODO rename 'type__runtype' to just 'run__type'
    def summary(self):
        """
        Create basic summary with int_luminosity and number_of_ls per type
        """
        summary_dict = (
            self.order_by("type__runtype", "type__reco")
                .values("type__runtype", "type__reco")
                .annotate(
                runs_certified=Count("pk"),
                int_luminosity=Sum("int_luminosity", output_field=FloatField()),
                number_of_ls=Sum("number_of_ls"),
            )
        )
        """
        Add List of run_numbers per type to the summary
        """
        for d in summary_dict:
            runs_per_type = self.filter(
                type__runtype=d.get("type__runtype"), type__reco=d.get("type__reco")
            ).order_by("run_number")

            good_run_numbers = [r.run_number for r in runs_per_type.good()]

            bad_run_numbers = [r.run_number for r in runs_per_type.bad()]

            d.update(
                {"run_numbers": {"good": good_run_numbers, "bad": bad_run_numbers}}
            )

        return summary_dict

    def summary_per_day(self):
        summary_dict = (
            self.order_by("date", "type__runtype", "type__reco")
                .values("date", "type__runtype", "type__reco")
                .annotate(
                runs_certified=Count("pk"),
                int_luminosity=Sum("int_luminosity", output_field=FloatField()),
                number_of_ls=Sum("number_of_ls"),
                day=(ExtractWeekDay("date")),
            )
        )

        """
        Add List of run_numbers per day and type to the summary
        """
        for d in summary_dict:
            runs = self.filter(
                date=d.get("date"),
                type__runtype=d.get("type__runtype"),
                type__reco=d.get("type__reco"),
            ).order_by("run_number")
            run_numbers = [run.run_number for run in runs]
            d.update({"run_numbers": self.compare_list_if_certified(run_numbers)})

        return summary_dict

    def compare_list_if_certified(self, list_of_run_numbers):
        """
        :param list_of_run_numbers: list of run_numbers e.g. [317696, 123456, 317696, 317696]
        :type list_of_run_numbers: list
        :return: dictionary of run_numbers
        :rtype: dictionary {"good": [], "bad": [], "missing": [], "conflicting": []}
        """

        d = {"good": [], "bad": [], "missing": [], "different_flags": []}

        runs = self.annotate_status()

        cleaned_run_number_list = [
            i for i in list_of_run_numbers if type(i) == int or i.isdigit()
        ]

        changed_flag_runs = runs.filter(
            run_number__in=cleaned_run_number_list
        ).filter_flag_changed()

        for run_number in list_of_run_numbers:
            try:
                run = runs.get(run_number=run_number)
                d["{}".format(run.status)].append(run_number)
            except (ObjectDoesNotExist, ValueError):
                d["missing"].append(run_number)
            except MultipleObjectsReturned:
                run_pair = changed_flag_runs.filter(run_number=run_number)
                if run_pair.exists():
                    d["different_flags"].append(run_number)
                else:
                    r = runs.filter(run_number=run_number)
                    d["{}".format(r[0].status)].append(run_number)

        return d

    def changed_flags(self):
        """
        compares all run_numbers in current QuerySet against whole database
        and returns a list of run_numbers where the flags changed

        Example: Run was certified good in express and bad promptreco
        """
        return list(set([run.run_number for run in self.filter_flag_changed()]))

    def today(self):
        pass

    def this_week(self):
        """
        filters QuerySet to only show runs of the current week
        week starts on monday at 00:00:00 and ends on sunday at 23:59:59
        """
        pass

    def last_week(self):
        """
        filters QuerySet to only show runs of the current week
        week starts on monday at 00:00:00 and ends on sunday at 23:59:59
        """
        pass

    def calendar_week(self, week_number):
        """
        filters QuerySet to only show runs of the specified calendar week

        A week starts on a monday. The week of a year that contains the first
        Thursday has the week number 1

        :param week_number: Week number according to the ISO-8601 standard.
        """
        pass

    def collisions(self):
        return self.filter(type__runtype="Collisions")

    def cosmics(self):
        return self.filter(type__runtype="Cosmics")

    def express(self):
        return self.filter(type__reco="Express")

    def prompt(self):
        return self.filter(type__reco="Prompt")

    def rereco(self):
        return self.filter(type__reco="reReco")

    def run_numbers(self):
        """
        :return: sorted list of run numbers (without duplicates)
        """
        return list(
            self.values_list("run_number", flat=True).order_by("run_number").distinct()
        )

    def fill_numbers(self):
        """
        :return: sorted list of fill numbers (without duplicates)
        """
        if not self.run_numbers():
            return []
        client = TrackerRunRegistryClient()
        return client.get_unique_fill_numbers_by_run_number(self.run_numbers())

    def pks(self):
        """
        :return: sorted list of primary keys
        """
        return list(self.values_list("id", flat=True).order_by("id"))

    def integrated_luminosity(self):
        if len(self) == 0:
            return 0
        return float(self.aggregate(Sum("int_luminosity"))["int_luminosity__sum"])

    def lumisections(self):
        if len(self) == 0:
            return 0
        return self.aggregate(Sum("number_of_ls"))["number_of_ls__sum"]

    def total_number(self):
        return len(self)

    def days(self):
        return [
            d["date"].strftime("%Y-%m-%d")
            for d in self.order_by("date").values("date").distinct()
        ]

    def reference_run_numbers(self):
        ref_dict = (
            self.order_by("reference_run__reference_run")
                .values("reference_run__reference_run")
                .distinct()
        )

        return [ref["reference_run__reference_run"] for ref in ref_dict]

    def reference_runs(self):
        from .models import ReferenceRun

        ref_ids = self.values_list("reference_run", flat=True).order_by("reference_run")
        return ReferenceRun.objects.filter(id__in=ref_ids)

    def types(self):
        from .models import Type

        type_ids = self.values_list("type", flat=True).order_by("type")
        return Type.objects.filter(id__in=type_ids)

    def per_day(self):
        """values_list
        Returns a list of querysets where one queryset is a specific day
        """
        per_day_list = []
        for day in self.days():
            per_day_list.append(self.filter(date=day))

        return per_day_list

    def per_type(self):
        """
        :return: list of querysets with one type per queryset
        """
        return [self.filter(type=t) for t in self.types()]

    def trackermap_missing(self):
        return self.filter(trackermap="Missing")

    def shifters(self):
        """
        :return: list of users (shifters) in the queryset
        """
        user_ids = list(
            self.values_list("userid", flat=True).order_by("userid").distinct()
        )

        return User.objects.filter(id__in=user_ids)

    def week_number(self):
        """
        :return: string of the week number(s) the runs were certified in
        """
        if not self.exists():
            return ""
        min_week = self.aggregate(Min("date"))["date__min"].isocalendar()[1]
        max_week = self.aggregate(Max("date"))["date__max"].isocalendar()[1]
        if min_week != max_week:
            return "{}-{}".format(min_week, max_week)
        return min_week

    def order_by_run_number(self):
        return self.order_by("run_number")

    def order_by_date(self):
        return self.order_by("date", "run_number")

    def print(self):
        """
        Prints out QuerySet to have an easy Overview
        """
        print()
        print(
            "{:10} {:10} {:10} {:10} {:10} {:10}".format(
                "run number", "type", "reco", "int lumi", "date", "flag"
            )
        )
        for run in self.annotate_status()[:50]:
            print(
                "{:10} {:10} {:10} {:10} {} {:10}".format(
                    run.run_number,
                    run.type.runtype,
                    run.type.reco,
                    run.int_luminosity,
                    run.date,
                    run.status,
                )
            )

    def print_verbose(self):
        """
        Prints out QuerySet to have an easy Overview
        """
        print(
            "{:<10} {:<10} {:<10} {:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} "
            "{:<10} {:<10}".format(
                "run number",
                "run type",
                "reco",
                "reference run",
                "trackermap",
                "lumisec",
                "int lumi",
                "pixel",
                "sistrip",
                "tracking",
                "date",
                "user",
            )
        )

        for run in self.annotate_status()[:50]:
            print(
                "{:<10} {:<10} {:<10} {:<30} {:<10} {:<10} {:<10} {:<10} {:<10} "
                "{:<10} {} {}".format(
                    run.run_number,
                    run.type.runtype,
                    run.type.reco,
                    "{} {} ({})".format(
                        run.reference_run.runtype,
                        run.reference_run.reco,
                        run.reference_run.reference_run,
                    ),
                    run.trackermap,
                    run.number_of_ls,
                    run.int_luminosity,
                    run.pixel,
                    run.sistrip,
                    run.tracking,
                    run.date,
                    run.userid,
                )
            )

    def print_types(self):
        for run_type in self.types():
            print(
                "{:10} {:10} {:10} {:10} {:10} {:10}".format(
                    run_type.runtype,
                    run_type.reco,
                    run_type.bfield,
                    run_type.beamtype,
                    run_type.beamenergy,
                    run_type.dataset,
                )
            )

    def print_reference_runs(self):
        for ref in self.reference_runs():
            print(
                "{:10} {:10} {:10} {:10} {:10} {:10} {:10}".format(
                    ref.reference_run,
                    ref.runtype,
                    ref.reco,
                    ref.bfield,
                    ref.beamtype,
                    ref.beamenergy,
                    ref.dataset,
                )
            )

    def compare_with_run_registry(self):
        run_numbers = self.run_numbers()
        run_registry = TrackerRunRegistryClient()
        keys = [
            "run_number",
            "type__runtype",
            "type__reco",
            "pixel",
            "sistrip",
            "tracking",
            "pixel_lowstat",
            "sistrip_lowstat",
            "tracking_lowstat",
        ]

        run_info_tuple_set = set(self.values_list(*keys))

        # the resthub api cannot handle more than 1000 elements in the SQL query
        if len(run_numbers) <= 500:
            run_registry_entries = run_registry.get_runs_by_list(run_numbers)
        else:  # split the list if it is too big
            list_of_run_number_lists = chunks(run_numbers, 500)
            run_registry_entries = []
            for run_number_list in list_of_run_number_lists:
                new_entries = run_registry.get_runs_by_list(run_number_list)
                run_registry_entries.extend(new_entries)

        convert_run_registry_to_runinfo(run_registry_entries)
        run_registry_tuple_set = {
            tuple(d[key] for key in keys) for d in run_registry_entries
        }

        deviating_run_info_tuple_list = sorted(
            run_info_tuple_set - run_registry_tuple_set
        )
        corresponding_run_registry_runs = []
        for run in deviating_run_info_tuple_list:
            elements = list(
                filter(
                    lambda x: x[0] == run[0] and x[2] == run[2], run_registry_tuple_set
                )
            )
            if not elements:
                elements = [("", "", "", "", "", "", False, False, False)]
            corresponding_run_registry_runs.extend(elements)

        deviating_run_info_dict = [
            dict(zip(keys, run)) for run in deviating_run_info_tuple_list
        ]
        corresponding_run_registry_dict = [
            dict(zip(keys, run)) for run in corresponding_run_registry_runs
        ]

        return deviating_run_info_dict, corresponding_run_registry_dict

    def annotate_fill_number(self):
        """
        Adds the lhc fill number from the Run Registry

        :return: QuerySet with added LHC fill number
        """
        run_registry = TrackerRunRegistryClient()
        fills = run_registry.get_fill_number_by_run_number(self.run_numbers())
        for run in self:
            run.fill_number = list(
                filter(lambda x: x["run_number"] == run.run_number, fills)
            )[0]["fill_number"]

    def group_run_numbers_by_fill_number(self):
        run_registry = TrackerRunRegistryClient()
        return run_registry.get_grouped_fill_numbers_by_run_number(self.run_numbers())
