from django.db import models

class RunInfo(models.Model):
    run_number = models.IntegerField(default=0)
    number_of_ls = models.IntegerField(default=0)
    integrated_luminosity = models.IntegerField(default=0)
    pixel_status = models.BooleanField(default=False)
    sistrip_status = models.BooleanField(default=False)
    tracking_status = models.BooleanField(default=False)
    comment = models.TextField()

    def __str__(self):
        return str(self.comment)

    @property
    def elog(self):
        return "this works"
        