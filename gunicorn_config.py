import multiprocessing

from environs import Env

env = Env()
env.read_env(override=False)

bind = f'{env.str("HOST", "0.0.0.0")}:{env.str("PORT", 80)}'
workers = env.int("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
threads = 1
timeout = 30
worker_class = "sync"
daemon = False
wsgi_app = "wristcheck_api.wsgi:application"
preload_app = True
proc_name = "wristcheck_api"
loglevel = env.str("GUNICORN_LOG_LEVEL", "debug")
accesslog = env.str("GUNICORN_ACCESS_LOG", "/var/log/gunicorn_access.log")
errorlog = env.str("GUNICORN_ERROR_LOG", "/var/log/gunicorn_error.log")
