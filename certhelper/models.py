from django.db import models

class RunInfo(models.Model):
    title = models.CharField(max_length=200)
    comment = models.CharField(max_length=200)
    some_integer = models.IntegerField(default=0)

    def __str__(self):
        return str(self.title)

    @property
    def elog(self):
        return "this works"
        