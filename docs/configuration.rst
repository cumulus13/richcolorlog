=============
Configuration
=============

RichColorLog provides extensive configuration options for customizing your logging setup.

setup_logging() Parameters
--------------------------

The main ``setup_logging()`` function accepts the following parameters:

Basic Parameters
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``name``
     - ``None``
     - Logger name. If None, returns root logger
   * - ``level``
     - ``'DEBUG'``
     - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   * - ``show``
     - ``True``
     - Enable/disable logging output

Display Options
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``show_background``
     - ``True``
     - Show background colors for log levels
   * - ``show_icon``
     - ``True``
     - Show emoji icons for log levels
   * - ``icon_first``
     - ``True``
     - Place icon before timestamp (vs. after message)
   * - ``show_time``
     - ``True``
     - Show timestamp in log output
   * - ``show_level``
     - ``True``
     - Show log level name
   * - ``show_path``
     - ``True``
     - Show file path and line number
   * - ``omit_repeated_times``
     - ``True``
     - Hide repeated timestamps

Format Options
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``format_template``
     - ``None``
     - Custom format string (see Format Templates)
   * - ``log_time_format``
     - ``'[%x %X]'``
     - Time format string or callable
   * - ``level_in_message``
     - ``False``
     - Include level name in message text
   * - ``markup``
     - ``False``
     - Enable Rich markup in messages

Syntax Highlighting
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``lexer``
     - ``None``
     - Pygments lexer name for syntax highlighting
   * - ``theme``
     - ``'fruity'``
     - Pygments theme for syntax highlighting
   * - ``render_emoji``
     - ``True``
     - Render emoji in messages

Custom Colors
~~~~~~~~~~~~~

Override default colors for each log level:

.. code-block:: python

   logger = setup_logging(
       debug_color='#FFAA00',
       info_color='#00FF00',
       warning_color='black on #FFFF00',
       error_color='white on red',
       critical_color='bright_white on #0000FF',
       notice_color='black on #00FFFF',
       alert_color='bright_white on #005500',
       emergency_color='bright_white on #AA00FF',
       fatal_color='blue on #FF557F',
   )

Format Templates
----------------

Use format templates to customize log output structure:

Available Placeholders
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Placeholder
     - Description
   * - ``%(asctime)s``
     - Timestamp
   * - ``%(name)s``
     - Logger name
   * - ``%(levelname)s``
     - Level name (DEBUG, INFO, etc.)
   * - ``%(levelno)d``
     - Numeric level value
   * - ``%(message)s``
     - Log message
   * - ``%(filename)s``
     - Source filename
   * - ``%(lineno)d``
     - Line number
   * - ``%(pathname)s``
     - Full path to source file
   * - ``%(funcName)s``
     - Function name
   * - ``%(module)s``
     - Module name
   * - ``%(process)d``
     - Process ID
   * - ``%(processName)s``
     - Process name
   * - ``%(thread)d``
     - Thread ID
   * - ``%(threadName)s``
     - Thread name
   * - ``%(icon)s``
     - Emoji icon for level

Example Templates
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Simple format
   logger = setup_logging(
       format_template="%(levelname)s - %(message)s"
   )

   # Detailed format
   logger = setup_logging(
       format_template="%(asctime)s [%(name)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"
   )

   # With icon
   logger = setup_logging(
       format_template="%(icon)s %(asctime)s %(levelname)s %(message)s",
       show_icon=True,
       icon_first=False  # Icon position controlled by template
   )

Environment Variables
---------------------

RichColorLog respects several environment variables:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Variable
     - Description
   * - ``NO_LOGGING``
     - Set to ``1`` to disable all logging
   * - ``LOGGING``
     - Set to ``0`` to disable all logging
   * - ``FORCE_COLOR``
     - Set to ``1`` to force color output
   * - ``NO_COLOR``
     - Set to disable color output
   * - ``TERM``
     - Terminal type for color detection
   * - ``COLORTERM``
     - Color terminal capabilities
   * - ``WT_SESSION``
     - Windows Terminal session (enables truecolor)
   * - ``RICHCOLORLOG_DEBUG``
     - Set to ``1`` for debug output

Example:

.. code-block:: bash

   # Disable logging
   export NO_LOGGING=1
   python myapp.py

   # Force colors in pipe
   export FORCE_COLOR=1
   python myapp.py | tee output.log

Configuration Examples
----------------------

Development Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       name='myapp',
       level='DEBUG',
       show_background=True,
       show_icon=True,
       icon_first=True,
       show_time=True,
       show_path=True,
       rich_tracebacks=True,
       tracebacks_show_locals=True,
   )

Production Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       name='myapp',
       level='INFO',
       show_background=False,
       show_icon=False,
       log_file=True,
       log_file_name='/var/log/myapp/app.log',
       log_file_level='DEBUG',
       syslog=True,
       syslog_host='logserver.example.com',
   )

Minimal Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       level='INFO',
       show_time=False,
       show_path=False,
       show_icon=False,
       format_template="%(levelname)s: %(message)s"
   )