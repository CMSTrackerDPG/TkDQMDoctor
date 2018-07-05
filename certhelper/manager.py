from django.db import models
from certhelper.query import SoftDeletionQuerySet, RunInfoQuerySet


class SoftDeletionManager(models.Manager):
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        :return:
        * QuerySet with the list of all objects that are not marked as deleted
        * QuerySet with all objects (including deleted) when alive_only argument is set to False on SoftDeletionManager
        """
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def dead(self):
        return self.get_queryset().dead()

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
