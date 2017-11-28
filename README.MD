# How to develop locally

## Get all the requirements 
* python3
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
