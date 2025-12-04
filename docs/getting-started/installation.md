---
title: Installation
---

# 🛠 Installation

## 📦 Install the package

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
