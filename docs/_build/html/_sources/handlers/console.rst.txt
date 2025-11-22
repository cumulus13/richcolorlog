===============
Console Handler
===============

RichColorLog provides two console handlers: ``RichColorLogHandler`` (Rich-based) and ``AnsiLogHandler`` (ANSI-based).

RichColorLogHandler
-------------------

The default handler when Rich library is available. Provides beautiful, feature-rich output.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from richcolorlog import setup_logging

   # Uses RichColorLogHandler by default
   logger = setup_logging()
   logger.info("Beautiful Rich output!")

Features
~~~~~~~~

- Table-based layout for alignment
- Syntax highlighting for code
- Rich markup support
- Emoji icons
- Traceback formatting
- Customizable themes

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       # Display options
       show_time=True,
       show_level=True,
       show_path=True,
       show_icon=True,
       icon_first=True,
       omit_repeated_times=True,

       # Appearance
       show_background=True,
       theme='fruity',
       markup=True,

       # Tracebacks
       rich_tracebacks=True,
       tracebacks_show_locals=True,
       tracebacks_width=100,
       tracebacks_code_width=88,
   )

AnsiLogHandler
--------------

A simpler handler using ANSI escape codes. Works without Rich library.

When to Use
~~~~~~~~~~~

- Environments without Rich installed
- Simpler output requirements
- Better compatibility with some terminals
- IPython/Jupyter notebooks

Usage
~~~~~

.. code-block:: python

   from richcolorlog import setup_logging_custom

   # Forces ANSI handler
   logger = setup_logging_custom(
       show_background=True,
       format_template="[%(levelname)s] %(message)s",
       show_time=True,
       show_path=True,
       show_icon=True,
       icon_first=True,
   )

Or explicitly disable Rich:

.. code-block:: python

   from richcolorlog import setup_logging
   from richcolorlog.logger import AnsiLogHandler

   logger = setup_logging(
       HANDLER=AnsiLogHandler,
   )

Format Template
~~~~~~~~~~~~~~~

The ANSI handler uses format templates:

.. code-block:: python

   logger = setup_logging_custom(
       format_template="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   )

Handler Parameters
------------------

Both handlers share common parameters:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``lexer``
     - ``None``
     - Pygments lexer for syntax highlighting
   * - ``show_background``
     - ``True``
     - Enable background colors
   * - ``show_icon``
     - ``True``
     - Show emoji icons
   * - ``icon_first``
     - ``True``
     - Icon position (before time vs after message)
   * - ``level_in_message``
     - ``False``
     - Include level name in message text

RichColorLogHandler-Specific
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``render_emoji``
     - ``True``
     - Render emoji characters
   * - ``theme``
     - ``'fruity'``
     - Pygments syntax theme
   * - ``console``
     - ``None``
     - Rich Console instance
   * - ``markup``
     - ``False``
     - Enable Rich markup parsing
   * - ``rich_tracebacks``
     - ``False``
     - Use Rich traceback formatting
   * - ``tracebacks_show_locals``
     - ``False``
     - Show local variables in tracebacks
   * - ``show_type``
     - ``False``
     - Show message type info

Creating Custom Console Handler
-------------------------------

Extend the base handlers:

.. code-block:: python

   from richcolorlog.logger import RichColorLogHandler

   class MyCustomHandler(RichColorLogHandler):
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           # Custom initialization

       def emit(self, record):
           # Custom emit logic
           # Add prefix/suffix, transform message, etc.
           super().emit(record)

   # Use custom handler
   from richcolorlog import setup_logging

   logger = setup_logging(HANDLER=MyCustomHandler)

Multiple Console Handlers
-------------------------

Add multiple console handlers with different configurations:

.. code-block:: python

   import logging
   from richcolorlog import setup_logging
   from richcolorlog.logger import AnsiLogHandler

   # Primary Rich handler
   logger = setup_logging(name='myapp', level='DEBUG')

   # Add secondary ANSI handler for stderr
   import sys
   stderr_handler = AnsiLogHandler()
   stderr_handler.setLevel(logging.ERROR)
   stderr_handler.stream = sys.stderr
   logger.addHandler(stderr_handler)

IPython/Jupyter Support
-----------------------

For notebooks, use the simple logger:

.. code-block:: python

   from richcolorlog import getLoggerSimple

   # Optimized for notebooks
   logger = getLoggerSimple(
       name='notebook',
       show_icon=True,
       icon_first=False,
       show_background=True,
   )

   logger.info("Works in Jupyter!")

This avoids async warnings and Rich detection issues in notebook environments.

Performance Considerations
--------------------------

For high-throughput logging:

.. code-block:: python

   logger = setup_logging(
       # Reduce processing overhead
       show_icon=False,
       show_path=False,
       omit_repeated_times=True,
       rich_tracebacks=False,
       markup=False,

       # Or use simpler ANSI handler
       HANDLER=AnsiLogHandler,
   )