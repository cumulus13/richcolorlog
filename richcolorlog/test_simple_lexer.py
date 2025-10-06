from logger import getLogger, setup_logging

logger = getLogger('myapp')

# Log with syntax highlighting
code = """
def hello():
    print("Hello World")
"""

logger.info(code, lexer='python')  # Will be highlighted as a python code
logger.debug("SELECT * FROM users", lexer='sql')  # Will be highlighted as SQL
logger.debug("This is a debug message")

