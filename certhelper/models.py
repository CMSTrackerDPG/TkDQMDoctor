from django.db import models

class RunInfo(models.Model):
    type                  = models.CharField(max_length=100)
    dataset               = models.CharField(max_length=200)
    reference_run_number  = models.IntegerField()

    run_number            = models.IntegerField()
    number_of_ls          = models.IntegerField()
    integrated_luminosity = models.DecimalField(max_digits=20, decimal_places=2)
    pixel                 = models.BooleanField()
    sistrip               = models.BooleanField()
    tracking              = models.BooleanField()
    comment               = models.TextField()
        