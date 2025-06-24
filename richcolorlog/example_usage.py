#!/usr/bin/env python
"""
Example usage of the rich-logger package.
"""

import logging
from rich_logger import setup_logging, get_def


def main():
    """Main function demonstrating rich-logger usage."""
    # Setup the logger with enhanced features
    logger = setup_logging(
        show_locals=True,      # Show local variables in tracebacks
        logfile="example.log", # Custom log file
        level=logging.DEBUG    # Set minimum level
    )
    
    # Basic logging examples
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Custom log levels
    logger.emergency("This is an emergency!")
    logger.fatal("This is fatal!")
    logger.alert("This is an alert!")
    logger.notice("This is a notice")
    
    # Logging with context
    context = get_def()
    logger.info(f"{context}Logging from main function")
    
    # Exception handling example
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division by zero occurred!")
    
    # Code logging with syntax highlighting
    code_snippet = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
print(fibonacci(10))
    '''
    
    logger.info("Here's a Python code example:")
    # Note: To use syntax highlighting, you would need to modify the record
    # This is a simplified example
    logger.info(code_snippet)
    
    print("✅ Example completed! Check example.log for file output.")


class ExampleClass:
    """Example class to demonstrate context logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def example_method(self):
        """Example method with context logging."""
        context = get_def()
        self.logger.info(f"{context}Executing example method")
        
        # Simulate some work
        data = {"key": "value", "number": 42}
        self.logger.debug(f"{context}Processing data: {data}")
        
        return "Method completed successfully"


if __name__ == "__main__":
    main()
    
    # Test class-based logging
    obj = ExampleClass()
    result = obj.example_method()
    print(f"Result: {result}")