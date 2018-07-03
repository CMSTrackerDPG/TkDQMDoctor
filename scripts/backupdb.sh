#!/bin/bash

# TODO option without filename
# TODO pass envfilename

backupfilename="db-$(date +"%Y-%m-%d-%H%M%S").json"
envfilename="develop.env"

if [ -f "${envfilename}" ]; then
    echo -e "Exporting environment variables from ${envfilename}..."
    expenv "${envfilename}"
    echo -e "Creating backup..."
    python manage.py dumpdata --exclude socialaccount.socialapp --exclude socialaccount.socialtoken --exclude auth.permission --exclude contenttypes --indent 2 > "${backupfilename}"
    if [ -f "${backupfilename}" ]; then
        echo -e "\e[39m Created \e[34m${backupfilename}"
        echo -e "\e[92m==BACKUP SUCCESSFULL=="
    else
        echo -e "\e[31==BACKUP FAILED=="
    fi
else
    echo -e "\e[31mError: ${envfilename} does not exist!\e[39m"
    echo -e "Please create a develop.env file containing the credentials to the database"
fi
