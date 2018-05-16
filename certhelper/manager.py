from django.db import models
from certhelper.query import SoftDeletionQuerySet


class SoftDeletionManager(models.Manager):
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

    # TODO check if this is necessarry
    def hard_delete(self):
        return self.get_queryset().hard_delete()
