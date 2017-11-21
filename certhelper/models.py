from django.db import models

class RunInfo(models.Model):
    title = models.CharField(max_length=200)
    comment = models.TextField()
    number = models.IntegerField(default=0)
    # date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.title)

    @property
    def elog(self):
        return "this works"
        