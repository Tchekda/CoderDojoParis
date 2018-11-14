#!/bin/sh
python manage.py collectstatic -l --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py test -v2
