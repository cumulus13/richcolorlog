import os
from logger3 import setup_logging_custom

print("Test function (CustomFormatter), No Background Color.\n")

logger = setup_logging_custom(show_background=False)

logger.critical("This is a critical message")
logger.error("This is an error message")
logger.warning("This is a warning message")
logger.notice("This is a notice message")
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.emergency("This is a emergency message")
logger.alert("This is a alert message")
logger.fatal("This is a fatal message")

print("\n", "="*(os.get_terminal_size()[0] - 3), "\n")

print("Test function (CustomFormatter), Background Color.\n")

logger = setup_logging_custom(show_background=True)

logger.critical("This is a critical message")
logger.error("This is an error message")
logger.warning("This is a warning message")
logger.notice("This is a notice message")
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.emergency("This is a emergency message")
logger.alert("This is a alert message")
logger.fatal("This is a fatal message")

# print("Test function (CustomFormatter), LEXER + No Background Color.\n")
print("Test function (CustomFormatter), LEXER\n")

logger = setup_logging_custom(show_background=False)


code = """
    def hello():
        print("Hello World")
    """

logger.info(code, lexer='python')  # Akan di-highlight sebagai Python code
logger.debug("SELECT * FROM users", lexer='sql')  # Akan di-highlight sebagai SQL

# print("\nTest function (CustomFormatter), LEXER + Background Color.\n")

# logger = setup_logging_custom(show_background=True)


# code = """
#     def hello():
#         print("Hello World")
#     """

# logger.info(code, lexer='python')  # Akan di-highlight sebagai Python code
# logger.debug("SELECT * FROM users", lexer='sql')  # Akan di-highlight sebagai SQL
