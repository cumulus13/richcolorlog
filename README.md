# 🌈 **richcolorlog** – Beautiful, Powerful & Multi-Output Logging for Python

> ✨ **Log like a pro** with emoji icons, syntax highlighting, custom log levels, and support for **console, file, RabbitMQ, Kafka, ZeroMQ, Syslog, and databases** — all in one package!

[![PyPI version](https://img.shields.io/pypi/v/richcolorlog.svg?color=blue&logo=pypi)](https://pypi.org/project/richcolorlog/)
[![Python Versions](https://img.shields.io/pypi/pyversions/richcolorlog.svg?logo=python)](https://pypi.org/project/richcolorlog/)
[![License](https://img.shields.io/github/license/cumulus13/richcolorlog?color=green)](https://github.com/cumulus13/richcolorlog/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/richcolorlog)](https://pepy.tech/project/richcolorlog)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://richcolorlog.readthedocs.io/)


[![Screenshot](https://raw.githubusercontent.com/cumulus13/richcolorlog/master/screenshot.png)](https://raw.githubusercontent.com/cumulus13/richcolorlog/master/screenshot.png)

---

## 🚀 Features

- ✅ **Rich Console Output** with colors, backgrounds, and **emoji icons** per log level  
- 🎨 **Syntax Highlighting** for code snippets (Python, SQL, JSON, etc.) via `lexer='python'`  
- 🎯 **Custom Log Levels**: `EMERGENCY`, `ALERT`, `NOTICE`, `FATAL` (Syslog-compliant)  
- 📦 **Multi-Handler Support**:  
  - 🖥️ Console (Rich + ANSI fallback)  
  - 📄 File (with level-based formatting)  
  - 🐇 RabbitMQ  
  - 📡 Kafka  
  - 📡 ZeroMQ  
  - 📡 Syslog  
  - 🗄️ PostgreSQL / MySQL / MariaDB / SQLite  

- 🧪 **Jupyter/IPython Friendly** (no async warnings!)  
- 🧩 **Full LogRecord Template Support**: `%(asctime)s`, `%(funcName)s`, `%(threadName)s`, `%(icon)s`, etc.  
- 🔁 **Smart Timestamp**: Repeated timestamps are hidden (like `RichHandler` original)
- 🎨 **Custom Colors**: Set color per level (`info_color`, `error_color`, etc.)
- ⚙️ **Highly Configurable**: `icon_first`, `level_in_message`, `show_background`, etc.  
- 🚀 **Easy to use** - Simple setup with sensible defaults
- ⚡ **Zero required dependencies** (only `rich` for Rich mode; brokers optional)
- 🎨 **Support any terminal** - with ansi color Fallback

---

## 📦 Installation

Install from PyPI:

```bash
pip install richcolorlog
```

> 💡 **Optional**: Install extras for message brokers:
> ```bash
> pip install richcolorlog[rabbitmq,kafka,zmq,db]
> ```

Or install from source:

```bash
git clone https://github.com/cumulus13/richcolorlog
cd richcolorlog
pip install -e .
```

---

## Documentations

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://richcolorlog.readthedocs.io/)

## 🧪 Quick Start

### Basic Usage (Rich Console)

```python
>>> from richcolorlog import setup_logging

>>> logger = setup_logging(
        name="myapp",
        show_background=True,
        show_icon=True,
        icon_first=True
    )
>>> logger.emergency("This is an emergency message")
    logger.alert("This is an alert message")
    logger.critical("This is a critical message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.info("This is an info message")
    logger.debug("This is a debug message")
>>> # output
    🆘 [10/04/25 14:12:07] EMERGENCY This is an emergency message
    🚨 [10/04/25 14:12:07] ALERT    This is an alert message
    💥 [10/04/25 14:12:07] CRITICAL This is a critical message
    ❌ [10/04/25 14:12:07] ERROR    This is an error message
    ⛔ [10/04/25 14:12:07] WARNING  This is a warning message
    📢 [10/04/25 14:12:07] NOTICE   This is a notice message
    🔔 [10/04/25 14:12:07] INFO     This is an info message
    🐛 [10/04/25 14:12:07] DEBUG    This is a debug message

>>> FORMAT = "%(icon)s %(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
>>> logger = setup_logging(show_background=True, format_template=FORMAT, name="TEST")
>>> code = """
    def hello():
        print("Hello World")
    """
>>> logger.info(code, lexer='python')
>>> #output
    🔔 [10/04/25 15:12:34] TEST 15448 INFO

    def hello():
        print("Hello World")

>>> logger.debug("SELECT * FROM users", lexer="sql")  # Syntax highlighted!
>>> #output
    🐛 [10/04/25 15:12:35] TEST 15448 DEBUG                                
    SELECT * FROM users

```

### With Custom Format Template

```python
template = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s() | %(message)s"

logger = setup_logging(
    name="api",
    format_template=template,
    show_background=False
)

logger.notice("User logged in successfully 🔑")
```

### Custom Format Template + Icon in Template

```python
FORMAT = "%(icon)s %(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

logger = setup_logging(
    name="TEST",
    format_template=FORMAT,
    icon_first=True,           # Icon always at start (overrides template position)
    omit_repeated_times=True   # Hide repeated timestamps
)

logger.info("Hello world")
# Output:
# 🔔 [10/06/25 15:30:00] INFO - Hello world (test.py:10)
# 🔔                     INFO - Another message (test.py:11)
```

### Show Level in Message (`level_in_message=True`)

```python
logger = setup_logging(level_in_message=True)
logger.info("This is a message")
# Output: INFO - This is a message
```

### Simple Logger (No Rich, for Jupyter)

```python
from richcolorlog import setup_logging_custom

logger = setup_logging_custom(
    name="notebook",
    show_icon=True,
    icon_first=False,
    show_background=False
)

logger.info("Running analysis in Jupyter 📊")
```

---

## 🎯 Advanced Examples

### 🔌 Send Logs to Kafka & File Logging

```python
logger = setup_logging(
    name="producer",
    log_file=True,
    log_file_name="app.log",
    kafka=True,
    kafka_host="localhost",
    kafka_port=9092,
    kafka_topic="app-logs",
    level="DEBUG"
)

logger.alert("Critical system event! 🚨")
```

### 🗄️ Log to PostgreSQL

```python
logger = setup_logging(
    db=True,
    db_type="postgresql",
    db_host="localhost",
    db_name="logs",
    db_user="admin",
    db_password="secret"
)

logger.emergency("Database connection lost!")
```

### 🎨 Custom Colors per Level

```python
logger = setup_logging(
    info_color="#00FFAA",
    error_color="bold red on #111111",
    warning_color="yellow",
    show_background=True
)
logger.info("Custom color!")
logger.error("Custom background!")
```

### 🧠 Custom Log Levels

```python
logger.notice("New user registered 📢")      # Custom level 25
logger.fatal("Fatal error — shutting down 💀")  # Level 55
logger.alert("Immediate action required! 🚨")   # Level 59
```

### 🧠 Custom Log Levels (Correct Location!)

```python
# File: test.py
logger = setup_logging(name="test")
logger.emergency("System down!")  # Shows: test.py:5 (not logger.py!)
```

```
import logging
logger = logging.getLogger("INHERITANCE")
from richcolorlog import RichColorLogHandler
handler = RichColorLogHandler()
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False

logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

```
---

## 🛠️ Configuration Options

| Parameter | Description | Default |
|----------|------------|--------|
| `show_icon` | Show emoji icons | `True` |
| `icon_first` | Icon before timestamp | `True` |
| `format_template` | Log format (supports `%(icon)s`) | `None` |
| `level_in_message` | Prefix message with `"LEVEL - "` | `False` |
| `omit_repeated_times` | Hide repeated timestamps | `True` |
| `show_background` | Enable background colors | `True` |
| `..._color` | Custom color per level (`info_color`, `error_color`, etc.) | Default |
| All `RichHandler` args | `tracebacks_show_locals`, `keywords`, `highlighter`, etc. | Fully supported |

> ✅ If `format_template` contains `%(icon)s`, the icon is **still controlled by `icon_first`** — no duplicates.

---

## 🦝 Available Lexers

You can use any lexer supported by Pygments for syntax highlighting:

- `"python"` - Python code
- `"javascript"` - JavaScript code
- `"sql"` - SQL queries  
- `"json"` - JSON data
- `"yaml"` - YAML configuration
- `"bash"` - Shell scripts
- And many more...

## 🐇 Custom Log Levels

richcolorlog adds several custom log levels above the standard CRITICAL level:

| Level | Numeric Value | Description |
|-------|---------------|-------------|
| NOTICE | 55 | Informational messages |
| ALERT | 60 | Alert conditions |
| CRITICAL | 65 | Critical conditions |
| FATAL | 70 | Fatal errors |
| EMERGENCY | 75 | System is unusable |

---

## 🧩 Supported Log Record Fields in Templates

You can use **any standard `LogRecord` field** in your `format_template`:

```text
%(asctime)s       → 2025-10-03 14:30:00
%(name)s          → myapp
%(levelname)s     → INFO
%(message)s       → Your log message
%(filename)s      → app.py
%(lineno)d        → 42
%(funcName)s      → main
%(process)d       → 12345
%(thread)d        → 67890
%(module)s        → app
%(pathname)s      → /path/to/app.py
%(created)f       → 1728000000.123
%(msecs)d         → 123
%(relativeCreated)d → 456
%(processName)s   → MainProcess
%(threadName)s    → Thread-1
%(icon)s          → 🐞 (auto-injected)
```

> ✅ **Custom fields** from `extra={}` are also supported!

---

## 🌐 Compatibility

- ✅ **Python 3.8+**
- ✅ **Jupyter Notebook / IPython** (auto-detects and disables async features)
- ✅ **Terminals** (Windows, macOS, Linux)
- ✅ **Docker / CI Environments** (falls back to ANSI if needed)

---

## 📚 Why Use `richcolorlog`?

| Feature | Standard `logging` | `rich` | `richcolorlog` |
|--------|-------------------|--------|----------------|
| Emoji Icons | ❌ | ❌ | ✅ |
| Custom Levels (`NOTICE`, `ALERT`) | ❌ | ❌ | ✅ |
| Syntax Highlighting | ❌ | ❌ | ✅ |
| Multi-Output (File + Kafka + DB) | Manual | ❌ | ✅ |
| Template + Icon | ❌ | Limited | ✅ |
| Accurate File/Line | ✅ | ❌ | ✅ |
| Jupyter Safe | ❌ | ⚠️ | ✅ |
| Repeated Timestamps | ❌ | ✅ | ✅ 
| Custom Format Templates | ✅ | Limited | ✅ + **icon support** |

---

## 🙏 Acknowledgements

- Built on top of [`rich`](https://github.com/Textualize/rich) by Will McGugan with ansi color Fallback if no rich installed  
- Icons from [EmojiOne](https://emojione.com/)
---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

MIT © [Hadi Cahyadi](https://github.com/cumulus13)

---

## 🔗 Links

- 📦 **PyPI**: https://pypi.org/project/richcolorlog/  
- 💻 **GitHub**: https://github.com/cumulus13/richcolorlog  
- 📧 **Author**: cumulus13@gmail.com

---

> 💬 **Made with ❤️ for developers who love beautiful, informative logs!**  
> ⭐ **Star the repo if you find it useful!**


## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)
