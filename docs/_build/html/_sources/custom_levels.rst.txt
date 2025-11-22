=================
Custom Log Levels
=================

RichColorLog extends Python's standard logging with additional syslog-compatible log levels.

Level Hierarchy
---------------

From lowest to highest severity:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Level
     - Value
     - Icon
     - Description
   * - DEBUG
     - 10
     - 🐛
     - Detailed diagnostic information
   * - INFO
     - 20
     - 🔔
     - General informational messages
   * - NOTICE
     - 25
     - 📢
     - Normal but significant conditions
   * - WARNING
     - 30
     - ⛔
     - Warning conditions
   * - ERROR
     - 40
     - ❌
     - Error conditions
   * - CRITICAL
     - 50
     - 💥
     - Critical conditions
   * - FATAL
     - 55
     - 💀
     - Fatal errors
   * - ALERT
     - 59
     - 🚨
     - Action must be taken immediately
   * - EMERGENCY
     - 60
     - 🆘
     - System is unusable

Using Custom Levels
-------------------

All custom levels are available as logger methods:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging()

   # Standard Python levels
   logger.debug("Debugging information")
   logger.info("Informational message")
   logger.warning("Warning message")
   logger.error("Error occurred")
   logger.critical("Critical error")

   # Custom levels
   logger.notice("Notice: User logged in")
   logger.fatal("Fatal: Cannot recover from error")
   logger.alert("Alert: Disk space critical")
   logger.emergency("Emergency: System failure")

Level Constants
---------------

Import level constants for programmatic use:

.. code-block:: python

   from richcolorlog import (
       DEBUG_LEVEL,
       INFO_LEVEL,
       NOTICE_LEVEL,
       WARNING_LEVEL,
       ERROR_LEVEL,
       CRITICAL_LEVEL,
       FATAL_LEVEL,
       ALERT_LEVEL,
       EMERGENCY_LEVEL,
   )

   # Use in configuration
   logger = setup_logging(level=NOTICE_LEVEL)

   # Check if level is enabled
   if logger.isEnabledFor(ALERT_LEVEL):
       logger.alert("This will be logged")

Syslog Severity Mapping
-----------------------

Custom levels map to RFC 5424 syslog severities:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - RichColorLog Level
     - Syslog Severity
     - Syslog Name
   * - EMERGENCY
     - 0
     - Emergency
   * - ALERT
     - 1
     - Alert
   * - FATAL
     - 1
     - Alert (no standard)
   * - CRITICAL
     - 2
     - Critical
   * - ERROR
     - 3
     - Error
   * - WARNING
     - 4
     - Warning
   * - NOTICE
     - 5
     - Notice
   * - INFO
     - 6
     - Informational
   * - DEBUG
     - 7
     - Debug

This mapping ensures compatibility when using the Syslog handler.

Filtering by Level
------------------

Set minimum level for handlers:

.. code-block:: python

   from richcolorlog import setup_logging, NOTICE_LEVEL

   # Console shows NOTICE and above
   # File logs everything including DEBUG
   logger = setup_logging(
       level='DEBUG',           # Logger accepts all
       log_file=True,
       log_file_level='DEBUG', # File gets everything
   )

   # The console handler level is set by 'level' parameter

Per-Handler Levels
~~~~~~~~~~~~~~~~~~

Different handlers can have different levels:

.. code-block:: python

   logger = setup_logging(
       level='DEBUG',
       log_file=True,
       log_file_level='DEBUG',      # File: all messages
       syslog=True,
       syslog_level='WARNING',      # Syslog: warnings and above
       rabbitmq=True,
       rabbitmq_level='ERROR',      # RabbitMQ: errors only
   )

Level-Based Table Names (Database)
----------------------------------

When using the database handler, logs are stored in separate tables by level:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Level
     - Table Name
   * - EMERGENCY
     - ``log_emergency``
   * - ALERT
     - ``log_alert``
   * - FATAL
     - ``log_fatal``
   * - CRITICAL
     - ``log_critical``
   * - ERROR
     - ``log_error``
   * - WARNING
     - ``log_warning``
   * - NOTICE
     - ``log_notice``
   * - INFO
     - ``log_info``
   * - DEBUG
     - ``log_debug``

All logs are also stored in ``log_syslog`` table for combined querying.

Icon Customization
------------------

Icons are provided by the ``Icon`` class:

.. code-block:: python

   from richcolorlog.logger import Icon

   # Access icons
   print(Icon.debug)      # 🐛
   print(Icon.info)       # 🔔
   print(Icon.notice)     # 📢
   print(Icon.warning)    # ⛔
   print(Icon.error)      # ❌
   print(Icon.critical)   # 💥
   print(Icon.fatal)      # 💀
   print(Icon.alert)      # 🚨
   print(Icon.emergency)  # 🆘

   # Uppercase aliases also work
   print(Icon.DEBUG)      # 🐛
   print(Icon.EMERGENCY)  # 🆘

Best Practices
--------------

Use the right level for the right situation:

.. code-block:: python

   # DEBUG: Detailed info for debugging
   logger.debug(f"Processing item {item_id} with data: {data}")

   # INFO: Normal operations
   logger.info(f"User {user_id} logged in successfully")

   # NOTICE: Noteworthy but normal
   logger.notice(f"Configuration reloaded from {config_path}")

   # WARNING: Something unexpected but recoverable
   logger.warning(f"Rate limit approaching: {current}/{limit}")

   # ERROR: Operation failed
   logger.error(f"Failed to save file: {filename}")

   # CRITICAL: Serious problem
   logger.critical(f"Database connection pool exhausted")

   # FATAL: Unrecoverable error
   logger.fatal(f"Cannot initialize required service: {service}")

   # ALERT: Needs immediate attention
   logger.alert(f"Security breach detected from IP: {ip}")

   # EMERGENCY: System unusable
   logger.emergency("System memory exhausted, shutting down")