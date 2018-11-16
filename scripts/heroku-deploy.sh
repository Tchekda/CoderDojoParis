#!/bin/sh
python manage.py collectstatic -l --noinput
python manage.py makemigrations Core Homepage Dashboard
python manage.py migrate Core Homepage Dashboard
python manage.py test -v2
