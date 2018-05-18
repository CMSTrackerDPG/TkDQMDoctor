import datetime

from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter(name='addplaceholder')
def addplaceholder(value, arg):
    return value.as_widget(attrs={'placeholder': arg})


@register.filter
def dateoffset(value, offset):
    newdate = datetime.datetime.strptime(value, '%Y-%m-%d') + timezone.timedelta(offset)
    # return str(value + timezone.timedelta(offset))
    #newvalue = str(newdate.day) + "-" + str(newdate.month) + "-" + str(newdate.year)
    return newdate.strftime('%d-%m-%Y')
