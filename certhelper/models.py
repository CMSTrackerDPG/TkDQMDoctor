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
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from certhelper.manager import SoftDeletionManager, RunInfoManager
from certhelper.utilities.utilities import get_full_name

RECO_CHOICES = (('Express', 'Express'), ('Prompt', 'Prompt'), ('reReco', 'reReco'))
RUNTYPE_CHOICES = (('Cosmics', 'Cosmics'), ('Collisions', 'Collisions'))
BFIELD_CHOICES = (('0 T', '0 T'), ('3.8 T', '3.8 T'))
BEAMTYPE_CHOICES = (('Cosmics', 'Cosmics'), ('Proton-Proton', 'Proton-Proton'), ('HeavyIon-Proton', 'HeavyIon-Proton'),
                    ('HeavyIon-HeavyIon', 'HeavyIon-HeavyIon'))
BEAMENERGY_CHOICES = (('Cosmics', 'Cosmics'), ('5 TeV', '5 TeV'), ('13 TeV', '13 TeV'))


class SoftDeletionModel(models.Model):
    """
    Marks object as deleted rather than irrevocably deleting that object
    Also adds timestamps for creation time and update time

    check https://medium.com/@adriennedomingus/soft-deletion-in-django-e4882581c340 for further information
    """
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(SoftDeletionModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()

    def restore(self):
        self.deleted_at = None
        self.save()


class Category(SoftDeletionModel):
    name = models.CharField(max_length=30, help_text="Title for the category of problems found")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


# TODO make parent_category not nullable
class SubCategory(SoftDeletionModel):
    name = models.CharField(max_length=30)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


# TODO make parent_category not nullable
class SubSubCategory(SoftDeletionModel):
    name = models.CharField(max_length=30)
    parent_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class Type(SoftDeletionModel):
    reco = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    beamenergy = models.CharField(max_length=10, choices=BEAMENERGY_CHOICES)
    dataset = models.CharField(max_length=150)

    class Meta:
        unique_together = ["reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]

    def __str__(self):
        return str(self.reco) + " " + str(self.runtype) + " " + str(self.bfield) + " " + str(self.beamtype) + " " + str(
            self.beamenergy) + " " + str(self.dataset)


# ReferenceRun that should only be added by shift-leaders / staff
class ReferenceRun(SoftDeletionModel):
    reference_run = models.IntegerField()
    reco = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    beamenergy = models.CharField(max_length=10, choices=BEAMENERGY_CHOICES)
    dataset = models.CharField(max_length=150)

    class Meta:
        unique_together = ["reference_run", "reco", "runtype", "bfield", "beamtype", "beamenergy", "dataset"]
        ordering = ('-reference_run',)

    def __str__(self):
        return str(self.reference_run) + " " + str(self.reco) + " " + str(self.runtype) + " " + str(
            self.bfield) + " " + str(self.beamtype) + " " + str(self.beamenergy) + " " + str(self.dataset)


# Runs that shifters are certifying
class RunInfo(SoftDeletionModel):
    objects = RunInfoManager()
    all_objects = RunInfoManager(alive_only=False)

    GOOD_BAD_CHOICES = (('Good', 'Good'), ('Bad', 'Bad'), ('Lowstat', 'Lowstat'), ('Excluded', 'Excluded'))
    TRACKERMAP_CHOICES = (('Exists', 'Exists'), ('Missing', 'Missing'))
    userid = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    reference_run = models.ForeignKey(ReferenceRun, on_delete=models.CASCADE)
    run_number = models.PositiveIntegerField()
    trackermap = models.CharField(max_length=7, choices=TRACKERMAP_CHOICES)
    number_of_ls = models.PositiveIntegerField()
    int_luminosity = models.DecimalField(max_digits=20, decimal_places=2)
    pixel = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    sistrip = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    tracking = models.CharField(max_length=10, choices=GOOD_BAD_CHOICES)
    comment = models.TextField(blank=True)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    subsubcategory = models.ForeignKey(SubSubCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-run_number',)

    def __str__(self):
        return str(self.run_number) + ", " + str(self.type.runtype) + " " + str(self.type.reco) + \
               " (ref: " + str(self.reference_run.reference_run) + ", " + \
               str(self.reference_run.runtype) + " " + str(self.reference_run.reco) + ")"

    def is_good(self):
        assert self.type.runtype in ['Cosmics', 'Collisions']
        good_criteria = ['Good', 'Lowstat']
        candidates = [self.sistrip, self.tracking]
        if self.type.runtype == 'Collisions':
            candidates.append(self.pixel)

        for candidate in candidates:
            if candidate not in good_criteria:
                return False
        return True

    def is_bad(self):
        return not self.is_good()

    def validate_unique(self, exclude=None):
        if not self.type_id:
            raise ValidationError("Type is empty")

        qs = RunInfo.objects.filter(
            run_number=self.run_number,
            type=self.type,
            reference_run=self.reference_run
        )

        # If noone else certified the run and I am not editing the Run
        if qs.exists() and qs[0].pk != self.pk:
            if len(qs) != 1:
                # TODO Logging Warning, duplicate certification
                pass
            run = qs[0]
            raise ValidationError(
                'This run ({}, {} {}, (ref: {})) was already certified by {} on {}'.format(
                    run.run_number,
                    run.type.runtype,
                    run.type.reco,
                    run.reference_run.reference_run,
                    get_full_name(run.userid),
                    run.date)
            )

    def save(self):
        self.validate_unique()
        super(RunInfo, self).save()
