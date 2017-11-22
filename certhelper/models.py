from django.db import models


class ReferenceInfo(models.Model):
    type                  = models.CharField(max_length=100)
    dataset               = models.CharField(max_length=200)
    reference_run_number  = models.IntegerField()

    def __str__(self):
        return str(str(self.reference_run_number) + " " + self.type)


class RunInfo(models.Model):
    reference_info        = models.ForeignKey(ReferenceInfo, on_delete=models.CASCADE, related_name='runinfos')
    run_number            = models.IntegerField()
    number_of_ls          = models.IntegerField()
    integrated_luminosity = models.DecimalField(max_digits=20, decimal_places=2)
    pixel                 = models.BooleanField()
    sistrip               = models.BooleanField()
    tracking              = models.BooleanField()
    comment               = models.TextField()
