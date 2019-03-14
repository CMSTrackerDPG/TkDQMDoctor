Project Structure
=================

Basically, the project has the following folder structure:

::

    TkDQMDoctor
    ├───certhelper
    │   │   admin.py
    │   │   apps.py
    │   │   filters.py
    │   │   forms.py
    │   │   manager.py
    │   │   models.py
    │   │   query.py
    │   │   signals.py
    │   │   tables.py
    │   │   urls.py
    │   │   views.py
    │   │   __init__.py
    │   │
    │   ├───migrations
    │   ├───static
    │   ├───templates
    │   └───utilities
    ├───doc
    ├───dqmsite
    │       settings.py
    │       test_ci_settings.py
    │       test_settings.py
    │       urls.py
    │       wsgi.py
    │       __init__.py
    │
    ├───runregistry
    ├───static
    └───tests
        ├───certhelper
        ├───fixtures
        ├───selenium
        └───utils

runregsitry
-----------

``runregistry`` is a python module, dedicated for accessing the Run
Registry. Although a Run Registry client for python called ``rhapi.py``
already exists (https://github.com/valdasraps/resthub), it is not
compatible with Python 3. Therefore a new client had to be written that
is Python 3 compliant. If interested a dedicated GitHub repository for a
Python 3 Run Registry client can be found at
https://github.com/CMSTrackerDPG/runregcrawlr

dqmsite
-------

The ``dqmsite`` module contains the settings files for both testing and
production environment.

tests
-----

The ``tests`` module is dedicated to unit tests. They can be executed
locally via ``pytest`` or automatically via Travis CI when pushing a
branch to GitHub. A detailed description about testing can be found in
chapter Testing.

static
------

The ``static`` folder consists of static files like javascript files,
css files and images. This folder together with static files from other
applications will be
`collected <https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/>`__
and then served by the
`WhiteNoise <http://whitenoise.evans.io/en/stable/>`__ middleware when
deploying to production.

certhelper
----------

``certhelper`` is the main application, the "Certification Helper". All
the shifter and shift leader related tools are implemented there.

urls.py
~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/http/urls/

Every time a new page is added or the path of an existing page updated,
changes to ``urls.py`` have to be made. An excerpt of this file from the
TkDQmDoctor website looks like this:

.. code:: pyhton

    urlpatterns = [
        url(r'^$', views.listruns, name='list'),
        url(r'^shiftleader/$', views.shiftleader_view, name='shiftleader'),
        url(r'^summary/$', views.summaryView, name='summary'),
        url(r'^create/$', views.CreateRun.as_view(), name='create'),

        url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateRun.as_view(), name='update'),
        url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteRun.as_view(), name='delete'),
        # ...
    ]

``urlpatterns`` is a list of URLs which consist of the URL path
expressed in regular expressions, the view function which is called when
visiting the URL and a unique name for easy referral.

The views are implemented in ``views.py`` and can be either function
based views or class-based views. In the example above the view
``shiftleader_view`` is a function based view and
\`\`\`CreateRun\`\`\`\`is a class-based view which can be easily found
out by the python naming convention. Function names should always be
lowercase with an underscore as word separator and class names should
always start with a capital letter with the CamelCase naming convention.

If the view is a class-based view then additionally the ``.as_view()``
method of that class has to be called in the second url parameter.

The first view that is called when a user visits
https://tkdqmdoctor.web.cern.ch/ is ``views.listruns`` as it is the only
pattern in the urlpatterns list that matches the url: ``r'^$'``

views.py
~~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/http/views/

This ``views.py`` file consists of all the views that exist in the app.
A view function takes a Web request and returns a Web response. In most
cases the response consists of the HTML content of a web page, that will
be displayed when a user tries to visit a page. It can also be a 404
error, a JSON file, an image, etc.

A view has to be mapped to a URL in the urls.py file with an unambiguous
url path.

Most commonly a view uses a *template* to generate HTML code. In order
to specify which data should be used in the template the *context*
dictionary has to be filled accordingly

::

    context["mydata""] = "Hello World"

models.py
~~~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/db/models/

This file contains classes which inherit from *django.db.models.Model*.
Each model maps to a single database table and each instance of the
python class represents a line in that table.

The most important model is the *RunInfo* model. It represents a
certified run that will be created when a shifter submits the "Add Run"
form.

.. code:: python

    class RunInfo(SoftDeletionModel):
        # ...
        userid = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
        type = models.ForeignKey(Type, on_delete=models.CASCADE)
        reference_run = models.ForeignKey(ReferenceRun, on_delete=models.CASCADE)
        run_number = models.PositiveIntegerField()
        number_of_ls = models.PositiveIntegerField()
        int_luminosity = models.DecimalField(max_digits=20, decimal_places=2)
        # ...

manager.py
~~~~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/db/managers/

Managers are responsible for accessing the database for certain Django
models. Custom managers for a particular model extend the functionality
of the base Manager. This extra functionality, for example, could be to
only show runs that were certified as "Good". Every Django model has at
least one manager, most commonly the *objects* manager.

query.py
~~~~~~~~

https://docs.djangoproject.com/en/1.11/ref/models/querysets/

When a manager accesses the database a QuerySet object will be returned
containing the desired entity. The QuerySet object itself has methods
which can be used to further tailor the database query.

For example, does the ``cosmics`` method filter the QuerySet to only
"Cosmics" runs that were certified, rather than "Collisions".

.. code:: python

    def cosmics(self):
        return self.filter(type__runtype="Cosmics")

tables.py
~~~~~~~~~

https://django-tables2.readthedocs.io/en/latest/

When data should be presented on the website it can often be done in a
simple HTML table. The tables.py describe how these tables should look
like and what attributes of what model should be used.

signals.py
~~~~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/signals/
https://django-allauth.readthedocs.io/en/latest/signals.html

Signals provide a way of notifying an application when a certain event
happens. One signal could, for example, be to automatically update the
privileges (like shift leader or admin status) when a user performs a
login into the website.

admin.py
~~~~~~~~

https://docs.djangoproject.com/en/1.11/ref/contrib/admin/

Django provides an automatic admin interface which manages all the
models. This admin interface can be customized in the admin.py file.

apps.py
~~~~~~~

https://docs.djangoproject.com/en/1.11/ref/applications/

Before an application can be used it has to be configured in a registry
called *django.apps* which is done in *apps.py*

filters.py
~~~~~~~~~~

https://django-filter.readthedocs.io/en/master/index.html

It is often desired to only show a small portion of a database table.
Filters provide an easy way of filtering this data based on specific
criteria. One example of a filter is the run filter in the shifter view.

The way the filter should behave is specified in filters.py

forms.py
~~~~~~~~

https://docs.djangoproject.com/en/1.11/topics/forms/

When certifying a new run or updating an existing run the data has to be
entered in a form. *forms.py* specifies which attributes and which model
should be used and also how the valid form data should look like. Form
validation is performed with one of the *clean* methods of a form class.

.. code:: python

    class RunInfoForm(ModelForm):
      # ...
      def clean(self):
        cleaned_data = super(RunInfoForm, self).clean()

        is_sistrip_bad = cleaned_data.get('sistrip') == 'Bad'
        is_tracking_good = cleaned_data.get('tracking') == 'Good'
        
        if is_sistrip_bad and is_tracking_good:
        self.add_error(None, ValidationError(
            "Tracking can not be GOOD if SiStrip is BAD. Please correct."))

      # ...

templates
~~~~~~~~~

https://docs.djangoproject.com/en/1.11/ref/templates/language/

A template is a text document which can generate HTML code. Templates
have a close relationship with views, which take care of retrieving the
actual data that needs to be displayed. The data that should be
displayed in the template are defined in the *context* dictionary of the
view.

It can then be accessed directly like this:

::

    {{ mydata }}
