# wristcheck_api

Provide Rest API for mini-programs and dashboard

## Requirements

- [Python 3.x](https://www.python.org/)

- [Django 5.0.6](https://www.djangoproject.com/)

- [djangorestframework 3.15.1](https://www.django-rest-framework.org/)

- [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/)

## Quickstart

### 1. Create a virtual environment

```shell
pip3 install virtualenv
virtualenv -p python3 .venv
```

### 2. Enter the virtual environment

```shell
source .venv/bin/activate
```

### 3. Install dependency packages

```shell
pip install -r requirements.txt
```

### 4. Execute the migrations file

Used to create the table structure in the database specified in the .env environment variable configuration file

```shell
python manage.py migrate
```

### 5. Create a super user

You need to enter username, password, email

```shell
python manage.py createsuperuser
```

### 6. Start the project

Local startup (port can be customized)

```shell
python manage.py runserver 127.0.0.1:8888
```

You can access

- [admin backend](http://127.0.0.1:8888/admin/)

- [DRF interaction document](http://127.0.0.1:8888/)

- [swagger interaction document](http://127.0.0.1:8888/doc/swagger/#/)

- [redoc documentation](http://127.0.0.1:8888/doc/redoc/)