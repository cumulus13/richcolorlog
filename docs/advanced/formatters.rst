===========
Formatters
===========

RichColorLog provides several formatters for different output scenarios.

CustomFormatter (ANSI)
----------------------

Standard formatter using ANSI escape codes.

.. code-block:: python

   from richcolorlog.logger import CustomFormatter

   formatter = CustomFormatter(
       show_background=True,
       format_template="[%(levelname)s] %(message)s",
       show_time=True,
       show_name=True,
       show_pid=True,
       show_level=True,
       show_path=True,
       show_icon=True,
       icon_first=True,
       lexer='python',           # Pygments lexer
       use_colors=True,
       # Custom colors
       debug_color='\x1b[93m',   # ANSI codes
       info_color='\x1b[96m',
   )

   handler = logging.StreamHandler()
   handler.setFormatter(formatter)

CustomRichFormatter
-------------------

Formatter for Rich-based output with styling.

.. code-block:: python

   from richcolorlog.logger import CustomRichFormatter

   formatter = CustomRichFormatter(
       lexer='python',
       show_background=True,
       theme='fruity',
       icon_first=True,
   )

RichColorLogFormatter
---------------------

Adapter for compatibility with standard logging formatters.

.. code-block:: python

   from richcolorlog.logger import RichColorLogFormatter

   formatter = RichColorLogFormatter(
       fmt="%(log_color)s[%(levelname)s]%(reset)s %(message)s",
       datefmt="%H:%M:%S",
       show_background=True,
   )

   # Works with standard logging
   handler = logging.StreamHandler()
   handler.setFormatter(formatter)

LevelBasedFileFormatter
-----------------------

Different formats for different log levels.

.. code-block:: python

   from richcolorlog.logger import LevelBasedFileFormatter

   formatter = LevelBasedFileFormatter()

   # INFO and above:
   # 2025-01-15 10:30:45 - INFO - myapp - Message (file.py:42)

   # DEBUG:
   # 2025-01-15 10:30:45 - DEBUG - myapp - 12345 - 140123 - func - Message (/full/path.py:42)

Creating Custom Formatters
--------------------------

Extend base formatters:

.. code-block:: python

   import logging
   import json
   from datetime import datetime

   class JSONFormatter(logging.Formatter):
       """Format logs as JSON."""

       def format(self, record):
           log_entry = {
               'timestamp': datetime.fromtimestamp(record.created).isoformat(),
               'level': record.levelname,
               'logger': record.name,
               'message': record.getMessage(),
               'module': record.module,
               'function': record.funcName,
               'line': record.lineno,
               'process': record.process,
               'thread': record.thread,
           }

           # Include exception info
           if record.exc_info:
               log_entry['exception'] = self.formatException(record.exc_info)

           return json.dumps(log_entry)


   class ColorJSONFormatter(logging.Formatter):
       """JSON with colored level."""

       COLORS = {
           'DEBUG': '\x1b[93m',
           'INFO': '\x1b[92m',
           'WARNING': '\x1b[93m',
           'ERROR': '\x1b[91m',
           'CRITICAL': '\x1b[91;1m',
       }
       RESET = '\x1b[0m'

       def format(self, record):
           color = self.COLORS.get(record.levelname, '')
           log_entry = {
               'level': f"{color}{record.levelname}{self.RESET}",
               'message': record.getMessage(),
           }
           return json.dumps(log_entry)


   class StructuredFormatter(logging.Formatter):
       """Key=value structured logging."""

       def format(self, record):
           parts = [
               f"time={datetime.fromtimestamp(record.created).isoformat()}",
               f"level={record.levelname}",
               f"logger={record.name}",
               f"msg={record.getMessage()!r}",
               f"file={record.filename}:{record.lineno}",
           ]
           return " ".join(parts)

Using Custom Formatters
-----------------------

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(name='myapp')

   # Add JSON handler for file
   json_handler = logging.FileHandler('app.json')
   json_handler.setFormatter(JSONFormatter())
   logger.addHandler(json_handler)

   # Add structured handler for stdout
   structured_handler = logging.StreamHandler()
   structured_handler.setFormatter(StructuredFormatter())
   # Replace existing handler
   # logger.handlers = [structured_handler]

Format String Reference
-----------------------

Available placeholders:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Placeholder
     - Description
   * - ``%(asctime)s``
     - Human-readable time
   * - ``%(created)f``
     - Unix timestamp
   * - ``%(filename)s``
     - Filename portion of pathname
   * - ``%(funcName)s``
     - Function name
   * - ``%(levelname)s``
     - Text logging level
   * - ``%(levelno)d``
     - Numeric logging level
   * - ``%(lineno)d``
     - Source line number
   * - ``%(message)s``
     - The logged message
   * - ``%(module)s``
     - Module name
   * - ``%(msecs)d``
     - Millisecond portion of time
   * - ``%(name)s``
     - Logger name
   * - ``%(pathname)s``
     - Full pathname of source file
   * - ``%(process)d``
     - Process ID
   * - ``%(processName)s``
     - Process name
   * - ``%(relativeCreated)d``
     - Time since logging module loaded
   * - ``%(thread)d``
     - Thread ID
   * - ``%(threadName)s``
     - Thread name

RichColorLog-specific:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Placeholder
     - Description
   * - ``%(icon)s``
     - Emoji icon for level
   * - ``%(log_color)s``
     - ANSI color start code
   * - ``%(reset)s``
     - ANSI reset code