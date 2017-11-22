from django.db import models

class RunInfo(models.Model):
    run_number = models.IntegerField()
    reference_run_number = models.IntegerField()

    number_of_ls = models.IntegerField()
    integrated_luminosity = models.DecimalField(max_digits=20, decimal_places=10)
    pixel = models.BooleanField()
    sistrip = models.BooleanField()
    tracking = models.BooleanField()
    comment = models.TextField()

    def __str__(self):
        return str(self.comment)

    @property
    def elog(self):
        return "this works"
        