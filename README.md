# Rich Color Log

A beautiful and feature-rich logging package using the [Rich](https://github.com/Textualize/rich) library for enhanced console output and file logging.

[![Screenshot](./screenshot.png)](./screenshot.png)

## Features

- 🎨 **Beautiful console output** with Rich formatting
- 📝 **Dual logging** - Console and file output simultaneously
- 🎯 **Custom log levels** - EMERGENCY, FATAL, CRITICAL, ALERT, NOTICE
- 🌈 **Syntax highlighting** - Support for code syntax highlighting in logs
- 🔍 **Enhanced tracebacks** - Rich tracebacks with local variables
- ⚙️ **Highly configurable** - Customizable colors, themes, and formats
- 🚀 **Easy to use** - Simple setup with sensible defaults

## Installation

Install from PyPI:

```bash
pip install richcolorlog
```

Or install from source:

```bash
git clone https://github.com/cumulus13/richcolorlog
cd richcolorlog
pip install -e .
```

## Quick Start

### Basic Usage

```python
import logging
from richcolorlog import setup_logging

# Setup the logger use with rich library
logger = setup_logging()

# Use standard logging levels
logger.debug("This is a debug message")
logger.info("This is an info message") 
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")

# Use custom levels
logger.emergency("This is an emergency!")
logger.fatal("This is fatal!")
logger.alert("This is an alert!")
logger.notice("This is a notice")

# Setup the logger use without rich library (ANSI Colors)
logger = setup_logging_custom()
# S/A

```

### Advanced Configuration

#### Using Custom Formatter (rich)

```python
import logging
from richcolorlog import setup_logging

# Setup with custom options
logger = setup_logging(
    show_locals=True,      # Show local variables in tracebacks
    logfile="my_app.log",  # Custom log file name, option default file name [dot] log
    lexer="python",        # Syntax highlighting for Python code, option default None
    level=logging.INFO     # Set minimum log level or just 'INFO'
)

# Log with syntax highlighting
logger.info("Here's some Python code:", extra={"lexer": "python"})
logger.info("def hello_world():\n    print('Hello, World!')")
```

other parameters:

 - show_level: bool = False
 - show_time: bool = True
 - omit_repeated_times: bool = True
 - show_path: bool = True
 - enable_link_path: bool = True
 - highlighter = None
 - markup: bool = False
 - rich_tracebacks: bool = False
 - tracebacks_width: Optional[int] = None
 - tracebacks_extra_lines: int = 3
 - tracebacks_theme: Optional[str] = None
 - tracebacks_word_wrap: bool = True
 - tracebacks_show_locals: bool = False
 - tracebacks_suppress: Iterable[Union[str ModuleType]] = ()
 - locals_max_length: int = 10
 - locals_max_string: int = 80
 - log_time_format: Union[str FormatTimeCallable] = "[%x %X]"
 - keywords: Optional[List[str]] = None
 - show_background = True

#### Using Custom Formatter (ANSI Colors)

```python
from richcolorlog import setup_logging_custom

# Setup basic logging with ANSI color codes
logger = setup_logging_custom()
logger.info("This will be colored in the terminal")
```

other parameters:

 - level = Union[str, int] #example: 'DEBUG' or 'logging.DEBUG'
 - show_background = True
 - format_template=None
 - show_time=True
 - show_name=True
 - show_pid=True
 - show_level=True
 - show_path=True

## Custom Log Levels

Rich Logger adds several custom log levels above the standard CRITICAL level:

| Level | Numeric Value | Description |
|-------|---------------|-------------|
| NOTICE | 55 | Informational messages |
| ALERT | 60 | Alert conditions |
| CRITICAL | 65 | Critical conditions |
| FATAL | 70 | Fatal errors |
| EMERGENCY | 75 | System is unusable |

## Configuration Options

### `setup_logging()`

- `show_locals` (bool): Show local variables in tracebacks (default: False)
- `logfile` (str): Path to log file. Auto-generated if None (default: None)
- `lexer` (str): Syntax highlighter for code blocks (default: None)
- `level` (int): Minimum logging level (default: logging.DEBUG)

### Available Lexers

You can use any lexer supported by Pygments for syntax highlighting:

- `"python"` - Python code
- `"javascript"` - JavaScript code
- `"sql"` - SQL queries  
- `"json"` - JSON data
- `"yaml"` - YAML configuration
- `"bash"` - Shell scripts
- And many more...

## Examples

### Exception Handling with Rich Tracebacks

```python
import logging
from richcolorlog import setup_logging

logger = setup_logging(show_locals=True)

def divide_numbers(a, b):
    try:
        result = a / b
        logger.info(f"Division result: {result}")
        return result
    except ZeroDivisionError:
        logger.exception("Cannot divide by zero!")
        raise

# This will show a beautiful traceback with local variables
divide_numbers(10, 0)
```

### Logging with Context Information

```python
import logging
from richcolorlog import setup_logging, get_def

logger = setup_logging()

class MyClass:
    def my_method(self):
        context = get_def()  # Gets current method/class context
        logger.info(f"{context}Executing method")

obj = MyClass()
obj.my_method()
```

### Code Logging with Syntax Highlighting

```python
import logging
from richcolorlog import setup_logging

logger = setup_logging()

code_snippet = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

# Log code with Python syntax highlighting
logger.info("Generated function:", extra={"lexer": "python"})
logger.info(code_snippet)
```

## File Structure

When you install this package, your project structure should look like:

```
your_project/
├── your_script.py
├── your_script.log  # Auto-generated log file
└── ...
```

## Requirements

- Python >= 3.7
- rich >= 10.0.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rich](https://github.com/Textualize/rich) - For the amazing terminal formatting library
- The Python logging module - For the solid foundation

## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)