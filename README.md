# beans_logging

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bybatkhuu/module-python-logging/2.build-publish.yml?logo=GitHub)](https://github.com/bybatkhuu/module-python-logging/actions/workflows/2.build-publish.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bybatkhuu/module-python-logging?logo=GitHub)](https://github.com/bybatkhuu/module-python-logging/releases)
[![PyPI](https://img.shields.io/pypi/v/beans-logging?logo=PyPi)](https://pypi.org/project/beans-logging)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beans-logging?logo=Python)](https://docs.conda.io/en/latest/miniconda.html)

`beans_logging` is a python package for simple logger and easily managing logging modules.

It is a `Loguru` based custom logging package for python projects.

## Features

- Main **logger** based on **Loguru** logging - <https://pypi.org/project/loguru>
- Logging to **log files** (all, error, json)
- **Pre-defined** logging configs and handlers
- **Colorful** logging
- Auto **intercepting** and **muting** modules
- Load config from **YAML** or **JSON** file
- Custom options as a **config**
- Custom logging **formats**
- **Multiprocess** compatibility (Linux, macOS - 'fork')
- Add custom **handlers**
- **Base** logging module
- Support **Pydantic-v1** and **Pydantic-v2**

---

## Installation

### 1. Prerequisites

- **Python (>= v3.8)**
- **PyPi (>= v23)**

### 2. Install beans-logging package

Choose one of the following methods to install the package **[A ~ F]**:

**A.** [**RECOMMENDED**] Install from **PyPi**

```sh
# Install or upgrade beans-logging package:
pip install -U beans-logging
```

**B.** Install latest version from **GitHub**

```sh
# Install package by git:
pip install git+https://github.com/bybatkhuu/module-python-logging.git
```

**C.** Install from **pre-built release** files

1. Download **`.whl`** or **`.tar.gz`** file from **releases** - <https://github.com/bybatkhuu/module-python-logging/releases>
2. Install with pip:

```sh
# Install from .whl file:
pip install ./beans_logging-[VERSION]-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./beans_logging-[VERSION].tar.gz
```

**D.** Install from **source code** by building package

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module-python-logging.git beans_logging
cd ./beans_logging

# Install python build tool:
pip install -U pip build

# Build python package:
python -m build

_VERSION=$(./scripts/get-version.sh)

# Install from .whl file:
pip install ./dist/beans_logging-${_VERSION}-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./dist/beans_logging-${_VERSION}.tar.gz
```

**E.** Install with pip editable **development mode** (from source code)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module-python-logging.git beans_logging
cd ./beans_logging

# Install with editable development mode:
pip install -e .
```

**F.** Manually add to **PYTHONPATH** (not recommended)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module-python-logging.git beans_logging
cd ./beans_logging

# Install python dependencies:
pip install -r ./requirements.txt

# Add current path to PYTHONPATH:
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## Usage/Examples

To use `beans_logging`, import the `logger` instance from the `beans_logging.auto` package:

```python
from beans_logging.auto import logger
```

You can call logging methods directly from the `logger` instance:

```python
logger.info("Logging info.")
```

### **Simple**

[**`configs/logger.yml`**](https://github.com/bybatkhuu/module-python-logging/blob/main/examples/simple/configs/logger.yml):

```yml
logger:
  app_name: "my-app"
  level: "TRACE"
  file:
    log_handlers:
      enabled: true
    json_handlers:
      enabled: true
```

[**`main.py`**](https://github.com/bybatkhuu/module-python-logging/blob/main/examples/simple/main.py):

```python
from beans_logging.auto import logger


logger.trace("Tracing...")
logger.debug("Debugging...")
logger.info("Logging info.")
logger.success("Success.")
logger.warning("Warning something.")
logger.error("Error occured.")
logger.critical("CRITICAL ERROR.")

def divide(a, b):
    _result = a / b
    return _result

def nested(c):
    try:
        divide(5, c)
    except ZeroDivisionError as err:
        logger.error(err)
        raise

try:
    nested(0)
except Exception as err:
    logger.exception("Show me, what value is wrong:")
```

Run the [**`examples/simple`**](https://github.com/bybatkhuu/module-python-logging/tree/main/examples/simple):

```sh
cd ./examples/simple

python ./main.py
```

**Output**:

```txt
[2023-09-01 00:00:00.000 +09:00 | TRACE | beans_logging._base:478]: Intercepted modules: ['concurrent', 'concurrent.futures', 'asyncio']; Muted modules: [];
[2023-09-01 00:00:00.000 +09:00 | TRACE | __main__:7]: Tracing...
[2023-09-01 00:00:00.000 +09:00 | DEBUG | __main__:8]: Debugging...
[2023-09-01 00:00:00.000 +09:00 | INFO  | __main__:9]: Logging info.
[2023-09-01 00:00:00.000 +09:00 | OK    | __main__:10]: Success.
[2023-09-01 00:00:00.000 +09:00 | WARN  | __main__:11]: Warning something.
[2023-09-01 00:00:00.000 +09:00 | ERROR | __main__:12]: Error occured.
[2023-09-01 00:00:00.000 +09:00 | CRIT  | __main__:13]: CRITICAL ERROR.
[2023-09-01 00:00:00.000 +09:00 | ERROR | __main__:25]: division by zero
[2023-09-01 00:00:00.000 +09:00 | ERROR | __main__:32]: Show me, what value is wrong:
Traceback (most recent call last):

> File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 30, in <module>
    nested(0)
    └ <function nested at 0x10802a4c0>

  File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 23, in nested
    divide(5, c)
    │         └ 0
    └ <function divide at 0x1052f31f0>

  File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 17, in divide
    _result = a / b
              │   └ 0
              └ 5

ZeroDivisionError: division by zero
```

### **FastAPI**

Checkout `beans_logging_fastapi` package: <https://github.com/bybatkhuu/module.fastapi-logging>

- FastAPI HTTP access logging middleware
- Install with pip: `pip install -U beans-logging-fastapi`

---

## Running Tests

To run tests, run the following command:

```sh
# Install python test dependencies:
pip install -r ./requirements.test.txt

# Run tests:
python -m pytest -v
```

## Environment Variables

You can use the following environment variables inside [**`.env.example`**](https://github.com/bybatkhuu/module-python-logging/blob/main/.env.example) file:

```sh
ENV=development
DEBUG=true

BEANS_LOGGING_DISABLE_DEFAULT=false
BEANS_LOGGING_CONFIG_PATH="./configs/logger.yml"
BEANS_LOGGING_LOGS_DIR="./logs"
```

## Configuration

You can use the following configuration template [**`logger.yml`**](https://github.com/bybatkhuu/module-python-logging/blob/main/templates/configs/logger.yml): file:

```yaml
logger:
  # app_name: "app"
  level: "INFO"
  use_diagnose: false
  stream:
    use_color: true
    use_icon: false
    format_str: "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>"
    std_handler:
      enabled: true
  file:
    logs_dir: "./logs"
    rotate_size: 10000000 # 10MB
    rotate_time: "00:00:00"
    backup_count: 90
    log_handlers:
      enabled: false
      format_str: "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}"
      log_path: "{app_name}.std.all.log"
      err_path: "{app_name}.std.err.log"
    json_handlers:
      enabled: false
      use_custom: false
      log_path: "{app_name}.json.all.log"
      err_path: "{app_name}.json.err.log"
  intercept:
    auto_load:
      enabled: true
      only_base: false
      ignore_modules: []
    include_modules: []
    mute_modules: []
  extra:
```

## Documentation

- [docs](https://github.com/bybatkhuu/module-python-logging/blob/main/docs/README.md)
- [scripts](https://github.com/bybatkhuu/module-python-logging/blob/main/docs/scripts/README.md)

---

## References

- <https://github.com/Delgan/loguru>
- <https://loguru.readthedocs.io/en/stable/api/logger.html>
- <https://loguru.readthedocs.io/en/stable/resources/recipes.html>
- <https://github.com/bybatkhuu/module.fastapi-logging>
