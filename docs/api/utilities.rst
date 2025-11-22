=============
Utilities API
=============

Helper classes and functions.

Icon
----

.. py:class:: Icon

   Emoji icon mappings for different log levels.

   .. py:attribute:: debug
      :value: "🐛"

   .. py:attribute:: info
      :value: "🔔"

   .. py:attribute:: notice
      :value: "📢"

   .. py:attribute:: warning
      :value: "⛔"

   .. py:attribute:: error
      :value: "❌"

   .. py:attribute:: critical
      :value: "💥"

   .. py:attribute:: alert
      :value: "🚨"

   .. py:attribute:: emergency
      :value: "🆘"

   .. py:attribute:: fatal
      :value: "💀"

   Also available as uppercase (``DEBUG``, ``INFO``, etc.) and short aliases
   (``DEB``, ``INF``, ``WARN``, ``ERR``, etc.).

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import Icon

      print(f"{Icon.error} An error occurred")
      # Output: ❌ An error occurred

IconFilter
----------

.. py:class:: IconFilter(logging.Filter)

   Filter to add icons to log records.

   :param icon_first: Position hint (used by handler).
   :type icon_first: bool

   .. py:method:: filter(record) -> bool

      Add ``icon`` attribute to record based on level.

      :param record: Log record.
      :type record: logging.LogRecord
      :returns: Always True (passes all records).
      :rtype: bool

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import IconFilter

      handler.addFilter(IconFilter(icon_first=True))

PerformanceTracker
------------------

.. py:class:: PerformanceTracker

   Track performance metrics for logging operations.

   .. py:method:: record(operation: str, duration: float)

      Record a performance metric.

      :param operation: Operation name.
      :type operation: str
      :param duration: Duration in seconds.
      :type duration: float

   .. py:method:: get_stats() -> dict

      Get performance statistics.

      :returns: Statistics by operation.
      :rtype: dict

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import _performance

      stats = _performance.get_stats()
      # {'format': {'count': 100, 'avg': 0.0001, 'min': 0.00005, 'max': 0.001}}

performance_monitor
-------------------

.. py:function:: performance_monitor(func)

   Decorator to monitor function performance.

   :param func: Function to monitor.
   :type func: callable
   :returns: Wrapped function.
   :rtype: callable

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import performance_monitor

      @performance_monitor
      def my_function():
          # ... do work
          pass

      # Stats recorded in global _performance tracker

Syslog Mappings
---------------

.. py:data:: SYSLOG_SEVERITY_MAP

   Mapping from log levels to RFC 5424 syslog severities.

   .. code-block:: python

      SYSLOG_SEVERITY_MAP = {
          EMERGENCY_LEVEL: 0,  # Emergency
          ALERT_LEVEL: 1,      # Alert
          FATAL_LEVEL: 1,      # Fatal (maps to Alert)
          CRITICAL_LEVEL: 2,   # Critical
          ERROR_LEVEL: 3,      # Error
          WARNING_LEVEL: 4,    # Warning
          NOTICE_LEVEL: 5,     # Notice
          INFO_LEVEL: 6,       # Informational
          DEBUG_LEVEL: 7,      # Debug
      }

.. py:data:: LEVEL_TO_TABLE

   Mapping from log levels to database table names.

   .. code-block:: python

      LEVEL_TO_TABLE = {
          EMERGENCY_LEVEL: "log_emergency",
          ALERT_LEVEL: "log_alert",
          FATAL_LEVEL: "log_fatal",
          CRITICAL_LEVEL: "log_critical",
          ERROR_LEVEL: "log_error",
          WARNING_LEVEL: "log_warning",
          NOTICE_LEVEL: "log_notice",
          INFO_LEVEL: "log_info",
          DEBUG_LEVEL: "log_debug",
      }

.. py:data:: LOGGING_LEVELS_LIST

   All logging levels for iteration.

   .. code-block:: python

      LOGGING_LEVELS_LIST = [
          DEBUG_LEVEL,      # 10
          INFO_LEVEL,       # 20
          NOTICE_LEVEL,     # 25
          WARNING_LEVEL,    # 30
          ERROR_LEVEL,      # 40
          logging.CRITICAL, # 50
          CRITICAL_LEVEL,   # 58
          FATAL_LEVEL,      # 55
          ALERT_LEVEL,      # 59
          EMERGENCY_LEVEL,  # 60
      ]

IPython Utilities
-----------------

.. py:function:: _is_ipython() -> bool

   Check if running in IPython/Jupyter.

   :returns: True if in IPython environment.
   :rtype: bool

.. py:function:: _configure_ipython_logging()

   Configure logging for IPython compatibility.

   Suppresses async warnings and adjusts Rich detection.

.. py:function:: suppress_async_warning()

   Suppress async warnings in Jupyter/IPython.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import suppress_async_warning

      suppress_async_warning()

Environment Checking
--------------------

.. py:function:: _check_logging_disabled() -> bool

   Check if logging is disabled via environment variables.

   Checks ``NO_LOGGING=1`` and ``LOGGING=0``.

   :returns: True if logging is disabled.
   :rtype: bool

Test Functions
--------------

.. py:function:: test()

   Run comprehensive tests for the logger.

.. py:function:: test_brokers()

   Test message broker handlers.

.. py:function:: test_lexer()

   Test lexer functionality.

.. py:function:: run_test()

   Run all tests including examples.