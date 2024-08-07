#!/bin/sh
python manage.py makemigrations && python manage.py migrate
python manage.py collectstatic --noinput
which supervisord
#cp /app/supervisor.conf /etc/supervisor/conf.d/supervisord.conf
exec /usr/local/bin/supervisord -n -c /app/supervisor.conf