"""
Models define the database schema and the data that is stored in the database.
For (most) of the models there is a corresponding FORM so that it is possible
for users to add data to the model and to display it
TkDQMDoctor/dqmsite/certhelper/forms.py.
i.e

FORM               |  MODEL
====================================
ReferenceRunForm   |  ReferenceRun
RunInfoForm        |  RunInfo
TypeForm           |  Type


"""

from django.db import models

RECO_CHOICES       = (('Express','Express'),('Prompt','Prompt'), ('reReco', 'reReco'))
RUNTYPE_CHOICES    = (('Cosmics','Cosmics'),('Collisions','Collisions'))
BFIELD_CHOICES     = (('0 T','0 T'),('3.8 T','3.8 T'))
BEAMTYPE_CHOICES   = (('Proton-Proton','Proton-Proton'),('HeavyIon-Proton','HeavyIon-Proton'),('HeavyIon-HeavyIon', 'HeavyIon-HeavyIon'))
BEAMENERGY_CHOICES = (('5 TeV', '5 TeV'), ('13 TeV', '13 TeV'))

class Type(models.Model):
    reco                  = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype               = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield                = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype              = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    beamenergy            = models.CharField(max_length=10, choices=BEAMENERGY_CHOICES)
    dataset               = models.CharField(max_length=150)

    class Meta:
        unique_together = ["reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]
        
    def __str__(self):
        return str(self.reco) + " " + str(self.runtype) + " " + str(self.bfield) + " " + str(self.beamtype) + " " + str(self.beamenergy) + " "  + str(self.dataset)

# ReferenceRun that should only be added by shift-leaders / staff
class ReferenceRun(models.Model):
    reference_run  = models.IntegerField()
    reco                  = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype               = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield                = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype              = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    beamenergy            = models.CharField(max_length=10, choices=BEAMENERGY_CHOICES)
    dataset               = models.CharField(max_length=150)

    class Meta:
        unique_together = ["reference_run", "reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]

    def __str__(self):
        return str(self.reference_run) + " " +  str(self.reco) + " " + str(self.runtype) + " " + str(self.bfield) + " " + str(self.beamtype) + " " + str(self.beamenergy) + " " + str(self.dataset)

# Runs that shifters are certifying
class RunInfo(models.Model):
    GOOD_BAD_CHOICES  = (('Good','Good'), ('Bad','Bad'), ('Lowstat','Lowstat'), ('Excluded','Excluded'))
    TRACKERMAP_CHOICES  = (('Exists','Exists'),('Missing','Missing'))

    type                  = models.ForeignKey(Type)
    reference_run         = models.ForeignKey(ReferenceRun)
    run_number            = models.PositiveIntegerField()
    trackermap            = models.CharField(max_length=7, choices=TRACKERMAP_CHOICES)
    number_of_ls          = models.PositiveIntegerField()
    int_luminosity        = models.DecimalField(max_digits=20, decimal_places=2)
    pixel                 = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    sistrip               = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    tracking              = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    comment               = models.TextField(blank=True)

    class Meta:
        unique_together = ["run_number", "type", "trackermap"]

    def __str__(self):
        return str(self.run_number)




