from django.contrib import admin
from .models import *


class ReferenceRunAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class RunInfoAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class TypeAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class CategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class SubCategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class SubSubCategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


# Register your models here.
admin.site.register(ReferenceRun, ReferenceRunAdmin)
admin.site.register(RunInfo, RunInfoAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(SubSubCategory, SubSubCategoryAdmin)
