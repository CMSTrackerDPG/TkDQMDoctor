import datetime

from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def add_label_class(field, class_name):
    return field.as_widget(attrs={
        "class": " ".join((field.css_classes(), class_name))
    })


@register.filter(name='addplaceholder')
def addplaceholder(value, arg):
    return value.as_widget(attrs={'placeholder': arg})


@register.filter
def dateoffset(value, offset):
    """
    Shift a date by given offset.
    Example: dateoffset("2018-10-21", 2) => "2018-10-23"
    """
    newdate = datetime.datetime.strptime(value, '%Y-%m-%d') + timezone.timedelta(offset)
    return newdate.strftime('%Y-%m-%d')


@register.filter
def yyyymmdd_to_ddmmyyyy(value):
    if isinstance(value, datetime.date):
        newdate = value
    else:
        newdate = datetime.datetime.strptime(value, '%Y-%m-%d')
    return newdate.strftime('%d-%m-%Y')

@register.filter
def yyyymmdd(value):
    return value.strftime('%Y-%m-%d')
