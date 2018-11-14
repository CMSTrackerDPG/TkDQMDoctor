Development
===========

Prerequisites
-------------

-  git
-  python3
-  Django Tutorial

In case one wants to improve the TkDQMDoctor project, the following
steps are necessary:

-  Install Python version 3.5 or 3.6
-  Setup a virtual environment
-  Install requirements packages

Installing Python
~~~~~~~~~~~~~~~~~

Python can be downloaded on https://www.python.org/ or via package
managers on a linux distribution. Python (3.4+) should come bundled with
pip and virtualenv, so everything necessary should be ready to use.

**Windows**:

https://www.python.org/downloads/windows/

**Ubuntu**:

.. code:: bash

    sudo apt install python3

**CentOS**:

.. code:: bash

    sudo yum install python36u

**Arch Linux:**

.. code:: bash

    sudo pacman -S python

Checking Python Version
^^^^^^^^^^^^^^^^^^^^^^^

The project requires a minimum python version 3.5. To ensure that the
correct python version is configured the ``python3 --version`` command
be used.

.. code:: bash

    python3 --version

.. code:: bash

    Python 3.6.5

Cloning the Project
~~~~~~~~~~~~~~~~~~~

.. code:: bash

    git clone https://github.com/ptrstn/TkDQMDoctor
    cd TkDQMDoctor

Setup Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~

It is recommended to develop in a isolated virtual environment to ensure
the correct package versions and avoid conflicts with other projects.

.. code:: bash

    python -m venv venv
    source venv/bin/active

After executing these commands a ``(venv)`` should precede the command
line.

Installing Requirements
~~~~~~~~~~~~~~~~~~~~~~~

The requirements files contain every python package that is necessary in
order to deploy the website. Each line consists of one single python
package which can be a link to a GitHub repository or the package name
and version which are registered in the `pypi <https://pypi.org/>`__
repository. Since there are additional packages used exclusively for
testing, which are not necessary in the production environment an
additional testing-requirements.txt file exists.

.. code:: bash

    pip install -r requirements.txt
    pip install -r testing-requirements.txt

Configure database connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The credentials are read from environment variables which have to be set
accordingly.

In case one wants to work with a local SQLDatabase while developing then
following environment variables should be exported.

.. code:: bash

    DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
    DJANGO_DEBUG=True
    DJANGO_DATABASE_NAME=db.sqlite3
    DJANGO_SECRET_KEY=(%g65bg+&9rbnt+h&txlxw$+lkq=g=yrp!6@v+7@&$a%9^yt-!

In case one wants to work with the development database (used in
dev-tkdmdoctor.web.cern.ch) following environment variables have to be
exported:

.. code:: bash

    DJANGO_DATABASE_ENGINE=django.db.backends.postgresql_psycopg2
    DJANGO_DATABASE_NAME=<your database name>
    DJANGO_DATABASE_USER=<your username>
    DJANGO_DATABASE_PASSWORD=<your password>
    DJANGO_DATABASE_HOST=<your database host name>
    DJANGO_DATABASE_PORT=6600
    DJANGO_DEBUG=True
    DJANGO_SECRET_KEY=p*3y)jem=g8gj)6g_qy_6opfrwg2px^+((56y02l^pqz#!gitz

Alternatively a ``.env`` file with the content above can be created.

The DJANGO\_SECRET\_KEY key stated here serve just as examples and
should not be used anywhere outside of the local development. For a
production environment, the secret key should never be visible to the
outside world and can be generated with tools like:
https://www.miniwebtool.com/django-secret-key-generator/

These environment variables are read in the settings.py module which
configures the database.

Packages
--------

The website uses following python packages which are automatically
installed on deployment:

-  **django**: The most important package. The whole website is built
   with it.
-  **django-allauth**: Implements the CERN OAuth2 SSO Provider
-  **django-bootstrap3**: Easy Integration of the bootstrap frontend
-  **django-categories**: Easy creation of Categories (and
   Subcategories)
-  **django-ckeditor**: HTML Text editor to edit Checklist items
-  **django-dynamic-preferences**: Easily create preferences in the
   Admin Settings. Used to configure the shift leader popup message.
-  **django-filter**: Filter the certified runs
-  **django-nested-admin**: Makes it possible to inline multiple
   hierarchies in the admin panel. Used to inline checklist items in
   checklist groups in checklists
-  **django-tables2**: Display Tables
-  **django-widget-tweaks**: Convenient Template Tags
-  **psycopg2-binary**: Necessary to use PostgreSQL
-  **terminaltables**: Used to generate the shifters daily summary
   report
-  **whitenoise**: static files provider. Necessary for deploying the
   website without debug mode enabled.

The *requirements.txt* should always be updated when adding new
packages.

Testing Packages
~~~~~~~~~~~~~~~~

-  **pytest**: The Advantage of pytest is that unit tests can be written
   very shortly. pytest also provides a nice colored output when running
   unit tests Pytest also immediatly shows what's wrong rather than only
   seeing that something is wrong.
-  **pytest-cov**: Create coverage reports when running pytest
-  **pytest-django**: easy Django integration for pytest
-  **mixer**: Fast and convenient way of creating model instances for
   unit tests
-  **selenium**: Necessary to run functional tests (with firefox)

All packages that are used in a testing environment should be stated in
the *testing-requirements.txt* file.

Branches
--------

Master
~~~~~~

The master branch is the production branch. It is used to deploy to
tkdqmdoctor.web.cern.ch via OpenShift. This branch should only contain
stable and tested code. Changes should never be made directly in the
master branch.

Develop
~~~~~~~

Development branch to test new features before deploying it to the
production website. Commits in the development branch are automatically
deployed to dev-tkdqmdoctor.web.cern.ch every time changes are pushed to
GitHub.

.. code:: bash

    git push origin develop

When a develop branch is thoroughly tested and ready for production then
it can be merged into the master branch:

.. code:: bash

    git checkout master
    git merge develop
    git push origin master

Feature branches
~~~~~~~~~~~~~~~~

When developing new features, a new feature branch should be created.

.. code:: bash

    git checkout -b feature-mynewfeature develop

After the new changes have been committed, they can be merged back into
the develop branch.

.. code:: bash

    git checkout develop
    git merge my-new-feature
    git branch -d my-new-feature
    git push origin develop

The push to the development branch automatically triggers the unit tests
at Travis CI.

Django Tutorial
---------------

It is recommended to the finish the Django tutorial at
https://docs.djangoproject.com/en/1.11/intro/tutorial01/ before doing
any changes at the website. The tutorial is beneficial and gives a big
overview of how Django works.

Style Guide
-----------

To improve readability of the source code, a consistent style guide
should be used. The python files are all formatted with the Black Code
Formatter

The black code formatter can be installed on the local machine via

.. code:: bash

    pip install black

The project files can then be reformated with

.. code:: bash

    black [FILES...]


Run the website locally
-----------------------

TODO runserver

Migrations
----------

Whenever you make changes to ``models.py`` you should run the ``makemigrations`` command.

.. code:: bash

    python manage.py makemigrations

The migrations can then be applied with:

.. code:: bash

    python manage.py migrate


PyCharm
-------

- TODO how to setup project
- TODO how to run project
- TODO testing

Documentation
-------------

If you want to contribute to the documentation that is hosted at
`readthedocs`_ you should get familiar with Spinx and reStructedText

-  https://docs.readthedocs.io/en/latest/intro/getting-started-with-sphinx.html
-  http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

To generate a local documentation these commands have to be run:

.. code:: bash

   pip install sphinx
   cd docs
   make html

After that you can open the ``index.html`` file that is located at
``docs/_build/html``.

.. _readthedocs: https://tkdqmdoctor.readthedocs.io/en/latest/
