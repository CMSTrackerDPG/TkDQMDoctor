# How to develop locally

You need to take care that you have installed

* python3
* pip3

## Get all the requirements 

* pip3 install django
* pip3 install django-tables2

## Set up the project
* git clone https://github.com/imKuehlschrank/TkDQMDoctor.git
* cd TkDQMDoctor/
* python3 manage.py makemigrations certhelper
* python3 manage.py migrate
* python3 manage.py createsuperuser (follow the dialog)

## Run
* python3 manage.py runserver 
* Open browser at http://localhost:8000/admin log in with the credentials you created.
* Create a new ReferenceRun so that you can choose it in the "Add Run" Dialog
* Open http://localhost:8000.
* (Optional) create additional non-admin users that can access the protected parts of the website.

# Deploy to jandreadesktop.cern.ch
* ssh cernLogin@jandreadesktop.cern.ch
* cd /home/jandrea/tkDQMDoctor/TkDQMDoctor
* screen -r    (check for running sessions)
* python3 manage.py runserver 128.141.84.249:8000

## Remarks
If you just cloned the repository to the machine it still needs some minor adjustments to run properly:

* in settings.py add the "128.141.84.249:8000" to ALLOWED_HOSTS
* in settings.py scramble the SECRET_KEY (go wild on the keyboard)
* consider DEBUG = False


If you want to keep the server running after you exit your session use:

* screen
* python3 manage.py runserver 128.141.84.249:8000
* "Ctrl-a" "d"    (to deteach from the window)
* The process is now running detached and you can quit the session without killing the process

# Database

## How to update the database
After you modify the database schema in models.py:

* python3 manage.py makemigrations
* python3 manage.py migrate

This will update the database for you.
This does not mean that you should not check the terminal output telling you how the table was altered.

## How to create the database from scratch

* rm db.sqlite3
* rm -rf certhelper/migrations
* python3 manage.py makemigrations certhelper
* python3 manage.py migrate

# Tutorials
This tutorial takes about 4 hours to do. If you follow along it will explain a lot of the structure used in this project.
I highly recommend to -at least- read it.

Start here:

* https://docs.djangoproject.com/en/1.11/intro/tutorial01/


# ===== Documentation =====
# High level overview

Django is the framework that is used to connect the relational database in the background to the various html sites.

The routing is done in the file <code>urls.py</code>. This defines which url leads to which html page. The loading of the html-site is done through views in <code>views.py</code>. These views are being called in <code>urls.py</code>.

## Models (models.py)
Models define the database table that will be used to store everything.
So for example: Among other things our database defines a **ReferenceRun**. Its fields are 

*  Run number
*  reconstruction mode
*  bfield
*  etc.

This means that the table with the name **ReferenceRun** has columns with the above listed names.
The rows in that table are therefore individual reference runs.

## Forms (forms.py)

Forms are a way to display/input data into the database. You define your Form which uses a Model that you previously defined. In combination with djangos generic views this lets you create display/input webpages very easily.

## Views (views.py)




## Small example

```python

---------- models.py ----------
class ReferenceRun(models.Model):
    reference_run  = models.IntegerField()
    reco                  = models.CharField(max_length=30, choices=RECO_CHOICES)
    runtype               = models.CharField(max_length=30, choices=RUNTYPE_CHOICES)
    bfield                = models.CharField(max_length=30, choices=BFIELD_CHOICES)
    beamtype              = models.CharField(max_length=30, choices=BEAMTYPE_CHOICES)
    beamenergy            = models.CharField(max_length=10, choices=BEAMENERGY_CHOICES)
    dataset               = models.CharField(max_length=150)

---------- tables.py ----------
class ReferenceRunTable(tables.Table):
    class Meta:
        model = ReferenceRun
        attrs = {'class': 'table table table-hover table-bordered'}

---------- forms.py ----------
class ReferenceRunForm(ModelForm):
    class Meta:
        model = ReferenceRun
        fields = '__all__'

---------- views.py ----------
class ListReferences(SingleTableView):  # SingleTableView is part of django-tables2
    model = ReferenceRun                # and implements generation of a simple table
    table_class = ReferenceRunTable

---------- urls.py ----------
url(r'^references/$', views.ListReferences.as_view(),  name='references')

```

This is everything that is needed to define the ReferneceRun table, and display its entries in a table.

```html
{% load static %}
{% load render_table from django_tables2 %}
{% render_table table %}
```
