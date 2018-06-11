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
