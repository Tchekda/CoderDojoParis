#!/bin/sh
sh heroku-deploy.sh
heroku pg:reset DATABASE --confirm tchekda-coderdojoparis
