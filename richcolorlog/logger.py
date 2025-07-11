#!/usr/bin/env python
"""
Rich Logger - Enhanced logging with Rich formatting and custom levels.
"""

import logging
import os
import re
import inspect
import shutil
from typing import Optional, Union, Iterable, List
from types import ModuleType

try:
    from rich.logging import FormatTimeCallable
except ImportError:
    # Fallback type if Rich is not available
    from typing import Callable
    FormatTimeCallable = Callable[[float], str]

try:
    from rich.logging import RichHandler
    from rich.text import Text
    from rich.console import Console
    from rich.syntax import Syntax
    from rich import traceback as rich_traceback
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
class CustomFormatter(logging.Formatter):
    """Custom formatter with ANSI color codes for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'debug': "\x1b[38;2;255;170;0m",         # #FFAA00
        'info': "\x1b[38;2;0;255;255m",          # #00ffff
        'warning': "\x1b[30;48;2;255;255;0m",    # black on #ffff00
        'error': "\x1b[97;41m",                  # #ffffff on red
        'critical': "\x1b[97;48;2;85;0;0m",      # bright_white on #550000
        'fatal': "\x1b[97;48;2;0;85;255m",       # bright_white on #0055FF
        'emergency': "\x1b[97;48;2;170;0;255m",  # bright_white on #aa00ff
        'alert': "\x1b[97;48;2;0;85;0m",         # bright_white on #005500
        'notice': "\x1b[30;48;2;0;255;255m",     # black on #00ffff
        'reset': "\x1b[0m"
    }
    
    FORMAT_TEMPLATE = "%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(
        self,
        show_background=True,
        format_template=None,
        show_time=True,
        show_name=True,
        show_pid=True,
        show_level=True,
        show_path=True,
    ):
        super().__init__()
        # Build format template based on flags if not provided
        if format_template:
            self.FORMAT_TEMPLATE = format_template
        else:
            parts = []
            if show_time:
                parts.append("%(asctime)s")
            if show_name:
                parts.append("%(name)s")
            if show_pid:
                parts.append("%(process)d")
            if show_level:
                parts.append("%(levelname)s")
            parts.append("%(message)s")
            if show_path:
                parts.append("(%(filename)s:%(lineno)d)")
            self.FORMAT_TEMPLATE = " - ".join(parts)

        # The rest of the constructor continues below...if not show_background:
        if not show_background:
            # Remove background colors for all levels except those that are foreground only
            self.COLORS.update({
                'warning': "\x1b[38;2;255;255;0m",    # yellow
                'error': "\x1b[31m",                  # red
                'critical': "\x1b[38;2;85;0;0m",      # #550000
                'fatal': "\x1b[38;2;0;85;255m",       # #0055FF
                'emergency': "\x1b[38;2;170;0;255m",  # #aa00ff
                'alert': "\x1b[38;2;0;85;0m",         # #005500
                'notice': "\x1b[38;2;0;255;255m",     # #00ffff
            })
        
        self.formatters = {
            logging.DEBUG: logging.Formatter(self.COLORS['debug'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            logging.INFO: logging.Formatter(self.COLORS['info'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            logging.WARNING: logging.Formatter(self.COLORS['warning'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            logging.ERROR: logging.Formatter(self.COLORS['error'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            logging.CRITICAL: logging.Formatter(self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            CRITICAL_LEVEL: logging.Formatter(self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            EMERGENCY_LEVEL: logging.Formatter(self.COLORS['emergency'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            FATAL_LEVEL: logging.Formatter(self.COLORS['fatal'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            ALERT_LEVEL: logging.Formatter(self.COLORS['alert'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            NOTICE_LEVEL: logging.Formatter(self.COLORS['notice'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
        }

    def format(self, record):
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)

# Define custom log levels
EMERGENCY_LEVEL = logging.CRITICAL + 10
FATAL_LEVEL = EMERGENCY_LEVEL + 1
CRITICAL_LEVEL = FATAL_LEVEL + 1
ALERT_LEVEL = CRITICAL_LEVEL + 1
NOTICE_LEVEL = ALERT_LEVEL + 1

# Add custom level names
logging.addLevelName(EMERGENCY_LEVEL, "EMERGENCY")
logging.addLevelName(FATAL_LEVEL, "FATAL")
logging.addLevelName(CRITICAL_LEVEL, "CRITICAL")
logging.addLevelName(ALERT_LEVEL, "ALERT")
logging.addLevelName(NOTICE_LEVEL, "NOTICE")


def _add_custom_level_method(level_name: str, level_value: int):
    """Add a custom logging method to the Logger class."""
    def log_method(self, message, *args, **kwargs):
        if self.isEnabledFor(level_value):
            self._log(level_value, message, args, **kwargs)
    
    setattr(logging.Logger, level_name.lower(), log_method)


# Add custom logging methods
_add_custom_level_method("EMERGENCY", EMERGENCY_LEVEL)
_add_custom_level_method("FATAL", FATAL_LEVEL)
_add_custom_level_method("CRITICAL", CRITICAL_LEVEL)
_add_custom_level_method("ALERT", ALERT_LEVEL)
_add_custom_level_method("NOTICE", NOTICE_LEVEL)

if RICH_AVAILABLE:

    class CustomRichFormatter(logging.Formatter):
        """Custom Rich formatter with syntax highlighting support."""

        LEVEL_STYLES = {
            logging.DEBUG: "bold #FFAA00",
            logging.INFO: "bold #00ffff",
            logging.WARNING: "black on #ffff00",
            logging.ERROR: "#ffffff on red",
            logging.CRITICAL: "bright_white on #550000",
            FATAL_LEVEL: "bright_white on #0055FF",
            EMERGENCY_LEVEL: "bright_white on #aa00ff",
            ALERT_LEVEL: "bright_white on #005500",
            NOTICE_LEVEL: "black on #00ffff",
            CRITICAL_LEVEL: "bright_white on #550000",
        }
        
        def __init__(self, lexer = None, show_background = True):
            super().__init__()
            # Define styles for different log levels
            self.lexer = lexer
            if not show_background:
                self.LEVEL_STYLES.update({
                    logging.WARNING: "#ffff00",
                    logging.ERROR: "red",
                    logging.CRITICAL: "bold #550000",
                    FATAL_LEVEL: "#0055FF",
                    EMERGENCY_LEVEL: "#aa00ff",
                    ALERT_LEVEL: "#005500",
                    NOTICE_LEVEL: "#00ffff",
                    CRITICAL_LEVEL: "#550000",
                    logging.INFO: "bold #00FF00",
                })
        
        def format(self, record):
            """Format log record with Rich styling and optional syntax highlighting."""
            lexer = getattr(record, "lexer", self.lexer or None)
            level_style = self.LEVEL_STYLES.get(record.levelno, "")
            prefix = f"{record.levelname} - ({record.filename}:{record.lineno}) "
            prefix_text = Text(prefix, style=level_style)
            # print(f"lexer: {lexer}, level: {record.levelno}, style: {level_style}")
            if lexer:
                try:
                    # Apply syntax highlighting
                    syntax = Syntax(
                        record.getMessage(), 
                        lexer, 
                        theme="fruity", 
                        line_numbers=False
                    )
                    text_obj = syntax.highlight(record.getMessage())
                    if text_obj.plain.endswith("\n"):
                        text_obj = text_obj[:-1]
                    prefix_text.append(text_obj)
                    return prefix_text
                except Exception:
                    # Fallback if syntax highlighting fails
                    pass
            
            # Handle Text objects
            if isinstance(record.msg, Text):
                return record.msg
                
            # Default formatting
            log_fmt = f"{record.levelname} - {record.getMessage()} ({record.filename}:{record.lineno})"
            return Text(log_fmt, style=level_style)
else:
    # Fallback: CustomRichFormatter = CustomFormatter
    CustomRichFormatter = CustomFormatter

def setup_logging_custom(
    level: Union[str, int] = 'DEBUG',
    show_background = True,
    format_template=None,
    show_time=True,
    show_name=True,
    show_pid=True,
    show_level=True,
    show_path=True,
    exceptions = []
    ):
    """Setup basic logging with custom formatter (ANSI colors)."""
    if isinstance(level, str):
        logging.basicConfig(level=getattr(logging, level))
    else:
        logging.basicConfig(level=level)

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): logging.getLogger(str(i)).setLevel('CRITICAL')

    logger = logging.getLogger()

    # Update handlers with custom formatter
    for handler in logger.handlers:
        handler.setFormatter(CustomFormatter(
                show_background,
                format_template,
                show_time,
                show_name,
                show_pid,
                show_level,
                show_path,
            )
        )
    
    return logger

def setup_logging(
    lexer: Optional[str] = None,
    logfile: Optional[str] = None, 
    show_locals: bool = False, 
    level: Union[str, int] = 'DEBUG',
    show_level: bool = False,
    show_time: bool = True,
    omit_repeated_times: bool = True,
    show_path: bool = True,
    enable_link_path: bool = True,
    highlighter = None,
    markup: bool = False,
    rich_tracebacks: bool = False,
    tracebacks_width: Optional[int] = None,
    tracebacks_extra_lines: int = 3,
    tracebacks_theme: Optional[str] = None,
    tracebacks_word_wrap: bool = True,
    tracebacks_show_locals: bool = False,
    tracebacks_suppress: Iterable[Union[str, ModuleType]] = (),
    locals_max_length: int = 10,
    locals_max_string: int = 80,
    log_time_format: Union[str, FormatTimeCallable] = "[%x %X]",
    keywords: Optional[List[str]] = None,
    show_background = True,
    exceptions = []
) -> logging.Logger:
    """
    Setup enhanced logging with Rich formatting.
    
    Args:
        show_locals: Show local variables in tracebacks
        logfile: Path to log file (auto-generated if None)
        lexer: Syntax highlighter for code (e.g., 'python', 'javascript')
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    
    # print(f"Setting up logging with level: {level}, show_locals: {show_locals}, logfile: {logfile}, lexer: {lexer}")
    # Auto-generate logfile name if not provided
    # if logfile is None:
    #     try:
    #         main_file = inspect.stack()[-1].filename
    #         base = os.path.splitext(os.path.basename(main_file))[0]
    #         logfile = f"{base}.log"
    #     except (IndexError, AttributeError):
    #         logfile = "app.log"

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): logging.getLogger(str(i)).setLevel('CRITICAL')
    
    if isinstance(level, str):
        logging.basicConfig(level=getattr(logging, level))
    else:
        logging.basicConfig(level=level)
    
    if logfile is None:
        try:
            main_file = inspect.stack()[-1].filename
            # Check if it contains an invalid character or not a python file
            if not main_file or main_file.startswith('<') or not main_file.endswith(('.py', '.pyc')):
                logfile = "app.log"
            else:
                base = os.path.splitext(os.path.basename(main_file))[0]
                logfile = f"{base}.log"
        except Exception as e:
            logfile = "app.log"
    
    # Setup Rich handler for console
    rich_handler = RichHandler(
        show_time = show_time,
        omit_repeated_times = omit_repeated_times,
        show_level = show_level,
        show_path = show_path,
        enable_link_path = enable_link_path,
        highlighter = highlighter,
        markup = markup,
        rich_tracebacks = rich_tracebacks,
        tracebacks_width = tracebacks_width or shutil.get_terminal_size()[0],
        tracebacks_extra_lines = tracebacks_extra_lines,
        tracebacks_theme = tracebacks_theme or 'fruity',
        tracebacks_word_wrap = tracebacks_word_wrap,
        tracebacks_show_locals = tracebacks_show_locals,
        tracebacks_suppress = tracebacks_suppress,
        locals_max_length = locals_max_length,
        locals_max_string = locals_max_string,
        log_time_format = log_time_format,
        keywords = keywords,
    )
    rich_handler._log_render.emojis = False
    rich_handler.setFormatter(CustomRichFormatter(lexer, show_background))

    # Setup file handler
    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    ))

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)
    
    # Patch RichHandler to handle Text objects properly
    def custom_render_message(self, record, message):
        use_markup = getattr(record, "markup", self.markup)
        if isinstance(message, Text):
            return message
        else:
            return Text.from_markup(message) if use_markup else Text(message)
    
    # Apply patch to RichHandler
    for handler in logger.handlers:
        if isinstance(handler, RichHandler):
            handler.render_message = custom_render_message.__get__(handler)
    
    return logger


def get_def() -> str:
    """
    Get current function/class definition name for logging context.
    
    Returns:
        Formatted string with function/class context
    """
    name = ''
    
    try:
        # Try to get function name from stack
        frame = inspect.stack()[1]
        name = str(frame.function)
    except (IndexError, AttributeError) as e:
        logging.exception("Error getting name from stack[1]: %s", e)
    
    # Fallback to stack[2] if needed
    if not name:
        try:
            frame = inspect.stack()[2]
            name = str(frame.function)
        except (IndexError, AttributeError) as e:
            logging.exception("Error getting name from stack[2]: %s", e)
    
    # Handle module-level calls
    if not name or name == "<module>":
        # Try to get class name
        try:
            frame = inspect.stack()[1]
            self_obj = frame.frame.f_locals.get('self')
            if self_obj:
                class_name = self_obj.__class__.__name__
                if class_name != "NoneType":
                    name = f"[#00ffff]({class_name}) --> "
        except Exception as e:
            logging.exception("Error getting class from stack[1]: %s", e)
        
        # Look for calling function in stack
        if not name or name == "<module>":
            try:
                for frame_info in inspect.stack()[3:]:
                    if isinstance(frame_info.lineno, int) and frame_info.function != '<module>':
                        name = f"[#ff5500]{frame_info.function}\\[[white on red]{frame_info.lineno}][/] --> "
                        break
            except Exception as e:
                logging.exception("Error scanning stack: %s", e)
    
    # Ultimate fallback to filename
    if not name or name == "<module>":
        try:
            filename = os.path.basename(inspect.stack()[0].filename)
            name = filename
        except Exception as e:
            logging.exception("Error getting filename: %s", e)
            name = "unknown"
    
    return name or "unknown"

def test():
    logger = setup_logging_custom()
    try:
        console.print("[italic]Test function to verify logger setup (CustomFormatter).[/]\n")
    except:
        print("Test function to verify logger setup (CustomFormatter).\n")
    logger.emergency("This is an emergency message")
    logger.critical("This is a critical message")
    logger.alert("This is an alert message")
    logger.fatal("This is a fatal message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    print("=" * shutil.get_terminal_size()[0])
    
    logger = setup_logging_custom(show_background = False)
    try:
        console.print("[italic]Test function to verify logger setup (CustomFormatter), No Background Color.[/]\n")
    except:
        print("Test function to verify logger setup (CustomFormatter), No Background Color.\n")
    logger.emergency("This is an emergency message")
    logger.critical("This is a critical message")
    logger.alert("This is an alert message")
    logger.fatal("This is a fatal message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    print("=" * shutil.get_terminal_size()[0])
    
    logger = setup_logging()
    
    try:
        console.print("[italic]Test function to verify logger setup (CustomRichFormatter).[/]\n")
    except:
        print("Test function to verify logger setup (CustomRichFormatter).\n")
    logger.emergency("This is an emergency message")
    logger.critical("This is a critical message")
    logger.alert("This is an alert message")
    logger.fatal("This is a fatal message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    print("=" * shutil.get_terminal_size()[0])
    
    logger = setup_logging(show_background = False)
    
    try:
        console.print("[italic]Test function to verify logger setup (CustomRichFormatter), No Background Color.[/]\n")
    except:
        print("Test function to verify logger setup (CustomRichFormatter), No Background Color.\n")
    logger.emergency("This is an emergency message")
    logger.critical("This is a critical message")
    logger.alert("This is an alert message")
    logger.fatal("This is a fatal message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    
if __name__ == "__main__":
    # Run test if executed directly
    test()
    # Example usage of get_def
    print(f"get_def(): {get_def()}")