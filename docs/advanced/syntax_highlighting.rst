===================
Syntax Highlighting
===================

RichColorLog supports syntax highlighting in log messages using Pygments.

Requirements
------------

.. code-block:: bash

   pip install pygments

Basic Usage
-----------

Global Lexer
~~~~~~~~~~~~

Apply syntax highlighting to all messages:

.. code-block:: python

   from richcolorlog import setup_logging

   # All messages treated as Python code
   logger = setup_logging(lexer='python')

   code = '''
   def hello():
       print("Hello World!")
   '''
   logger.debug(code)

Per-Message Lexer
~~~~~~~~~~~~~~~~~

Specify lexer for individual messages:

.. code-block:: python

   logger = setup_logging()

   code = """def greeting(name):
                 print(f"Hello {name} !")"""

   # Python code
   logger.info(code, extra={'lexer': 'python'})
   logger.debug(code, extra={'lexer': 'python'})

   logger.info(code, lexer='python')
   logger.debug(code, extra={'lexer': 'python'})

   code = """SELECT * FROM clients"""

   # SQL
   logger.info(code, extra={'lexer': 'sql'})
   logger.debug("SELECT * FROM users", extra={'lexer': 'sql'})

   logger.info(code, lexer= 'sql')
   logger.debug("SELECT * FROM users", lexer='sql')

   # JSON
   logger.debug('{"key": "value"}', extra={'lexer': 'json'})
   logger.debug('{"key": "value"}', lexer=json')

Available Lexers
----------------

Common lexers:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Lexer
     - Description
   * - ``python``
     - Python code
   * - ``sql``
     - SQL queries
   * - ``json``
     - JSON data
   * - ``yaml``
     - YAML configuration
   * - ``xml``
     - XML markup
   * - ``html``
     - HTML markup
   * - ``javascript``
     - JavaScript code
   * - ``bash``
     - Bash/shell scripts
   * - ``java``
     - Java code
   * - ``cpp``
     - C++ code
   * - ``go``
     - Go code
   * - ``rust``
     - Rust code
   * - ``ruby``
     - Ruby code
   * - ``php``
     - PHP code

See `Pygments lexers <https://pygments.org/docs/lexers/>`_ for full list.

Themes
------

Change the syntax highlighting theme:

.. code-block:: python

   logger = setup_logging(
       lexer='python',
       theme='monokai',  # Dark theme
   )

Popular themes:

- ``monokai`` - Dark with vibrant colors
- ``fruity`` - Dark (default)
- ``native`` - Dark, native look
- ``vim`` - Vim-like colors
- ``vs`` - Visual Studio light
- ``friendly`` - Light, friendly colors
- ``colorful`` - Colorful light theme

See `Pygments styles <https://pygments.org/styles/>`_ for full list.

Rich Handler Highlighting
-------------------------

The Rich handler uses Rich's Syntax for highlighting:

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       lexer='python',
       theme='monokai',
   )

   # Syntax highlighting with Rich formatting
   logger.debug('''
   def calculate(x, y):
       """Calculate sum."""
       return x + y
   ''')

ANSI Handler Highlighting
-------------------------

The ANSI handler uses Pygments TerminalFormatter:

.. code-block:: python

   from richcolorlog import setup_logging_custom

   logger = setup_logging_custom(lexer='python')

   # Pygments terminal highlighting
   logger.debug("print('hello world')")
   # Or
   logger.debug("print('hello world')", lexer='python')

Auto-Detection
--------------

Create a helper for automatic lexer detection:

.. code-block:: python

   import re

   def detect_lexer(text):
       """Detect appropriate lexer for text."""
       patterns = {
           'json': r'^\s*[\[{]',
           'xml': r'^\s*<[?!]?[a-zA-Z]',
           'sql': r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b',
           'python': r'^\s*(def |class |import |from |if |for |while )',
           'yaml': r'^\s*[a-zA-Z_]+:\s*\n',
       }

       for lexer, pattern in patterns.items():
           if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
               return lexer

       return None

   # Usage
   data = '{"key": "value"}'
   lexer = detect_lexer(data)
   logger.debug(data, lexer=lexer)

Logging Decorated Code
----------------------

Log function source code:

.. code-block:: python

   import inspect
   from functools import wraps

   def log_source(logger):
       """Decorator to log function source code."""
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               source = inspect.getsource(func)
               logger.debug(f"Executing:\n{source}", extra={'lexer': 'python'})
               return func(*args, **kwargs)
           return wrapper
       return decorator

   @log_source(logger)
   def my_function(x, y):
       return x + y

Logging Data Structures
-----------------------

Pretty-print data with highlighting:

.. code-block:: python

   import json
   import yaml

   def log_json(logger, data, level='debug'):
       """Log data as formatted JSON."""
       formatted = json.dumps(data, indent=2)
       getattr(logger, level)(formatted, extra={'lexer': 'json'})

   def log_yaml(logger, data, level='debug'):
       """Log data as YAML."""
       formatted = yaml.dump(data, default_flow_style=False)
       getattr(logger, level)(formatted, extra={'lexer': 'yaml'})

   # Usage
   config = {'database': {'host': 'localhost', 'port': 5432}}
   log_json(logger, config)
   log_yaml(logger, config)

Performance Considerations
--------------------------

Syntax highlighting adds processing overhead:

.. code-block:: python

   # Disable for production
   import os

   logger = setup_logging(
       lexer='python' if os.getenv('DEBUG') else None,
   )

   # Or use conditional highlighting
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug(code, extra={'lexer': 'python'})