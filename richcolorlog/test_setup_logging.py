#!/usr/bin/env python3
# file: richcolorlog/test_setup_logging.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-03 21:59:12.091172
# Description: 
# License: MIT

import os
# from logger3 import getLogger as setup_logging
from logger import setup_logging

print("Test function (CustomFormatter), No Background Color.\n")
FORMAT = "%(icon)s %(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
logger = setup_logging(show_background=False, format_template=FORMAT, name="TEST [1]")

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

logger = setup_logging(show_background=True, format_template=FORMAT, name="TEST [2]", level_in_message=True)

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
print("\n", "="*(os.get_terminal_size()[0] - 3), "\n")

print("Test function (CustomFormatter), LEXER\n")

logger = setup_logging(show_background=False, format_template=FORMAT, name="TEST [3]")


code = """
    def hello():
        print("Hello World")
    """

logger.info(code, lexer='python')  # Akan di-highlight sebagai Python code
logger.debug("SELECT * FROM users", lexer='sql')  # Akan di-highlight sebagai SQL

print("\n", "="*(os.get_terminal_size()[0] - 3), "\n")

print("\nTest function (CustomFormatter), LEXER + Background Color.\n")

logger = setup_logging(show_background=True, format_template=FORMAT, name="TEST [4]")


code = """
    def hello():
        print("Hello World")
    """

logger.info(code, lexer='python')  # Akan di-highlight sebagai Python code
logger.debug("SELECT * FROM users", lexer='sql')  # Akan di-highlight sebagai SQL


print("\n", "="*(os.get_terminal_size()[0] - 3), "\n")

print("Test function (CustomFormatter) + No Background + custom variable format \n")


FORMAT="%(asctime)s [%(levelname)s] %(name)s | user=%(user_id)s | %(message)s"
logger = setup_logging(show_background=False, format_template=FORMAT, name="TEST [5]")

# Logging dengan field kustom
logger.info("User logged in", extra={"user_id": "U12345"})

print("\n", "="*(os.get_terminal_size()[0] - 3), "\n")

print("Test function (CustomFormatter) + Background + custom variable format \n")


FORMAT="%(asctime)s [%(levelname)s] %(name)s | user=%(user_id)s | %(message)s"
logger = setup_logging(show_background=True, format_template=FORMAT, name="TEST [6]")

# Logging dengan field kustom
logger.info("User logged in", extra={"user_id": "U12345"})

