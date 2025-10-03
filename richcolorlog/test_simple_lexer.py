from logger import getLogger, setup_logging

logger = getLogger('myapp')

# Log dengan syntax highlighting
code = """
def hello():
    print("Hello World")
"""

logger.info(code, lexer='python')  # Akan di-highlight sebagai Python code
logger.debug("SELECT * FROM users", lexer='sql')  # Akan di-highlight sebagai SQL
logger.debug("This is a debug message")

"""
Traceback (most recent call last):
  File "C:\PROJECTS\richcolorlog\richcolorlog\test_simple_lexer.py", line 3, in <module>
    logger = getLogger('myapp')
             ^^^^^^^^^^^^^^^^^^
  File "C:\PROJECTS\richcolorlog\richcolorlog\logger.py", line 1917, in getLogger
    formatter = CustomFormatter(
                ^^^^^^^^^^^^^^^^
  File "C:\PROJECTS\richcolorlog\richcolorlog\logger.py", line 365, in __init__
    self._build_formatters()
  File "C:\PROJECTS\richcolorlog\richcolorlog\logger.py", line 370, in _build_formatters
    logging.DEBUG: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['debug'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\sdk\anaconda3\Lib\logging\__init__.py", line 598, in __init__
    self._style.validate()
  File "c:\sdk\anaconda3\Lib\logging\__init__.py", line 438, in validate
    raise ValueError("Invalid format '%s' for '%s' style" % (self._fmt, self.default_format[0]))
ValueError: Invalid format '[{levelname}] {message}' for '%' style"""

# from logger import setup_logging

# logger = setup_logging(
#     name='myapp',
#     lexer='python',  # default lexer
#     show_icon=True,
#     show_background=True,
# )

# code = 'def hello():\n    print("Hello World")'
# logger.info(code, lexer='python')
# logger.debug("SELECT * FROM users", lexer='sql')