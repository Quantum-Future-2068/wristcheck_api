import multiprocessing

from environs import Env

env = Env()
env.read_env(override=False)

bind = f'{env.str("HOST", "0.0.0.0")}:{env.str("API_PORT", 8888)}'
workers = env.int("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
threads = 1
timeout = 30
worker_class = "sync"
daemon = False
wsgi_app = "wristcheck_api.wsgi:application"
preload_app = True
proc_name = "wristcheck_api"
accesslog = "-"  # 将访问日志输出到标准输出
errorlog = "-"  # 将错误日志输出到标准错误
loglevel = "info"  # 设置日志级别
