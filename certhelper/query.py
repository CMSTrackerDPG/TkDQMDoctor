from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import QuerySet, Q, Count, Sum, FloatField
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone


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
    def good(self):
        good_criteria = ['Good', 'Lowstat']

        return self.filter(sistrip__in=good_criteria).filter(tracking__in=good_criteria).filter(
            Q(type__runtype="Cosmics") | Q(pixel__in=good_criteria))

    def bad(self):
        bad_criteria = ['Bad', 'Excluded']

        return self.filter(Q(sistrip__in=bad_criteria) | Q(tracking__in=bad_criteria) | (
                Q(pixel__in=bad_criteria) & Q(type__runtype="Collisions")))

    # TODO rename 'type__runtype' to just 'run__type'
    def summary(self):
        return self \
            .order_by('type__runtype', 'type__reco') \
            .values('type__runtype', 'type__reco') \
            .annotate(
                runs_certified=Count('pk'),
                # TODO consider replacing FloatField with DecimalField
                int_luminosity=Sum('int_luminosity', output_field=FloatField()),
                number_of_ls=Sum('number_of_ls')
            )

    def summary_per_day(self):
        return self \
            .order_by('date', 'type__runtype', 'type__reco') \
            .values('date', 'type__runtype', 'type__reco') \
            .annotate(
                runs_certified=Count('pk'),
                int_luminosity=Sum('int_luminosity', output_field=FloatField()),
                number_of_ls=Sum('number_of_ls'),
                day=(ExtractWeekDay('date'))
            )

    def compare_list_if_certified(self, list_of_run_numbers):
        """
        :param list_of_run_numbers: list of run_numbers e.g. [317696, 123456, 317696, 317696]
        :type list_of_run_numbers: list
        :return: dictionary of run_numbers
        :rtype: dictionary {"good": [], "bad": [], "missing": [], "conflicting": []}
        """

        d = {"good": [], "bad": [], "missing": [], "conflicting": []}
        for run_number in list_of_run_numbers:
            try:
                run = self.get(run_number=run_number)
                if run.is_good:
                    d["good"].append(run_number)
                else:
                    d["bad"].append(run_number)
            except (ObjectDoesNotExist, ValueError):
                d["missing"].append(run_number)
            except MultipleObjectsReturned:
                runs = self.filter(run_number=run_number)
                is_good = runs[0].is_good
                conflict = False
                for run in runs:
                    if run.is_good != is_good:
                        conflict = True
                if conflict:
                    d["conflicting"].append(run_number)
                elif is_good:
                    d["good"].append(run_number)
                else:
                    d["bad"].append(run_number)
        return d

    def changed_flags(self):
        """
        compares all run_numbers in current QuerySet against whole database
        and returns a list of run_numbers where the flags changed

        Example: Run was certified good in express and bad promptreco
        """
        return list({run.run_number for run in self if run.flag_has_changed})

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

    def print(self):
        """
        Prints out QuerySet to have an easy Overview
        """

        print("{:<10}{:<11}{:<8}{}".format("run", "type", "reco", "good"))
        for run in self:
            print("{:<8}{:<11}{:<8}{}".format(run.run_number, run.type.runtype, run.type.reco, run.is_good))
