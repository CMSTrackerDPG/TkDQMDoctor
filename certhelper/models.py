from django.db import models

RECO_CHOICES      = (('Express','Express'),('Prompt','Prompt'))
RUNTYPE_CHOICES   = (('Cosmics','Cosmics'),('Collisions','Collisions'))
BFIELD_CHOICES    = (('0 T','0 T'),('3.8 T','3.8 T'))
BEAMTYPE_CHOICES  = (('P-P','P-P'),('Hi-P','Hi-P'),('Hi-Hi', 'Hi-Hi'))

class Type(models.Model):
    reco                  = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype               = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield                = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype              = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    dataset               = models.CharField(max_length=150)
    class Meta:
        unique_together = ["reco", "runtype", "bfield", "beamtype", "dataset"]
        
    def __str__(self):
        return str(self.reco) + " " + str(self.runtype) + " " + str(self.bfield) + " " + str(self.beamtype) + " " + str(self.dataset)


class ReferenceRun(models.Model):
    reference_run  = models.IntegerField()
    reco                  = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype               = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield                = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype              = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    dataset               = models.CharField(max_length=150)

    class Meta:
        unique_together = ["reference_run", "reco", "runtype", "bfield", "beamtype", "dataset"]

    def __str__(self):
        return str(self.reference_run) + " " +  str(self.reco) + " " + str(self.runtype) + " " + str(self.bfield) + " " + str(self.beamtype) + " " + str(self.dataset)

class RunInfo(models.Model):
    GOOD_BAD_CHOICES  = (('Good','Good'),('Bad','Bad'))
    TRACKERMAP_CHOICES  = (('Exists','Exists'),('Missing','Missing'))

    type                  = models.ForeignKey(Type)
    reference             = models.ForeignKey(ReferenceRun)
    run_number            = models.PositiveIntegerField()
    trackermap            = models.CharField(max_length=7, choices=TRACKERMAP_CHOICES)
    number_of_ls          = models.PositiveIntegerField()
    int_luminosity        = models.DecimalField(max_digits=20, decimal_places=2)
    pixel                 = models.CharField(max_length=4, choices=GOOD_BAD_CHOICES)
    sistrip               = models.CharField(max_length=4, choices=GOOD_BAD_CHOICES)
    tracking              = models.CharField(max_length=4, choices=GOOD_BAD_CHOICES)
    comment               = models.TextField()

    class Meta:
        unique_together = ["run_number", "type", "trackermap"]

    def __str__(self):
        return str(self.run_number)






