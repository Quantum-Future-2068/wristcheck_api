.PHONY: run
SHELL = /bin/bash

ifneq (,$(wildcard .env))
    include .env
    export
endif

PORT ?= 8000
PROJECT_NAME ?= wristcheck_api
APP_NAME ?= account
VIRTUALENVS ?= source .venv/bin/activate
WORKERS = 4
HOST = 0.0.0.0
PID_FILE=gunicorn.pid

create_venv:
	virtualenv -p python3 .venv

install: create_venv
	${VIRTUALENVS} && pip install -r requirements.txt

migrate: install
	${VIRTUALENVS} && python manage.py makemigrations && python manage.py migrate

collectstatic:
	${VIRTUALENVS} && python manage.py collectstatic

config_env:
	cp env_template .env

pytest: config_env
	${VIRTUALENVS} && pytest

run_local: migrate
	${VIRTUALENVS} && python manage.py runserver 127.0.0.1:$(PORT)

start_gunicorn: migrate
	${VIRTUALENVS} && gunicorn --workers ${WORKERS} --bind $(HOST):$(PORT) ${PROJECT_NAME}.wsgi --pid $(PID_FILE) --daemon

process:
	ps aux | grep gunicorn

stop_gunicorn:
	pkill -f gunicorn

black:
	${VIRTUALENVS} && black .

black_check:
	${VIRTUALENVS} && black --check .

# local, if exists

-include Makefile.local
