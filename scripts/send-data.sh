#!/bin/sh
python manage.py dumpdata > data.json
git add data.json
git commit -m "Added data"
heroku pg:reset DATABASE --confirm tchekda-coderdojoparis
git push heroku master -f
git reset --soft HEAD^
git reset HEAD data.json
git push origin master -f
heroku run python manage.py makemigrations
heroku run python manage.py migrate
heroku run python manage.py loaddata data.json
rm -fv data.json
