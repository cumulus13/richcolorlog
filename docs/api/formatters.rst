=============
Formatters API
=============

Formatter classes for formatting log records.

CustomFormatter
---------------

.. py:class:: CustomFormatter(logging.Formatter)

   Custom formatter with ANSI color codes for different log levels.

   :param show_background: Enable background colors.
   :type show_background: bool
   :param format_template: Custom format string.
   :type format_template: str, optional
   :param show_time: Include timestamp.
   :type show_time: bool
   :param show_name: Include logger name.
   :type show_name: bool
   :param show_pid: Include process ID.
   :type show_pid: bool
   :param show_level: Include log level.
   :type show_level: bool
   :param show_path: Include file path.
   :type show_path: bool
   :param show_icon: Enable icons.
   :type show_icon: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param lexer: Pygments lexer for highlighting.
   :type lexer: str, optional
   :param use_colors: Enable ANSI colors.
   :type use_colors: bool

   .. py:method:: format(record) -> str

      Format the log record with colors.

      :param record: Log record to format.
      :type record: logging.LogRecord
      :returns: Formatted string with ANSI codes.
      :rtype: str

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import CustomFormatter

      formatter = CustomFormatter(
          show_background=True,
          format_template="[%(levelname)s] %(message)s"
      )

CustomRichFormatter
-------------------

.. py:class:: CustomRichFormatter(logging.Formatter)

   Enhanced Rich formatter with syntax highlighting support.

   :param lexer: Pygments lexer name.
   :type lexer: str, optional
   :param show_background: Enable background colors.
   :type show_background: bool
   :param theme: Pygments theme name.
   :type theme: str
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool

   .. py:attribute:: LEVEL_STYLES

      Dictionary mapping log levels to Rich style strings.

   .. py:method:: format(record) -> str

      Format log record with Rich styling.

      :param record: Log record to format.
      :type record: logging.LogRecord
      :returns: Formatted string with Rich markup.
      :rtype: str

RichColorLogFormatter
---------------------

.. py:class:: RichColorLogFormatter(CustomRichFormatter)

   Adapter formatter for compatibility with standard logging.Formatter.

   :param fmt: Format string with ``%(log_color)s`` and ``%(reset)s``.
   :type fmt: str, optional
   :param datefmt: Date format string.
   :type datefmt: str, optional
   :param show_background: Enable background colors.
   :type show_background: bool
   :param show_time: Include timestamp.
   :type show_time: bool
   :param show_name: Include logger name.
   :type show_name: bool
   :param show_pid: Include process ID.
   :type show_pid: bool
   :param show_level: Include log level.
   :type show_level: bool
   :param show_path: Include file path.
   :type show_path: bool
   :param lexer: Pygments lexer.
   :type lexer: str
   :param theme: Pygments theme.
   :type theme: str
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import RichColorLogFormatter

      formatter = RichColorLogFormatter(
          fmt="%(log_color)s[%(levelname)s]%(reset)s %(message)s",
          datefmt="%H:%M:%S"
      )

      handler = logging.StreamHandler()
      handler.setFormatter(formatter)

LevelBasedFileFormatter
-----------------------

.. py:class:: LevelBasedFileFormatter(logging.Formatter)

   Formatter with different formats based on log level.

   Uses detailed format for DEBUG, simpler format for INFO and above.

   .. py:attribute:: info_format
      :value: "%(asctime)s - %(levelname)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)"

   .. py:attribute:: debug_format
      :value: "%(asctime)s - %(levelname)s - %(name)s - %(process)d - %(thread)d - %(funcName)s - %(message)s (%(pathname)s:%(lineno)d)"

   .. py:method:: format(record) -> str

      Format record using level-appropriate format.

      :param record: Log record to format.
      :type record: logging.LogRecord
      :returns: Formatted string.
      :rtype: str

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import LevelBasedFileFormatter

      formatter = LevelBasedFileFormatter()

      file_handler = logging.FileHandler('app.log')
      file_handler.setFormatter(formatter)

Formatter Color Attributes
--------------------------

CustomFormatter exposes these color dictionaries:

.. code-block:: python

   CustomFormatter.COLORS = {
       'debug': "...",      # ANSI code for debug
       'info': "...",       # ANSI code for info
       'notice': "...",     # ANSI code for notice
       'warning': "...",    # ANSI code for warning
       'error': "...",      # ANSI code for error
       'critical': "...",   # ANSI code for critical
       'fatal': "...",      # ANSI code for fatal
       'alert': "...",      # ANSI code for alert
       'emergency': "...",  # ANSI code for emergency
       'reset': "\x1b[0m",  # Reset code
   }

CustomRichFormatter exposes:

.. code-block:: python

   CustomRichFormatter.LEVEL_STYLES = {
       logging.DEBUG: "bold #FFAA00",
       logging.INFO: "bold #00FFFF",
       logging.WARNING: "black on #FFFF00",
       logging.ERROR: "white on red",
       logging.CRITICAL: "bright_white on #550000",
       # ... custom levels
   }