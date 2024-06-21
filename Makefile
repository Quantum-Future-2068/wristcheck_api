.PHONY: run
SHELL = /bin/bash

PORT ?= 8000
PROJECT_NAME ?= wristcheck_api
APP_NAME ?= account
VIRTUALENVS ?= source .venv/bin/activate
WORKERS = 4
HOST = 0.0.0.0

pull:
	git pull 

install: pull 
	${VIRTUALENVS} && pip install -r requirements.txt

migrate: install
	${VIRTUALENVS} && python manage.py makemigrations && python manage.py migrate

collectstatic:
	${VIRTUALENVS} && python manage.py collectstatic

pytest:
	${VIRTUALENVS} && pytest

run_local: migrate
	${VIRTUALENVS} && python manage.py runserver 127.0.0.1:$(PORT)

run_gunicorn: migrate
	${VIRTUALENVS} && gunicorn --workers ${WORKERS} --bind $(HOST):$(PORT) ${PROJECT_NAME}.wsgi --daemon

run_gunicorn_only:
	${VIRTUALENVS} && gunicorn --workers ${WORKERS} --bind $(HOST):$(PORT) ${PROJECT_NAME}.wsgi --daemon

process:
	ps aux | grep gunicorn | grep -v grep

stop_gunicorn:
	pkill -f gunicorn

restart_gunicorn:
	pkill -HUP -f gunicorn

black:
	${VIRTUALENVS} && black $$(git ls-files '*.py')

# local, if exists

-include Makefile.local
