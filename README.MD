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

# Deploy from jandreadesktop.cern.ch
* ssh cernLogin@jandreadesktop.cern.ch
* cd /home/jandrea/tkDQMDoctor/TkDQMDoctor
* screen -r    (check for running sessions)
* python3 manage.py runserver 128.141.84.249:8000

If you want to keep the server running after you exit your session use 

* screen
* python3 manage.py runserver 128.141.84.249:8000
* "Ctrl-a" "d"    (to deteach from the window)
* The process is now running detached and you can quit the session without killing the process

# When you change the database

## Changes in models: How to update the database

* python3 manage.py makemigrations
* python3 manage.py migrate

This will update the database for you.
This does not mean that you should not check the terminal output telling you how the table was altered.

## How to create the database from scratch

* rm db.sqlite3
* rm -rf certhelper/migrations
* python3 manage.py makemigrations certhelper
* python3 manage.py migrate

# Other stuff

## Tutorials
This tutorial takes about 4 hours to do. If you follow along it will explain a lot of the structure used in this project.
It is highly recommended to at least think through it.

Start here:

* https://docs.djangoproject.com/en/1.11/intro/tutorial01/