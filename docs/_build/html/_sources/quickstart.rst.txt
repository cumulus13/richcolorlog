==========
Quickstart
==========

This guide will help you get started with RichColorLog in just a few minutes.

Basic Setup
-----------

The simplest way to use RichColorLog:

.. code-block:: python

   from richcolorlog import setup_logging

   # Create a logger with default settings
   logger = setup_logging()

   # Log messages at different levels
   logger.debug("This is a debug message")
   logger.info("This is an info message")
   logger.warning("This is a warning message")
   logger.error("This is an error message")
   logger.critical("This is a critical message")

Named Loggers
-------------

Create named loggers for different modules:

.. code-block:: python

   from richcolorlog import setup_logging

   # Named logger for your module
   logger = setup_logging(name='myapp.module')

   logger.info("Message from myapp.module")

   # Another logger for a different module
   db_logger = setup_logging(name='myapp.database')
   db_logger.debug("Database query executed")

Custom Log Levels
-----------------

RichColorLog provides additional syslog-compatible log levels:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging()

   # Standard levels
   logger.debug("Debug level - detailed diagnostic info")
   logger.info("Info level - general information")
   logger.warning("Warning level - potential issues")
   logger.error("Error level - errors occurred")
   logger.critical("Critical level - serious errors")

   # Custom levels (syslog-compatible)
   logger.notice("Notice level - normal but significant")
   logger.alert("Alert level - action must be taken immediately")
   logger.emergency("Emergency level - system is unusable")
   logger.fatal("Fatal level - fatal error occurred")

Configuring Appearance
----------------------

Customize the log appearance:

.. code-block:: python

   from richcolorlog import setup_logging

   # With background colors (default)
   logger = setup_logging(show_background=True)

   # Without background colors (foreground only)
   logger = setup_logging(show_background=False)

   # With emoji icons
   logger = setup_logging(show_icon=True, icon_first=True)

   # Custom format template
   logger = setup_logging(
       format_template="%(asctime)s %(levelname)s %(message)s"
   )

File Logging
------------

Enable file logging alongside console output:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       log_file=True,
       log_file_name='app.log',
       log_file_level='DEBUG'
   )

   logger.info("This appears in console AND app.log")
   logger.debug("Debug messages go to file with detailed format")

Syntax Highlighting
-------------------

Highlight code in log messages:

.. code-block:: python

   from richcolorlog import setup_logging

   # Enable Python syntax highlighting
   logger = setup_logging(lexer='python')

   code = '''
   def hello():
       print("Hello World!")
   '''
   logger.debug(code)

   # Or per-message highlighting
   logger = setup_logging()
   logger.info("SQL Query:", extra={'lexer': 'sql'})
   logger.debug("SELECT * FROM users WHERE active = 1", extra={'lexer': 'sql'})

Using with ANSI (No Rich)
-------------------------

For environments without Rich or for simpler output:

.. code-block:: python

   from richcolorlog import setup_logging_custom

   # ANSI-based logger (no Rich dependency)
   logger = setup_logging_custom(
       show_background=True,
       show_icon=True,
       icon_first=True
   )

   logger.info("ANSI colored output")

Simple Logger for IPython/Jupyter
---------------------------------

For IPython or Jupyter notebooks:

.. code-block:: python

   from richcolorlog import getLoggerSimple

   # Optimized for notebooks
   logger = getLoggerSimple(name='notebook')

   logger.info("Works great in Jupyter!")

Complete Example
----------------

Here's a complete example showing various features:

.. code-block:: python

   from richcolorlog import setup_logging
   import logging

   # Setup with multiple options
   logger = setup_logging(
       name='myapp',
       level='DEBUG',
       show_background=True,
       show_icon=True,
       icon_first=True,
       show_time=True,
       show_level=True,
       show_path=True,
       log_file=True,
       log_file_name='myapp.log',
       log_file_level='INFO',
       omit_repeated_times=True,
   )

   # Application logging
   logger.info("Application started")
   logger.debug("Configuration loaded from config.yaml")

   try:
       # Some operation
       result = perform_operation()
       logger.notice("Operation completed successfully")
   except ValueError as e:
       logger.error(f"Validation error: {e}")
   except Exception as e:
       logger.critical(f"Unexpected error: {e}")
       logger.emergency("System state may be corrupted!")

   logger.info("Application shutdown")

Next Steps
----------

* Learn about :doc:`configuration` options
* Explore :doc:`custom_levels` in detail
* Set up :doc:`handlers/file` logging
* Configure :doc:`handlers/rabbitmq` for distributed logging