# wristcheck_api

这是使用Django搭建的restful API项目, 目前用于给小程序和CMS后台提供必要的接口

接口风格, 示例:

- 获取所有用户：GET /api/user/
- 创建新用户：POST /api/user/
- 获取单个用户：GET /api/user/{id}/
- 更新用户：PUT /api/user/{id}/
- 删除用户：DELETE /api/user/{id}/

## 1.Requirements

- [Python 3.12.0](https://www.python.org/)
- [Django 5.0.6](https://www.djangoproject.com/)
- [djangorestframework 3.15.1](https://www.django-rest-framework.org/)

具体依赖包请查看: `requirements.txt`文件


## 2.Environment management

使用[python-decouple](https://github.com/HBNetwork/python-decouple)

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
from decouple import config
DEBUG = config('DEBUG', default=True, cast=bool)
```

## 3.Quickstart

### 1.创建虚拟环境

```shell
virtualenv -p python3.12 .venv
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

此时, 可以访问[API文档登录](http://127.0.0.1:8000/drf-admin/)

这里是为Wristcheck的微信小程序提供的API接口文档：
- Api Root列出了资源对象和其API地址的映射关系，默认提供了对象的CRUD接口。
- 点击资源对象的API地址，会跳转到资源的管理界面。如果资源对象开放了create、update、delete请求，那么在这里可以进行请求。
- 自定义的接口在右上角的Extra Actions中。
