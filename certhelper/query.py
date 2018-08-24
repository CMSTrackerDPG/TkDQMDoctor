import collections

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import QuerySet, Q, Count, Sum, FloatField, When, Case, Value, \
    CharField
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone

from certhelper.utilities.utilities import uniquely_sorted


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
        good_criteria = ('Good', 'Lowstat')

        return self.annotate(status=Case(
            When(
                (Q(type__runtype="Cosmics") | Q(pixel__in=good_criteria)) &
                Q(sistrip__in=good_criteria) &
                Q(tracking__in=good_criteria),
                then=Value('good')),
            default=Value('bad'),
            output_field=CharField())
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



        run_number_list = [run["run_number"]
                           for run
                           in runs \
                               .annotate_status() \
                               .order_by("run_number") \
                               .values("run_number", "status") \
                               .annotate(times_certified=Count("run_number"))]

        changed_flag_runs = [run
                             for run, count
                             in collections.Counter(run_number_list).items()
                             if count > 1]

        return self.filter(run_number__in=changed_flag_runs)

    def good(self):
        good_criteria = ('Good', 'Lowstat')

        return self.filter(sistrip__in=good_criteria).filter(
            tracking__in=good_criteria).filter(
            Q(type__runtype="Cosmics") | Q(pixel__in=good_criteria))

    def bad(self):
        bad_criteria = ['Bad', 'Excluded']

        return self.filter(
            Q(sistrip__in=bad_criteria) | Q(tracking__in=bad_criteria) | (
                    Q(pixel__in=bad_criteria) & Q(type__runtype="Collisions")))

    # TODO rename 'type__runtype' to just 'run__type'
    def summary(self):
        """
        Create basic summary with int_luminosity and number_of_ls per type
        """
        summary_dict = self \
            .order_by('type__runtype', 'type__reco') \
            .values('type__runtype', 'type__reco') \
            .annotate(
            runs_certified=Count('pk'),
            int_luminosity=Sum('int_luminosity', output_field=FloatField()),
            number_of_ls=Sum('number_of_ls')
        )
        """
        Add List of run_numbers per type to the summary
        """
        for d in summary_dict:
            runs_per_type = self.filter(
                type__runtype=d.get("type__runtype"),
                type__reco=d.get("type__reco")).order_by("run_number")

            good_run_numbers = [
                r.run_number
                for r in
                runs_per_type.good()
            ]

            bad_run_numbers = [
                r.run_number
                for r in
                runs_per_type.bad()
            ]

            d.update({"run_numbers": {
                "good": good_run_numbers,
                "bad": bad_run_numbers}})

        return summary_dict

    def summary_per_day(self):
        summary_dict = self \
            .order_by('date', 'type__runtype', 'type__reco') \
            .values('date', 'type__runtype', 'type__reco') \
            .annotate(
            runs_certified=Count('pk'),
            int_luminosity=Sum('int_luminosity', output_field=FloatField()),
            number_of_ls=Sum('number_of_ls'),
            day=(ExtractWeekDay('date'))
        )

        """
        Add List of run_numbers per day and type to the summary
        """
        for d in summary_dict:
            runs = self.filter(
                date=d.get("date"),
                type__runtype=d.get("type__runtype"),
                type__reco=d.get("type__reco")) \
                .order_by("run_number")
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

        d = {
            "good": [],
            "bad": [],
            "missing": [],
            "different_flags": [],
        }

        runs = self.annotate_status()

        cleaned_run_number_list = [
            i for i in list_of_run_numbers
            if type(i) == int or i.isdigit()]

        changed_flag_runs = runs\
            .filter(run_number__in=cleaned_run_number_list)\
            .filter_flag_changed()

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
        return self.filter(type__reco="ReReco")

    def run_numbers(self):
        """
        :return: sorted list of run numbers (without duplicates)
        """
        return uniquely_sorted(self.values_list('run_number', flat=True)
                               .order_by('run_number'))

    def pks(self):
        """
        :return: sorted list of primary keys
        """
        return list(self.values_list('id', flat=True).order_by('id'))

    def integrated_luminosity(self):
        if len(self) == 0:
            return 0
        return float(self.aggregate(Sum('int_luminosity'))["int_luminosity__sum"])

    def total_number(self):
        return len(self)

    def days(self):
        return [d['date'].strftime('%Y-%m-%d') for d in
                self.order_by('date').values('date').distinct()]

    def reference_run_numbers(self):
        ref_dict = self \
            .order_by('reference_run__reference_run') \
            .values('reference_run__reference_run') \
            .distinct()

        return [ref["reference_run__reference_run"] for ref in ref_dict]

    def reference_runs(self):
        from .models import ReferenceRun
        return ReferenceRun.objects \
            .filter(reference_run__in=self.reference_run_numbers()) \
            .order_by("reference_run")

    def per_day(self):
        """
        Returns a list of querysets where one queryset is a specific day
        """
        per_day_list = []
        for day in self.days():
            per_day_list.append(self.filter(date=day))

        return per_day_list

    def print(self):
        """
        Prints out QuerySet to have an easy Overview
        """
        print()
        print("{:10} {:10} {:10} {:10} {:10} {:10}".format("run number", "type", "reco",
                                                           "int lumi", "date", "flag"))
        for run in self.annotate_status()[:50]:
            print("{:10} {:10} {:10} {:10} {} {:10}".format(run.run_number,
                                                            run.type.runtype,
                                                            run.type.reco,
                                                            run.int_luminosity,
                                                            run.date, run.status))

