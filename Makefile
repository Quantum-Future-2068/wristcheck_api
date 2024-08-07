.PHONY: run
SHELL = /bin/bash

ifneq (,$(wildcard .env))
    include .env
    export
endif

PORT ?= 8000
PROJECT_NAME ?= wristcheck_api
APP_NAME ?= account
WORKERS = 4
HOST = 0.0.0.0
PID_FILE=gunicorn.pid

config_env:
	cp env_template .env

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations && python manage.py migrate

collectstatic:
	python manage.py collectstatic --noinput

pytest:
	pytest

run_local: migrate
	python manage.py runserver 127.0.0.1:$(PORT)

start_gunicorn:
	gunicorn -c gunicorn_config.py

stop_gunicorn:
	pkill -f gunicorn

stop:
	supervisorctl stop wristcheck

start:
	supervisorctl start wristcheck

restart:
	supervisorctl restart wristcheck

# local, if exists

-include Makefile.local
