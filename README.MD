[![Build Status](https://travis-ci.com/CMSTrackerDPG/TkDQMDoctor.svg?branch=master)](https://travis-ci.com/CMSTrackerDPG/TkDQMDoctor)
[![Build Status](https://travis-ci.com/CMSTrackerDPG/TkDQMDoctor.svg?branch=develop)](https://travis-ci.com/CMSTrackerDPG/TkDQMDoctor)
[![codecov](https://codecov.io/gh/CMSTrackerDPG/TkDQMDoctor/branch/master/graph/badge.svg)](https://codecov.io/gh/CMSTrackerDPG/TkDQMDoctor)
[![Documentation Status](https://readthedocs.org/projects/tkdqmdoctor/badge/?version=latest)](https://tkdqmdoctor.readthedocs.io/en/latest/?badge=latest)

# TkDQMDoctor

## Prerequisits

- python (version 3.5 or 3.6)
- git 

## Set up your environment

```bash
git clone https://github.com/CMSTrackerDPG/TkDQMDoctor
cd TkDQMDoctor    
python3 -m venv venv
source venv/bin/active
pip install -r requirements.txt
pip install -r testing-requirements.txt
```

## Environment variables
Create a ```.env``` file with the following content:

```bash
DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3
DJANGO_DEBUG=True
DJANGO_DATABASE_NAME=db.sqlite3
DJANGO_SECRET_KEY=(%g65bg+&9rbnt+h&txlxw$+lkq=g=yrp!6@v+7@&$a%9^yt-!
```

*Note: your secret key should differ and never be made public.*

## Run website locally

Setup your local database

```bash
python manage.py migrate
python manage.py createsuperuser
```

Run the website

```bash
python manage.py runserver
```

Then the website can be visited at [http://localhost:8000](http://localhost:8000)

## Recommended reading

### Django tutorial

Before you participate in this project, it is recommended to do the Django tutorial first. 
It gives you a quick overview of most of the things you need to know.

- https://docs.djangoproject.com/en/1.11/intro/

### Documentation

A documentation about the TkDQMDoctor can be found in the folder ```docs``` or at [readthedocs](https://tkdqmdoctor.readthedocs.io/en/latest/). It contains both a user manual and a more detailed development manual.

- https://tkdqmdoctor.readthedocs.io/en/latest/

### Shift Instructions

Shift instructions can be found on the Twiki pages:

- [https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackerOfflineShiftInstructions](https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackerOfflineShiftInstructions)

Instructions for the shift leader can be found under:

- [https://twiki.cern.ch/twiki/bin/view/CMS/TrackerOfflineShiftLeaderInstructions](https://twiki.cern.ch/twiki/bin/view/CMS/TrackerOfflineShiftLeaderInstructions)
