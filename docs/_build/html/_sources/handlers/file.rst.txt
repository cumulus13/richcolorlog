============
File Handler
============

RichColorLog includes built-in file logging with level-based formatting.

Basic File Logging
------------------

Enable file logging with the ``log_file`` parameter:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       log_file=True,
       log_file_name='app.log',
       log_file_level='DEBUG',
   )

   logger.info("This goes to console AND file")
   logger.debug("Debug messages have detailed format in file")

Automatic Filename
------------------

If ``log_file_name`` is not specified, it auto-generates from your script name:

.. code-block:: python

   # In myapp.py
   logger = setup_logging(log_file=True)
   # Creates: myapp.log

   # Or specify explicitly
   logger = setup_logging(
       log_file=True,
       log_file_name='/var/log/myapp/application.log'
   )

Level-Based Formatting
----------------------

The file handler uses ``LevelBasedFileFormatter`` which applies different formats based on log level:

**INFO and above:**

.. code-block:: text

   2025-01-15 10:30:45,123 - INFO - myapp - User logged in (auth.py:42)

**DEBUG:**

.. code-block:: text

   2025-01-15 10:30:45,123 - DEBUG - myapp - 12345 - 140123456789 - authenticate - Processing credentials (auth.py:38)

The DEBUG format includes:

- Process ID
- Thread ID  
- Function name
- Full pathname

File Handler Configuration
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``log_file``
     - ``False``
     - Enable file logging
   * - ``log_file_name``
     - Auto-generated
     - Path to log file
   * - ``log_file_level``
     - ``INFO``
     - Minimum level for file logging

Example Configurations
----------------------

Development
~~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       level='DEBUG',
       log_file=True,
       log_file_name='debug.log',
       log_file_level='DEBUG',  # Capture everything
   )

Production
~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       level='INFO',
       log_file=True,
       log_file_name='/var/log/myapp/app.log',
       log_file_level='INFO',   # Skip debug in file too
   )

Separate Files by Level
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from richcolorlog import setup_logging

   logger = setup_logging(name='myapp', level='DEBUG')

   # Error log
   error_handler = logging.FileHandler('error.log')
   error_handler.setLevel(logging.ERROR)
   error_handler.setFormatter(logging.Formatter(
       '%(asctime)s - %(levelname)s - %(message)s'
   ))
   logger.addHandler(error_handler)

   # Debug log
   debug_handler = logging.FileHandler('debug.log')
   debug_handler.setLevel(logging.DEBUG)
   logger.addHandler(debug_handler)

Rotating File Handler
---------------------

For production, use rotating handlers to manage file size:

.. code-block:: python

   import logging
   from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
   from richcolorlog import setup_logging
   from richcolorlog.logger import LevelBasedFileFormatter

   logger = setup_logging(name='myapp', level='DEBUG')

   # Size-based rotation
   rotating_handler = RotatingFileHandler(
       'app.log',
       maxBytes=10*1024*1024,  # 10MB
       backupCount=5
   )
   rotating_handler.setFormatter(LevelBasedFileFormatter())
   logger.addHandler(rotating_handler)

   # Time-based rotation (daily)
   timed_handler = TimedRotatingFileHandler(
       'app.log',
       when='midnight',
       interval=1,
       backupCount=30
   )
   timed_handler.setFormatter(LevelBasedFileFormatter())
   logger.addHandler(timed_handler)

Custom File Formatter
---------------------

Create custom formatters for file output:

.. code-block:: python

   import logging
   from richcolorlog import setup_logging

   class JSONFormatter(logging.Formatter):
       def format(self, record):
           import json
           log_entry = {
               'timestamp': self.formatTime(record),
               'level': record.levelname,
               'logger': record.name,
               'message': record.getMessage(),
               'module': record.module,
               'function': record.funcName,
               'line': record.lineno,
           }
           return json.dumps(log_entry)

   logger = setup_logging(name='myapp')

   json_handler = logging.FileHandler('app.json')
   json_handler.setFormatter(JSONFormatter())
   logger.addHandler(json_handler)

File Encoding
-------------

Always specify encoding for non-ASCII content:

.. code-block:: python

   import logging
   from richcolorlog import setup_logging

   logger = setup_logging(name='myapp')

   handler = logging.FileHandler('app.log', encoding='utf-8')
   logger.addHandler(handler)

   logger.info("Unicode: こんにちは 🎉")

Best Practices
--------------

1. **Use absolute paths in production**

   .. code-block:: python

      log_file_name='/var/log/myapp/app.log'

2. **Set appropriate permissions**

   .. code-block:: bash

      sudo mkdir -p /var/log/myapp
      sudo chown appuser:appgroup /var/log/myapp

3. **Use rotation for long-running services**

4. **Consider separate files for different severity levels**

5. **Include enough context in log messages**

   .. code-block:: python

      logger.info(f"User {user_id} performed {action} on {resource}")