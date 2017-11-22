from django.contrib import admin
from .models import RunInfo
from .models import ReferenceInfo

# Register your models here.
admin.site.register(ReferenceInfo)
admin.site.register(RunInfo)