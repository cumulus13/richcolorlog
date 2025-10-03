#!/usr/bin/env python3
"""
Enhanced Rich Logger - Production-ready logging with Rich formatting and custom levels.

This module provides a comprehensive logging solution with:
- Rich console formatting with syntax highlighting
- Custom log levels (EMERGENCY, FATAL, ALERT, NOTICE)
- Flexible configuration options
- Production-ready error handling
- Performance optimizations
- Thread-safe operations
- Log rotation support
- Structured logging capabilities
"""

import logging
import logging.handlers
import os
import sys
import re
import inspect
import shutil
import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Iterable, List, Dict, Any, Callable
from types import ModuleType
from functools import lru_cache, wraps

# Version info
__version__ = "2.0.0"
__author__ = "Enhanced Logger"

# Thread-local storage for context
_local = threading.local()

try:
    from rich.logging import FormatTimeCallable, RichHandler
    from rich.text import Text
    from rich.console import Console
    from rich.syntax import Syntax
    from rich import traceback as rich_traceback
    from rich.markup import escape
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback types
    from typing import Callable
    FormatTimeCallable = Callable[[float], str]
    RichHandler = None
    Text = str
    console = None


class LoggerError(Exception):
    """Custom exception for logger-related errors."""
    pass


class PerformanceTracker:
    """Track performance metrics for logging operations."""
    
    def __init__(self):
        self._metrics = {}
        self._lock = threading.Lock()
    
    def record(self, operation: str, duration: float):
        """Record performance metric."""
        with self._lock:
            if operation not in self._metrics:
                self._metrics[operation] = []
            self._metrics[operation].append(duration)
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        with self._lock:
            stats = {}
            for operation, times in self._metrics.items():
                if times:
                    stats[operation] = {
                        'count': len(times),
                        'avg': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times)
                    }
            return stats


# Global performance tracker
_performance = PerformanceTracker()


def performance_monitor(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            _performance.record(func.__name__, duration)
    return wrapper


class SafeDict(dict):
    """Dictionary that doesn't raise KeyError, returns None instead."""
    
    def __missing__(self, key):
        return None


class StructuredFormatter(logging.Formatter):
    """Formatter for structured logging output (JSON)."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format record as JSON structure."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom attributes
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info'):
                log_data[key] = value
        
        try:
            return json.dumps(log_data, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            # Fallback to string representation
            log_data['_json_error'] = str(e)
            return json.dumps(log_data, default=str, ensure_ascii=False, skipkeys=True)


class CustomFormatter(logging.Formatter):
    """Enhanced custom formatter with ANSI color codes and better error handling."""
    
    # ANSI color codes with fallback support
    COLORS = SafeDict({
        'DEBUG': "\x1b[38;2;255;170;0m",         # #FFAA00
        'INFO': "\x1b[38;2;0;255;255m",          # #00FFFF
        'WARNING': "\x1b[30;48;2;255;255;0m",    # black on #FFFF00
        'ERROR': "\x1b[97;41m",                  # white on red
        'CRITICAL': "\x1b[97;48;2;85;0;0m",      # white on #550000
        'FATAL': "\x1b[97;48;2;0;85;255m",       # white on #0055FF
        'EMERGENCY': "\x1b[97;48;2;170;0;255m",  # white on #AA00FF
        'ALERT': "\x1b[97;48;2;0;85;0m",         # white on #005500
        'NOTICE': "\x1b[30;48;2;0;255;255m",     # black on #00FFFF
        'RESET': "\x1b[0m"
    })
    
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(
        self,
        show_background: bool = True,
        format_template: Optional[str] = None,
        show_time: bool = True,
        show_name: bool = True,
        show_pid: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        use_colors: bool = True,
    ):
        """Initialize CustomFormatter with enhanced options."""
        super().__init__()
        self.use_colors = use_colors and self._supports_color()
        
        # Build format template
        if format_template:
            self.format_template = format_template
        else:
            self.format_template = self._build_format_template(
                show_time, show_name, show_pid, show_level, show_path
            )
        
        # Adjust colors for background preference
        if not show_background:
            self.COLORS.update({
                'WARNING': "\x1b[38;2;255;255;0m",    # yellow
                'ERROR': "\x1b[31m",                  # red
                'CRITICAL': "\x1b[38;2;85;0;0m",      # #550000
                'FATAL': "\x1b[38;2;0;85;255m",       # #0055FF
                'EMERGENCY': "\x1b[38;2;170;0;255m",  # #AA00FF
                'ALERT': "\x1b[38;2;0;85;0m",         # #005500
                'NOTICE': "\x1b[38;2;0;255;255m",     # #00FFFF
            })
        
        # Pre-build formatters for performance
        self._build_formatters()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports color output."""
        try:
            return (
                hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
                os.environ.get('TERM') != 'dumb' and
                os.environ.get('NO_COLOR') is None
            )
        except (AttributeError, OSError):
            return False
    
    def _build_format_template(self, show_time, show_name, show_pid, show_level, show_path) -> str:
        """Build format template based on options."""
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
        return " - ".join(parts)
    
    def _build_formatters(self):
        """Pre-build formatters for all log levels."""
        self.formatters = {}
        for level_name in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 
                          'FATAL', 'EMERGENCY', 'ALERT', 'NOTICE']:
            level_value = getattr(logging, level_name, None) or globals().get(f"{level_name}_LEVEL")
            if level_value and self.use_colors:
                color = self.COLORS[level_name]
                reset = self.COLORS['RESET']
                format_str = f"{color}{self.format_template}{reset}"
            else:
                format_str = self.format_template
            
            self.formatters[level_value] = logging.Formatter(format_str)

    @performance_monitor
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with appropriate styling."""
        try:
            formatter = self.formatters.get(record.levelno)
            if formatter:
                return formatter.format(record)
            return super().format(record)
        except Exception as e:
            # Fallback formatting to prevent logging failures
            return f"[FORMATTER ERROR] {record.getMessage()} - {str(e)}"


# Define custom log levels with proper ordering
EMERGENCY_LEVEL = 60
FATAL_LEVEL = 55
CRITICAL_LEVEL = 50  # Same as logging.CRITICAL
ALERT_LEVEL = 45
NOTICE_LEVEL = 25

# Standard levels for reference
DEBUG = logging.DEBUG      # 10
INFO = logging.INFO        # 20
WARNING = logging.WARNING  # 30
ERROR = logging.ERROR      # 40

# Add custom level names
logging.addLevelName(EMERGENCY_LEVEL, "EMERGENCY")
logging.addLevelName(FATAL_LEVEL, "FATAL")
logging.addLevelName(ALERT_LEVEL, "ALERT")
logging.addLevelName(NOTICE_LEVEL, "NOTICE")


def _add_custom_level_method(level_name: str, level_value: int):
    """Add a custom logging method to the Logger class."""
    def log_method(self, message, *args, **kwargs):
        if self.isEnabledFor(level_value):
            self._log(level_value, message, args, **kwargs)
    
    # Add to Logger class
    method_name = level_name.lower()
    setattr(logging.Logger, method_name, log_method)


# Add custom logging methods
_add_custom_level_method("EMERGENCY", EMERGENCY_LEVEL)
_add_custom_level_method("FATAL", FATAL_LEVEL)
_add_custom_level_method("ALERT", ALERT_LEVEL)
_add_custom_level_method("NOTICE", NOTICE_LEVEL)


if RICH_AVAILABLE:
    class EnhancedRichFormatter(logging.Formatter):
        """Enhanced Rich formatter with better performance and error handling."""

        LEVEL_STYLES = SafeDict({
            logging.DEBUG: "bold #FFAA00",
            logging.INFO: "bold #00FFFF",
            logging.WARNING: "black on #FFFF00",
            logging.ERROR: "#FFFFFF on red",
            logging.CRITICAL: "bright_white on #550000",
            FATAL_LEVEL: "bright_white on #0055FF",
            EMERGENCY_LEVEL: "bright_white on #AA00FF",
            ALERT_LEVEL: "bright_white on #005500",
            NOTICE_LEVEL: "black on #00FFFF",
        })
        
        def __init__(self, lexer: Optional[str] = None, show_background: bool = True, theme: str = "fruity"):
            """Initialize EnhancedRichFormatter."""
            super().__init__()
            self.lexer = lexer
            self.theme = theme
            
            if not show_background:
                self.LEVEL_STYLES.update({
                    logging.WARNING: "#FFFF00",
                    logging.ERROR: "red",
                    logging.CRITICAL: "bold #550000",
                    FATAL_LEVEL: "#0055FF",
                    EMERGENCY_LEVEL: "#AA00FF",
                    ALERT_LEVEL: "#005500",
                    NOTICE_LEVEL: "#00FFFF",
                })
        
        @performance_monitor
        def format(self, record: logging.LogRecord) -> Union[Text, str]:
            """Format log record with Rich styling."""
            try:
                lexer = getattr(record, "lexer", self.lexer or None)
                level_style = self.LEVEL_STYLES[record.levelno] or ""
                
                # Build prefix
                prefix = f"{record.levelname} - ({record.filename}:{record.lineno}) "
                prefix_text = Text(prefix, style=level_style)
                
                # Handle syntax highlighting
                if lexer and hasattr(record, 'msg'):
                    try:
                        message = record.getMessage()
                        syntax = Syntax(
                            message, 
                            lexer, 
                            theme=self.theme, 
                            line_numbers=False,
                            word_wrap=True
                        )
                        text_obj = syntax.highlight(message)
                        if text_obj.plain.endswith("\n"):
                            text_obj = text_obj[:-1]
                        prefix_text.append(text_obj)
                        return prefix_text
                    except Exception:
                        # Fall through to default handling
                        pass
                
                # Handle Text objects
                if isinstance(record.msg, Text):
                    prefix_text.append(record.msg)
                    return prefix_text
                    
                # Default formatting
                message = record.getMessage()
                # Escape Rich markup to prevent injection
                safe_message = escape(message) if hasattr(record, '_safe_markup') else message
                log_text = Text(safe_message, style=level_style)
                prefix_text.append(log_text)
                return prefix_text
                
            except Exception as e:
                # Fallback to string formatting
                return f"[RICH FORMATTER ERROR] {record.getMessage()} - {str(e)}"
else:
    # Fallback when Rich is not available
    EnhancedRichFormatter = CustomFormatter


@lru_cache(maxsize=128)
def _get_caller_info(skip_frames: int = 2) -> tuple:
    """Get caller information with caching for performance."""
    try:
        frame = inspect.stack()[skip_frames]
        return frame.filename, frame.function, frame.lineno
    except (IndexError, AttributeError):
        return "<unknown>", "<unknown>", 0


class LoggerFactory:
    """Factory class for creating and managing logger instances."""
    
    _instances = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None, **kwargs) -> logging.Logger:
        """Get or create a logger instance with caching."""
        if name is None:
            try:
                # Auto-detect logger name from caller
                filename, _, _ = _get_caller_info(skip_frames=3)
                name = Path(filename).stem
            except Exception:
                name = "app"
        
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = cls._create_logger(name, **kwargs)
            return cls._instances[name]
    
    @classmethod
    def _create_logger(cls, name: str, **kwargs) -> logging.Logger:
        """Create a new configured logger instance."""
        return setup_logging(name=name, **kwargs)
    
    @classmethod
    def clear_cache(cls):
        """Clear the logger cache."""
        with cls._lock:
            cls._instances.clear()


def setup_logging_basic(
    level: Union[str, int] = logging.INFO,
    show_background: bool = True,
    format_template: Optional[str] = None,
    show_time: bool = True,
    show_name: bool = True,
    show_pid: bool = False,
    show_level: bool = True,
    show_path: bool = True,
    use_colors: bool = True,
    suppressed_loggers: Optional[List[str]] = None
) -> logging.Logger:
    """
    Setup basic logging with custom formatter (ANSI colors).
    
    Args:
        level: Logging level
        show_background: Whether to show background colors
        format_template: Custom format template
        show_time: Show timestamp
        show_name: Show logger name
        show_pid: Show process ID
        show_level: Show log level
        show_path: Show file path
        use_colors: Enable color output
        suppressed_loggers: List of logger names to suppress
        
    Returns:
        Configured logger instance
    """
    # Configure basic logging
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    logging.basicConfig(level=level, handlers=[])
    
    # Suppress noisy loggers
    if suppressed_loggers:
        for logger_name in suppressed_loggers:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Get root logger and clear existing handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    
    # Create and configure handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CustomFormatter(
        show_background=show_background,
        format_template=format_template,
        show_time=show_time,
        show_name=show_name,
        show_pid=show_pid,
        show_level=show_level,
        show_path=show_path,
        use_colors=use_colors,
    ))
    
    logger.addHandler(handler)
    logger.setLevel(level)
    
    return logger


def setup_logging(
    name: Optional[str] = None,
    lexer: Optional[str] = None,
    log_to_file: bool = False,
    log_file: Optional[str] = None, 
    show_locals: bool = False, 
    level: Union[str, int] = logging.INFO,
    show_level: bool = True,
    show_time: bool = True,
    omit_repeated_times: bool = True,
    show_path: bool = True,
    enable_link_path: bool = True,
    highlighter = None,
    markup: bool = False,
    rich_tracebacks: bool = True,
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
    show_background: bool = True,
    suppressed_loggers: Optional[List[str]] = None,
    enable_rotation: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    structured_logging: bool = False,
    enable_performance_tracking: bool = False
) -> logging.Logger:
    """
    Setup enhanced logging with Rich formatting and production features.
    
    Args:
        name: Logger name (auto-detected if None)
        lexer: Syntax highlighter for code
        log_to_file: Enable file logging
        log_file: Log file path (auto-generated if None)
        show_locals: Show local variables in tracebacks
        level: Logging level
        show_level: Show log level in console
        show_time: Show timestamp in console
        omit_repeated_times: Omit repeated timestamps
        show_path: Show file path in console
        enable_link_path: Enable clickable file paths
        highlighter: Rich highlighter instance
        markup: Enable Rich markup in log messages
        rich_tracebacks: Use Rich formatted tracebacks
        tracebacks_width: Width of traceback display
        tracebacks_extra_lines: Extra lines in tracebacks
        tracebacks_theme: Traceback syntax theme
        tracebacks_word_wrap: Wrap long lines in tracebacks
        tracebacks_show_locals: Show locals in tracebacks
        tracebacks_suppress: Modules to suppress in tracebacks
        locals_max_length: Max length of local variable representations
        locals_max_string: Max length of string representations
        log_time_format: Time format for logs
        keywords: Keywords to highlight in logs
        show_background: Show background colors
        suppressed_loggers: Loggers to suppress
        enable_rotation: Enable log file rotation
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        structured_logging: Enable structured (JSON) logging to file
        enable_performance_tracking: Track logging performance
        
    Returns:
        Configured logger instance
    """
    
    if not RICH_AVAILABLE:
        return setup_logging_basic(
            level=level, show_background=show_background,
            suppressed_loggers=suppressed_loggers
        )
    
    # Auto-generate logger name and log file
    if name is None:
        try:
            filename, _, _ = _get_caller_info(skip_frames=2)
            if filename and not filename.startswith('<') and filename.endswith(('.py', '.pyc')):
                name = Path(filename).stem
            else:
                name = "app"
        except Exception:
            name = "app"
    
    if log_file is None and log_to_file:
        log_file = f"{name}.log"
    
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Configure basic logging
    logging.basicConfig(level=level, handlers=[])
    
    # Suppress noisy loggers
    if suppressed_loggers:
        for logger_name in suppressed_loggers:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    try:
        # Setup Rich console handler
        rich_handler = RichHandler(
            show_time=show_time,
            omit_repeated_times=omit_repeated_times,
            show_level=show_level,
            show_path=show_path,
            enable_link_path=enable_link_path,
            highlighter=highlighter,
            markup=markup,
            rich_tracebacks=rich_tracebacks,
            tracebacks_width=tracebacks_width or shutil.get_terminal_size().columns,
            tracebacks_extra_lines=tracebacks_extra_lines,
            tracebacks_theme=tracebacks_theme or 'fruity',
            tracebacks_word_wrap=tracebacks_word_wrap,
            tracebacks_show_locals=show_locals or tracebacks_show_locals,
            tracebacks_suppress=tracebacks_suppress,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            log_time_format=log_time_format,
            keywords=keywords,
        )
        
        # Disable emojis for cleaner output
        if hasattr(rich_handler, '_log_render'):
            rich_handler._log_render.emojis = False
        
        # Set custom formatter
        rich_handler.setFormatter(EnhancedRichFormatter(
            lexer=lexer, 
            show_background=show_background,
            theme=tracebacks_theme or 'fruity'
        ))
        
        logger.addHandler(rich_handler)
        
    except Exception as e:
        # Fallback to basic logging if Rich setup fails
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter(show_background=show_background))
        logger.addHandler(console_handler)
        logger.warning(f"Rich logging setup failed, using basic formatter: {e}")
    
    # Setup file logging
    if log_to_file and log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            if enable_rotation:
                # Use rotating file handler
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, 
                    maxBytes=max_file_size, 
                    backupCount=backup_count,
                    encoding='utf-8'
                )
            else:
                # Use regular file handler
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
            # Choose formatter based on structured logging preference
            if structured_logging:
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
                    "(%(filename)s:%(lineno)d) [PID:%(process)d]"
                ))
            
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    # Patch RichHandler for better Text handling
    if RICH_AVAILABLE:
        def custom_render_message(self, record, message):
            use_markup = getattr(record, "markup", self.markup)
            if isinstance(message, Text):
                return message
            else:
                try:
                    return Text.from_markup(message) if use_markup else Text(message)
                except Exception:
                    # Fallback for invalid markup
                    return Text(str(message))
        
        # Apply patch to Rich handlers
        for handler in logger.handlers:
            if isinstance(handler, RichHandler):
                handler.render_message = custom_render_message.__get__(handler)
    
    # Add performance tracking if enabled
    if enable_performance_tracking:
        original_handle = logger.handle
        
        def tracked_handle(record):
            start_time = datetime.now()
            try:
                return original_handle(record)
            finally:
                duration = (datetime.now() - start_time).total_seconds()
                _performance.record('log_handle', duration)
        
        logger.handle = tracked_handle
    
    return logger


@lru_cache(maxsize=32)
def get_context_info() -> str:
    """
    Get current execution context for logging with caching.
    
    Returns:
        Formatted string with context information
    """
    try:
        # Get caller information
        filename, function_name, line_number = _get_caller_info(skip_frames=2)
        
        if function_name == "<module>":
            # Try to get class context
            frame = inspect.stack()[2]
            self_obj = frame.frame.f_locals.get('self')
            if self_obj and hasattr(self_obj, '__class__'):
                class_name = self_obj.__class__.__name__
                if class_name != "NoneType":
                    return f"[#00FFFF]({class_name}) --> "
            
            # Look for calling function in stack
            for frame_info in inspect.stack()[3:8]:  # Limit search depth
                if frame_info.function != '<module>':
                    return f"[#FF5500]{frame_info.function}\\[[white on red]{frame_info.lineno}][/] --> "
            
            # Fallback to filename
            return Path(filename).name
        
        return function_name
        
    except Exception as e:
        return f"<context_error:{type(e).__name__}>"


def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics for logging operations."""
    return _performance.get_stats()


def clear_performance_stats():
    """Clear performance tracking statistics."""
    _performance._metrics.clear()


def configure_global_logging(
    level: Union[str, int] = logging.INFO,
    suppress_urllib3: bool = True,
    suppress_requests: bool = True,
    suppress_boto: bool = True,
    additional_suppressed: Optional[List[str]] = None
):
    """
    Configure global logging settings for production use.
    
    Args:
        level: Global logging level
        suppress_urllib3: Suppress urllib3 debug logs
        suppress_requests: Suppress requests debug logs  
        suppress_boto: Suppress boto/AWS SDK debug logs
        additional_suppressed: Additional loggers to suppress
    """
    suppressed_loggers = []
    
    if suppress_urllib3:
        suppressed_loggers.extend(['urllib3.connectionpool', 'urllib3.util.retry'])
    
    if suppress_requests:
        suppressed_loggers.append('requests.packages.urllib3.connectionpool')
    
    if suppress_boto:
        suppressed_loggers.extend([
            'boto3.session', 'botocore.credentials', 'botocore.utils',
            'botocore.hooks', 'botocore.loaders', 'botocore.auth'
        ])
    
    if additional_suppressed:
        suppressed_loggers.extend(additional_suppressed)
    
    setup_logging_basic(level=level, suppressed_loggers=suppressed_loggers)


def test_logger():
    """Comprehensive test function for logger functionality."""
    print("=" * 60)
    print("Testing Enhanced Production Logger")
    print("=" * 60)
    
    # Test basic ANSI formatter
    print("\n1. Testing CustomFormatter (ANSI colors)")
    logger = setup_logging_basic(show_pid=True)
    
    logger.debug("Debug message with detailed information")
    logger.info("Info message - application started")
    logger.warning("Warning message - deprecated function used")
    logger.error("Error message - connection failed")
    logger.critical("Critical message - system failure")
    logger.emergency("Emergency message - immediate action required")
    logger.fatal("Fatal message - application terminating")
    logger.alert("Alert message - administrator attention needed")
    logger.notice("Notice message - significant condition")
    
    # Test Rich formatter if available
    if RICH_AVAILABLE:
        print("\n2. Testing EnhancedRichFormatter")
        logger = setup_logging(name="test_rich", level="DEBUG")
        
        logger.debug("Debug with Rich formatting")
        logger.info("Info with [bold cyan]Rich markup[/bold cyan]")
        logger.warning("Warning with emoji support 🚀")
        logger.error("Error with structured data", extra={"user_id": 123, "action": "login"})
        logger.critical("Critical with exception handling")
        
        # Test syntax highlighting
        code_logger = setup_logging(lexer="python", name="code_test")
        code_logger.info("""
def hello_world():
    print("Hello, World!")
    return True
        """.strip())
        
        print("\n3. Testing file logging with rotation")
        file_logger = setup_logging(
            name="file_test",
            log_to_file=True,
            log_file="test.log",
            enable_rotation=True,
            structured_logging=True,
            max_file_size=1024  # Small size for testing
        )
        
        for i in range(5):
            file_logger.info(f"Test log message {i}", extra={"iteration": i})
    
    # Test performance tracking
    print("\n4. Testing performance tracking")
    perf_logger = setup_logging(
        name="perf_test",
        enable_performance_tracking=True,
        level="INFO"
    )
    
    for i in range(10):
        perf_logger.info(f"Performance test message {i}")
    
    stats = get_performance_stats()
    if stats:
        print("Performance Statistics:")
        for operation, metrics in stats.items():
            print(f"  {operation}: {metrics}")
    
    # Test context information
    print("\n5. Testing context information")
    context = get_context_info()
    logger.info(f"Current context: {context}")
    
    # Test factory pattern
    print("\n6. Testing LoggerFactory")
    factory_logger1 = LoggerFactory.get_logger("test_app")
    factory_logger2 = LoggerFactory.get_logger("test_app")  # Should be same instance
    print(f"Same instance: {factory_logger1 is factory_logger2}")
    
    # Test error handling
    print("\n7. Testing error handling and fallbacks")
    try:
        # Simulate a logging error scenario
        error_logger = setup_logging(name="error_test")
        error_logger.info("Testing error resilience")
        
        # Test with invalid markup
        if RICH_AVAILABLE:
            error_logger.info("Invalid [bold markup test", extra={"_safe_markup": True})
    except Exception as e:
        print(f"Error handling test: {e}")
    
    print("\n" + "=" * 60)
    print("Logger testing completed!")
    print("=" * 60)


class ContextualLogger:
    """Enhanced logger with automatic context detection and structured logging."""
    
    def __init__(self, name: Optional[str] = None, **kwargs):
        """Initialize contextual logger."""
        self.logger = setup_logging(name=name, **kwargs)
        self._context = {}
    
    def set_context(self, **kwargs):
        """Set logging context that will be added to all log messages."""
        self._context.update(kwargs)
    
    def clear_context(self):
        """Clear logging context."""
        self._context.clear()
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log message with automatic context injection."""
        if self._context:
            extra = kwargs.get('extra', {})
            extra.update(self._context)
            kwargs['extra'] = extra
        
        # Add caller context
        context_info = get_context_info()
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['context'] = context_info
        
        self.logger._log(level, msg, args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg, *args, exc_info=True, **kwargs):
        """Log exception with context."""
        self._log_with_context(logging.ERROR, msg, *args, exc_info=exc_info, **kwargs)


def create_logger(
    name: Optional[str] = None,
    level: Union[str, int] = logging.INFO,
    **kwargs
) -> ContextualLogger:
    """
    Create a contextual logger instance with enhanced features.
    
    Args:
        name: Logger name (auto-detected if None)
        level: Logging level
        **kwargs: Additional arguments passed to setup_logging
        
    Returns:
        ContextualLogger instance
    """
    return ContextualLogger(name=name, level=level, **kwargs)


# Convenience function for quick setup
def quick_setup(
    level: Union[str, int] = logging.INFO,
    rich: bool = True,
    colors: bool = True,
    file_logging: bool = False
) -> logging.Logger:
    """
    Quick logger setup for common use cases.
    
    Args:
        level: Logging level
        rich: Use Rich formatting (if available)
        colors: Enable color output
        file_logging: Enable file logging
        
    Returns:
        Configured logger instance
    """
    if rich and RICH_AVAILABLE:
        return setup_logging(
            level=level,
            log_to_file=file_logging,
            show_background=colors
        )
    else:
        return setup_logging_basic(
            level=level,
            use_colors=colors
        )


# Export main functions and classes
__all__ = [
    # Setup functions
    'setup_logging',
    'setup_logging_basic',
    'configure_global_logging',
    'quick_setup',
    
    # Factory and enhanced logger
    'LoggerFactory',
    'ContextualLogger',
    'create_logger',
    
    # Utility functions
    'get_context_info',
    'get_performance_stats',
    'clear_performance_stats',
    
    # Custom levels
    'EMERGENCY_LEVEL',
    'FATAL_LEVEL', 
    'CRITICAL_LEVEL',
    'ALERT_LEVEL',
    'NOTICE_LEVEL',
    'DEBUG', 'INFO', 'WARNING', 'ERROR',
    
    # Formatters
    'CustomFormatter',
    'StructuredFormatter',
    'EnhancedRichFormatter' if RICH_AVAILABLE else 'CustomFormatter',
    
    # Test function
    'test_logger',
    
    # Constants
    'RICH_AVAILABLE'
]

def test():
    """Test function to verify logger setup with different configurations."""
    logger = setup_logging_basic()
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
    
    logger = setup_logging_basic(show_background=False)
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
    
    logger = setup_logging(log_to_file=True)
    
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
    
    logger = setup_logging(show_background=False)
    
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
    # Run comprehensive tests
    test_logger()
    
    # Example usage
    print("\n" + "=" * 60)
    print("Example Usage")
    print("=" * 60)
    
    # Quick setup example
    logger = quick_setup(level="DEBUG", rich=True, file_logging=True)
    logger.info("Quick setup logger example")
    
    # Contextual logger example
    ctx_logger = create_logger("example_app")
    ctx_logger.set_context(user_id=123, session="abc-456")
    ctx_logger.info("Contextual logging example")
    ctx_logger.error("Error with context")
    
    # Factory example
    app_logger = LoggerFactory.get_logger("my_app")
    app_logger.info("Factory logger example")
    
    print("\nTEST [1] Example completed!")

    test()

    print("\nTEST [2] Example completed!")