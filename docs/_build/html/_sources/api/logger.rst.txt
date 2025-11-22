==========
Logger API
==========

Main functions for creating and configuring loggers.

setup_logging
-------------

.. py:function:: setup_logging(name=None, level='DEBUG', **kwargs) -> logging.Logger

   Create and configure a logger with Rich formatting.

   :param name: Logger name. If None, configures root logger.
   :type name: str, optional
   :param level: Minimum logging level.
   :type level: str or int
   :param lexer: Pygments lexer for syntax highlighting.
   :type lexer: str, optional
   :param show_locals: Show local variables in tracebacks.
   :type show_locals: bool
   :param show_background: Enable background colors.
   :type show_background: bool
   :param render_emoji: Render emoji characters.
   :type render_emoji: bool
   :param show_icon: Show emoji icons for levels.
   :type show_icon: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param exceptions: List of logger names to suppress.
   :type exceptions: list, optional
   :param show: Enable/disable logging output.
   :type show: bool
   :param theme: Pygments theme for syntax highlighting.
   :type theme: str
   :param format_template: Custom format string.
   :type format_template: str, optional
   :param log_file: Enable file logging.
   :type log_file: bool
   :param log_file_name: Path to log file.
   :type log_file_name: str, optional
   :param log_file_level: Minimum level for file logging.
   :type log_file_level: str or int
   :returns: Configured logger instance.
   :rtype: logging.Logger

   **Example:**

   .. code-block:: python

      from richcolorlog import setup_logging

      logger = setup_logging(
          name='myapp',
          level='DEBUG',
          show_background=True,
          show_icon=True,
          log_file=True,
      )

      logger.info("Application started")

setup_logging_custom
--------------------

.. py:function:: setup_logging_custom(name=__name__, level='DEBUG', **kwargs) -> logging.Logger

   Create a logger with ANSI color formatting (no Rich dependency).

   :param name: Logger name.
   :type name: str
   :param level: Minimum logging level.
   :type level: str or int
   :param show_background: Enable background colors.
   :type show_background: bool
   :param format_template: Custom format string.
   :type format_template: str, optional
   :param show_time: Show timestamp.
   :type show_time: bool
   :param show_name: Show logger name.
   :type show_name: bool
   :param show_pid: Show process ID.
   :type show_pid: bool
   :param show_level: Show log level.
   :type show_level: bool
   :param show_path: Show file path and line number.
   :type show_path: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param use_colors: Enable ANSI colors.
   :type use_colors: bool
   :returns: Configured logger instance.
   :rtype: logging.Logger

   **Example:**

   .. code-block:: python

      from richcolorlog import setup_logging_custom

      logger = setup_logging_custom(
          show_background=False,
          format_template="[%(levelname)s] %(message)s"
      )

getLogger
---------

.. py:function:: getLogger(*args, **kwargs) -> logging.Logger

   Alias for :func:`setup_logging`.

   **Example:**

   .. code-block:: python

      from richcolorlog import getLogger

      logger = getLogger('myapp', level='DEBUG')

getLoggerSimple
---------------

.. py:function:: getLoggerSimple(name=None, show_icon=True, icon_first=False, show_background=True, level=logging.DEBUG) -> logging.Logger

   Create a simple logger optimized for IPython/Jupyter.

   :param name: Logger name.
   :type name: str, optional
   :param show_icon: Show emoji icons.
   :type show_icon: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param show_background: Enable background colors.
   :type show_background: bool
   :param level: Logging level.
   :type level: int
   :returns: Simple configured logger.
   :rtype: logging.Logger

   **Example:**

   .. code-block:: python

      from richcolorlog import getLoggerSimple

      # In Jupyter notebook
      logger = getLoggerSimple('notebook')
      logger.info("Works in Jupyter!")

get_def
-------

.. py:function:: get_def() -> str

   Get current function/class definition name for logging context.

   :returns: Name of current function or class.
   :rtype: str

   **Example:**

   .. code-block:: python

      from richcolorlog import get_def

      def my_function():
          logger.info(f"{get_def()}: Starting operation")

      # Output: my_function: Starting operation

CustomLogger
------------

.. py:class:: CustomLogger(logging.Logger)

   Extended Logger class with custom level methods.

   .. py:method:: debug(msg, *args, **kwargs)

      Log DEBUG message.

   .. py:method:: info(msg, *args, **kwargs)

      Log INFO message.

   .. py:method:: notice(msg, *args, **kwargs)

      Log NOTICE message (custom level).

   .. py:method:: warning(msg, *args, **kwargs)

      Log WARNING message.

   .. py:method:: error(msg, *args, **kwargs)

      Log ERROR message.

   .. py:method:: critical(msg, *args, **kwargs)

      Log CRITICAL message.

   .. py:method:: fatal(msg, *args, **kwargs)

      Log FATAL message (custom level).

   .. py:method:: alert(msg, *args, **kwargs)

      Log ALERT message (custom level).

   .. py:method:: emergency(msg, *args, **kwargs)

      Log EMERGENCY message (custom level).

   **Passing lexer:**

   .. code-block:: python

      logger.debug(code, extra={'lexer': 'python'})

Level Constants
---------------

.. py:data:: DEBUG_LEVEL
   :value: 10

.. py:data:: INFO_LEVEL
   :value: 20

.. py:data:: NOTICE_LEVEL
   :value: 25

.. py:data:: WARNING_LEVEL
   :value: 30

.. py:data:: ERROR_LEVEL
   :value: 40

.. py:data:: CRITICAL_LEVEL
   :value: 58

.. py:data:: FATAL_LEVEL
   :value: 55

.. py:data:: ALERT_LEVEL
   :value: 59

.. py:data:: EMERGENCY_LEVEL
   :value: 60