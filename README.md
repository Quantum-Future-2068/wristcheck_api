# wristcheck_api

这是使用Django搭建的restful API项目, 目前用于给小程序和CMS后台提供必要的接口

## 1.Requirements

- [Python 3.12.0](https://www.python.org/)
- [Django 5.0.6](https://www.djangoproject.com/)
- [djangorestframework 3.15.1](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/)

具体依赖包请查看: `requirements.txt`文件


## 2.Environment management

使用[python-dotenv](https://github.com/theskumar/python-dotenv)

项目的根目录有一个名为`env_template`的文件, 项目默认从项目根目录的`.env`文件获取变量. 
所以, 我们拷贝一份

```shell
cp env_template .env
```

然后在`.env`文件更改, 以DEBUG变量为例:

```
DEBUG=True
```

在项目代码中使用变量

```python
import os
from dotenv import load_dotenv
load_dotenv(override=True)
DEBUG = bool(os.getenv("DEBUG"))
```

## 3.Quickstart

### 1.创建虚拟环境

```shell
pip3 install virtualenv
virtualenv -p python3 .venv
```

### 2.进入虚拟环境

```shell
source .venv/bin/activate 
```

### 3.安装依赖包

```shell
pip install -r requirements.txt
```

### 4.执行migrations文件

用于在.env环境变量配置文件中指定的数据库中创建表结构

```shell
python manage.py migrate
```

### 5.创建super user

需要输入username, password, email

```shell
python manage.py createsuperuser
```

### 6.启动项目

本地启动(端口可自定义)

```shell
python manage.py runserver 127.0.0.1:8000
```

可以访问

- [admin后台](https://1a83-2408-824e-1514-9830-189d-8641-287f-5df2.ngrok-free.app/admin/)
- [DRF交互文档](https://1a83-2408-824e-1514-9830-189d-8641-287f-5df2.ngrok-free.app/)
- [swagger交互文档](https://1a83-2408-824e-1514-9830-189d-8641-287f-5df2.ngrok-free.app/doc/swagger/#/)
- [redoc文档](https://1a83-2408-824e-1514-9830-189d-8641-287f-5df2.ngrok-free.app/doc/redoc/)

