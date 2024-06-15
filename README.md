# wristcheck_api

## Environment variable

使用python-decouple==3.8
从项目根目录的.env文件获取变量

### how to use?

.env 文件内容

```
DEBUG=True
```

```python
from decouple import config
DEBUG = config('DEBUG', default=True, cast=bool)
```
