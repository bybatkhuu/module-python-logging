# Python Logging (beans-logging)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bybatkhuu/module-python-logging/2.build-publish.yml?logo=GitHub)](https://github.com/bybatkhuu/module-python-logging/actions/workflows/2.build-publish.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bybatkhuu/module-python-logging?logo=GitHub&color=blue)](https://github.com/bybatkhuu/module-python-logging/releases)
[![PyPI](https://img.shields.io/pypi/v/beans-logging?logo=PyPi)](https://pypi.org/project/beans-logging)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beans-logging?logo=Python)](https://docs.conda.io/en/latest/miniconda.html)

`beans-logging` is a python package for simple logger and easily managing logs.

It is a `Loguru` based custom logging package for python projects.

## ✨ Features

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

---

## 🛠 Installation

### 1. 🚧 Prerequisites

- Install **Python (>= v3.10)** and **pip (>= 23)**:
    - **[RECOMMENDED] [Miniconda (v3)](https://www.anaconda.com/docs/getting-started/miniconda/install)**
    - *[arm64/aarch64] [Miniforge (v3)](https://github.com/conda-forge/miniforge)*
    - *[Python virutal environment] [venv](https://docs.python.org/3/library/venv.html)*

[OPTIONAL] For **DEVELOPMENT** environment:

- Install [**git**](https://git-scm.com/downloads)
- Setup an [**SSH key**](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)

### 2. 📥 Download or clone the repository

[TIP] Skip this step, if you're going to install the package directly from **PyPi** or **GitHub** repository.

**2.1.** Prepare projects directory (if not exists):

```sh
# Create projects directory:
mkdir -pv ~/workspaces/projects

# Enter into projects directory:
cd ~/workspaces/projects
```

**2.2.** Follow one of the below options **[A]**, **[B]** or **[C]**:

**OPTION A.** Clone the repository:

```sh
git clone https://github.com/bybatkhuu/module-python-logging.git && \
    cd module-python-logging
```

**OPTION B.** Clone the repository (for **DEVELOPMENT**: git + ssh key):

```sh
git clone git@github.com:bybatkhuu/module-python-logging.git && \
    cd module-python-logging
```

**OPTION C.** Download source code:

1. Download archived **zip** file from [**releases**](https://github.com/bybatkhuu/module-python-logging/releases).
2. Extract it into the projects directory.

### 3. 📦 Install the package

[NOTE] Choose one of the following methods to install the package **[A ~ F]**:

**OPTION A.** [**RECOMMENDED**] Install from **PyPi**:

```sh
pip install -U beans-logging
```

**OPTION B.** Install latest version directly from **GitHub** repository:

```sh
pip install git+https://github.com/bybatkhuu/module-python-logging.git
```

**OPTION C.** Install from the downloaded **source code**:

```sh
# Install directly from the source code:
pip install .

# Or install with editable mode:
pip install -e .
```

**OPTION D.** Install for **DEVELOPMENT** environment:

```sh
pip install -e .[dev]

# Install pre-commit hooks:
pre-commit install
```

**OPTION E.** Install from **pre-built release** files:

1. Download **`.whl`** or **`.tar.gz`** file from [**releases**](https://github.com/bybatkhuu/module-python-logging/releases)
2. Install with pip:

```sh
# Install from .whl file:
pip install ./beans_logging-[VERSION]-py3-none-any.whl

# Or install from .tar.gz file:
pip install ./beans_logging-[VERSION].tar.gz
```

**OPTION F.** Copy the **module** into the project directory (for **testing**):

```sh
# Install python dependencies:
pip install -r ./requirements.txt

# Copy the module source code into the project:
cp -r ./src/beans_logging [PROJECT_DIR]
# For example:
cp -r ./src/beans_logging /some/path/project/
```

## 🚸 Usage/Examples

To use `beans_logging`, import the `logger` instance from the `beans_logging.auto` package:

```python
from beans_logging.auto import logger
```

You can call logging methods directly from the `logger` instance:

```python
logger.info("Logging info.")
```

### **Simple**

[**`configs/logger.yml`**](./examples/simple/configs/logger.yml):

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

[**`main.py`**](./examples/simple/main.py):

```python
#!/usr/bin/env python

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
except Exception:
    logger.exception("Show me, what value is wrong:")
```

Run the [**`examples/simple`**](./examples/simple):

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

👍

---

## ⚙️ Configuration

[**`templates/configs/logger.yml`**](./templates/configs/logger.yml):

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

### 🌎 Environment Variables

[**`.env.example`**](./.env.example):

```sh
# ENV=LOCAL
# DEBUG=false
# TZ=UTC

# BEANS_LOGGING_DISABLE_DEFAULT=false
# BEANS_LOGGING_CONFIG_PATH="./configs/logger.yml"
# BEANS_LOGGING_LOGS_DIR="./logs"
```

---

## 🧪 Running Tests

To run tests, run the following command:

```sh
# Install python test dependencies:
pip install .[test]

# Run tests:
python -m pytest -sv -o log_cli=true
# Or use the test script:
./scripts/test.sh -l -v -c
```

## 🏗️ Build Package

To build the python package, run the following command:

```sh
# Install python build dependencies:
pip install -r ./requirements/requirements.build.txt

# Build python package:
python -m build
# Or use the build script:
./scripts/build.sh
```

## 📝 Generate Docs

To build the documentation, run the following command:

```sh
# Install python documentation dependencies:
pip install -r ./requirements/requirements.docs.txt

# Serve documentation locally (for development):
mkdocs serve -a 0.0.0.0:8000
# Or use the docs script:
./scripts/docs.sh

# Or build documentation:
mkdocs build
# Or use the docs script:
./scripts/docs.sh -b
```

## 📚 Documentation

- [Docs](./docs)

---

## 📑 References

- <https://github.com/Delgan/loguru>
- <https://loguru.readthedocs.io/en/stable/api/logger.html>
- <https://loguru.readthedocs.io/en/stable/resources/recipes.html>
- <https://docs.python.org/3/library/logging.html>
- <https://github.com/bybatkhuu/module-fastapi-logging>
