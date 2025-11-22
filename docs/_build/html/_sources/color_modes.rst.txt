===========
Color Modes
===========

RichColorLog automatically detects terminal color capabilities and adapts output accordingly.

Color Support Detection
-----------------------

The library uses the ``Check`` class to detect terminal capabilities:

.. code-block:: python

   from richcolorlog.logger import Check, ColorSupport

   # Detect current terminal support
   mode = Check()  # Returns one of the ColorSupport values
   print(f"Color support: {mode}")

Color Support Levels
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Description
   * - ``truecolor``
     - 24-bit color (16.7 million colors)
   * - ``256color``
     - 256 color palette
   * - ``basic``
     - 8/16 basic ANSI colors
   * - ``none``
     - No color support

Detection Logic
---------------

The detection follows this priority:

1. **Environment Variables**

   - ``COLORTERM=truecolor`` or ``COLORTERM=24bit`` → TrueColor
   - ``WT_SESSION`` set (Windows Terminal) → TrueColor
   - ``TERM`` contains ``256color`` → 256 colors
   - ``TERM`` contains ``color`` → Basic colors

2. **curses/terminfo** (Unix-like systems)

   - Queries terminal capabilities via ``curses.tigetnum("colors")``

3. **Windows Detection**

   - Enables ANSI processing via Windows API
   - Windows 10+ typically supports TrueColor

4. **TTY Check**

   - Non-TTY output (pipes, files) defaults to no colors

Forcing Color Mode
------------------

Override automatic detection:

.. code-block:: python

   from richcolorlog.logger import Check, ColorSupport

   # Force specific mode
   mode = Check(force=ColorSupport.TRUECOLOR)
   mode = Check(force=ColorSupport.COLOR_256)
   mode = Check(force=ColorSupport.BASIC)
   mode = Check(force=ColorSupport.NONE)

Or use environment variables:

.. code-block:: bash

   # Force colors in pipe
   FORCE_COLOR=1 python myapp.py | cat

   # Disable colors
   NO_COLOR=1 python myapp.py

Color Schemes
-------------

The ``Colors`` class provides color schemes for different modes:

TrueColor (24-bit)
~~~~~~~~~~~~~~~~~~

Full RGB color support with exact color values:

.. code-block:: python

   from richcolorlog.logger import Colors

   # With background
   colors = Colors(color_type='ansi', show_background=True).check()

   # Example: debug color
   # "\x1b[38;2;0;0;0;48;2;255;170;0m" (black on orange)

   # Without background
   colors = Colors(color_type='ansi', show_background=False).check()

   # Example: debug color
   # "\x1b[38;2;255;170;0m" (orange foreground only)

256 Color Mode
~~~~~~~~~~~~~~

Uses 256-color palette approximations:

.. code-block:: python

   colors = Colors(color_type='ansi', show_background=True).check()
   # On 256-color terminal:
   # debug: "\x1b[30;48;5;214m" (black on color 214)

Basic (8/16 Colors)
~~~~~~~~~~~~~~~~~~~

Falls back to standard ANSI colors:

.. code-block:: python

   colors = Colors(color_type='ansi', show_background=True).check()
   # On basic terminal:
   # debug: "\x1b[30;43m" (black on yellow)

Rich Color Format
~~~~~~~~~~~~~~~~~

For Rich library output:

.. code-block:: python

   colors = Colors(color_type='rich', show_background=True).check()
   # Returns Rich-compatible style strings:
   # debug: "#000000 on #FFAA00"
   # error: "white on red"

Default Color Palette
---------------------

With Background
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Level
     - TrueColor
     - Description
   * - DEBUG
     - ``#000000 on #FFAA00``
     - Black on orange
   * - INFO
     - ``#000000 on #00FF00``
     - Black on green
   * - NOTICE
     - ``#000000 on #00FFFF``
     - Black on cyan
   * - WARNING
     - ``black on #FFFF00``
     - Black on yellow
   * - ERROR
     - ``white on red``
     - White on red
   * - CRITICAL
     - ``bright_white on #0000FF``
     - White on blue
   * - FATAL
     - ``blue on #FF557F``
     - Blue on pink
   * - ALERT
     - ``bright_white on #005500``
     - White on dark green
   * - EMERGENCY
     - ``bright_white on #AA00FF``
     - White on purple

Without Background
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Level
     - TrueColor
     - Description
   * - DEBUG
     - ``#FFAA00``
     - Orange
   * - INFO
     - ``#00FF00``
     - Green
   * - NOTICE
     - ``#00FFFF``
     - Cyan
   * - WARNING
     - ``#FFFF00``
     - Yellow
   * - ERROR
     - ``red``
     - Red
   * - CRITICAL
     - ``#0000FF``
     - Blue
   * - FATAL
     - ``#FF557F``
     - Pink
   * - ALERT
     - ``#005500``
     - Dark green
   * - EMERGENCY
     - ``#AA00FF``
     - Purple

Custom Colors
-------------

Override default colors:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       # Rich format colors
       debug_color='bold yellow',
       info_color='bold cyan',
       warning_color='black on bright_yellow',
       error_color='bold white on red',
       critical_color='bold white on dark_red',
       notice_color='bold magenta',
       alert_color='blink bold white on red',
       emergency_color='bold white on bright_red',
       fatal_color='bold red',
   )

Or for ANSI handler:

.. code-block:: python

   from richcolorlog import setup_logging_custom

   logger = setup_logging_custom(
       # ANSI escape codes
       debug_color='\x1b[93m',          # Bright yellow
       info_color='\x1b[96m',           # Bright cyan
       error_color='\x1b[91m',          # Bright red
   )

Windows Support
---------------

On Windows, RichColorLog enables ANSI support automatically:

.. code-block:: python

   from richcolorlog.logger import Check

   # This is called automatically but can be called manually
   Check.enable_windows_ansi()

Requirements for Windows:

- Windows 10 version 1511 or later
- Windows Terminal recommended for best results
- Legacy cmd.exe has limited support

Testing Color Support
---------------------

.. code-block:: python

   from richcolorlog import setup_logging
   from richcolorlog.logger import Check, ColorSupport

   # Check detected mode
   mode = Check()
   print(f"Detected color mode: {mode}")

   # Test all levels
   logger = setup_logging(level='DEBUG')

   logger.debug("Debug message")
   logger.info("Info message")
   logger.notice("Notice message")
   logger.warning("Warning message")
   logger.error("Error message")
   logger.critical("Critical message")
   logger.fatal("Fatal message")
   logger.alert("Alert message")
   logger.emergency("Emergency message")