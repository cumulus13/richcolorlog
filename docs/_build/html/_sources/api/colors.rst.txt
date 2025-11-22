==========
Colors API
==========

Classes for color detection and color scheme management.

ColorSupport
------------

.. py:class:: ColorSupport

   Constants for color support levels.

   .. py:attribute:: TRUECOLOR
      :value: "truecolor"

      24-bit color (16.7 million colors).

   .. py:attribute:: COLOR_256
      :value: "256color"

      256 color palette.

   .. py:attribute:: BASIC
      :value: "basic"

      8/16 basic ANSI colors.

   .. py:attribute:: NONE
      :value: "none"

      No color support.

Check
-----

.. py:class:: Check

   Auto-detect terminal color support across all major OS.

   Returns detected color mode when instantiated (not an instance).

   :param force: Force a specific color mode.
   :type force: str, optional
   :returns: Detected or forced color support level.
   :rtype: str

   .. py:staticmethod:: enable_windows_ansi() -> bool

      Enable ANSI processing on Windows.

      :returns: True if successful.
      :rtype: bool

   .. py:classmethod:: detect_color_support(force=None) -> str

      Detect terminal color capabilities.

      :param force: Force a specific mode.
      :type force: str, optional
      :returns: Color support level.
      :rtype: str

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import Check, ColorSupport

      # Auto-detect
      mode = Check()
      print(f"Detected: {mode}")

      # Force specific mode
      mode = Check(force=ColorSupport.TRUECOLOR)

Colors
------

.. py:class:: Colors(color_type='ansi', show_background=False, **color_overrides)

   Handler for color schemes with various format output.

   :param color_type: Output format ('ansi' or 'rich').
   :type color_type: str
   :param show_background: Include background colors.
   :type show_background: bool
   :param emergency_color: Custom emergency color.
   :type emergency_color: str
   :param alert_color: Custom alert color.
   :type alert_color: str
   :param critical_color: Custom critical color.
   :type critical_color: str
   :param error_color: Custom error color.
   :type error_color: str
   :param warning_color: Custom warning color.
   :type warning_color: str
   :param fatal_color: Custom fatal color.
   :type fatal_color: str
   :param notice_color: Custom notice color.
   :type notice_color: str
   :param debug_color: Custom debug color.
   :type debug_color: str
   :param info_color: Custom info color.
   :type info_color: str

   .. py:method:: check() -> dict

      Detect and return color scheme according to terminal support.

      :returns: Dictionary of color codes by level.
      :rtype: dict

   .. py:method:: rich_color(show_background=False) -> dict

      Return color scheme in Rich library format.

      :param show_background: Include background colors.
      :type show_background: bool
      :returns: Dictionary of Rich style strings by level.
      :rtype: dict

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import Colors

      # ANSI colors with background
      colors = Colors(color_type='ansi', show_background=True)
      scheme = colors.check()
      print(scheme['error'])  # ANSI escape code

      # Rich colors without background
      colors = Colors(color_type='rich', show_background=False)
      scheme = colors.check()
      print(scheme['error'])  # "red"

      # Custom colors
      colors = Colors(
          color_type='rich',
          show_background=True,
          error_color='bold white on dark_red',
          warning_color='black on bright_yellow',
      )

SafeDict
--------

.. py:class:: SafeDict(dict)

   Dictionary that returns None for missing keys instead of raising KeyError.

   .. py:method:: __missing__(key)

      Return None for missing keys.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import SafeDict

      d = SafeDict({'a': 1})
      print(d['a'])  # 1
      print(d['b'])  # None (no KeyError)

Default Color Schemes
---------------------

TrueColor with Background
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   {
       'debug': "#000000 on #FFAA00",      # Black on orange
       'info': "#000000 on #00FF00",       # Black on green
       'notice': "#000000 on #00FFFF",     # Black on cyan
       'warning': "black on #FFFF00",      # Black on yellow
       'error': "white on red",            # White on red
       'critical': "bright_white on #0000FF",  # White on blue
       'fatal': "blue on #FF557F",         # Blue on pink
       'alert': "bright_white on #005500", # White on dark green
       'emergency': "bright_white on #AA00FF",  # White on purple
   }

TrueColor Foreground Only
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   {
       'debug': "#FFAA00",     # Orange
       'info': "#00FF00",      # Green
       'notice': "#00FFFF",    # Cyan
       'warning': "#FFFF00",   # Yellow
       'error': "red",         # Red
       'critical': "#0000FF",  # Blue
       'fatal': "#FF557F",     # Pink
       'alert': "#005500",     # Dark green
       'emergency': "#AA00FF", # Purple
   }

ANSI Escape Codes
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # TrueColor (24-bit)
   '\x1b[38;2;R;G;Bm'           # Foreground RGB
   '\x1b[48;2;R;G;Bm'           # Background RGB
   '\x1b[38;2;R;G;B;48;2;R;G;Bm'  # Both

   # 256 Color
   '\x1b[38;5;Nm'  # Foreground (N = 0-255)
   '\x1b[48;5;Nm'  # Background

   # Basic (8/16)
   '\x1b[30-37m'   # Foreground (30=black, 31=red, ...)
   '\x1b[40-47m'   # Background
   '\x1b[90-97m'   # Bright foreground
   '\x1b[100-107m' # Bright background

   # Reset
   '\x1b[0m'