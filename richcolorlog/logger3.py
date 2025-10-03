#!/usr/bin/env python3
# file: richcolorlog/logger.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-02 09:58:21.987880
# Description: Rich Logger - Enhanced logging with Rich formatting and custom levels.
# Supports multiple outputs: Console, File, RabbitMQ, Kafka, ZeroMQ, Syslog, Database
# License: MIT

import logging
import logging.handlers
import traceback
import os
import sys
import inspect
import shutil
import socket
import json
from typing import Optional, Union, Iterable, List, Dict, Any, Callable
from types import ModuleType
from datetime import datetime
import threading
from functools import lru_cache, wraps

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import TerminalFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

try:
    from rich.logging import FormatTimeCallable
except ImportError:
    FormatTimeCallable = Callable[[float], str]

try:
    import rich
    from rich.logging import RichHandler
    from rich.text import Text
    from rich.console import Group
    from rich.table import Table
    from rich.console import Console
    from rich.syntax import Syntax
    from rich import traceback as rich_traceback
    from rich.markup import escape as rich_escape
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None
    RichHandler = object
    # Fallback escape function
    def rich_escape(text: str) -> str:
        return str(text)


# Define custom log levels (matching syslog severity)
EMERGENCY_LEVEL = logging.CRITICAL + 10  # 60 - System unusable
FATAL_LEVEL = 55
ALERT_LEVEL = logging.CRITICAL + 9       # 59 - Action must be taken immediately
CRITICAL_LEVEL = logging.CRITICAL + 8    # 58 - Critical conditions
ERROR_LEVEL = logging.ERROR              # 40 - Error conditions
WARNING_LEVEL = logging.WARNING          # 30 - Warning conditions
NOTICE_LEVEL = logging.INFO + 5          # 25 - Normal but significant
INFO_LEVEL = logging.INFO                # 20 - Informational messages
DEBUG_LEVEL = logging.DEBUG              # 10 - Debug messages

# Standard levels
DEBUG = logging.DEBUG
ERROR = logging.ERROR
INFO = logging.INFO
WARNING = logging.WARNING
CRITICAL = logging.CRITICAL

# Add custom level names
logging.addLevelName(EMERGENCY_LEVEL, "EMERGENCY")
logging.addLevelName(ALERT_LEVEL, "ALERT")
logging.addLevelName(CRITICAL_LEVEL, "CRITICAL")
logging.addLevelName(NOTICE_LEVEL, "NOTICE")
logging.addLevelName(FATAL_LEVEL, "FATAL")

# All logging levels for iteration
LOGGING_LEVELS_LIST = [
    DEBUG_LEVEL,
    INFO_LEVEL,
    NOTICE_LEVEL,
    WARNING_LEVEL,
    ERROR_LEVEL,
    logging.CRITICAL,
    CRITICAL_LEVEL,
    FATAL_LEVEL,
    ALERT_LEVEL,
    EMERGENCY_LEVEL,
]

# Syslog severity mapping (RFC 5424)
SYSLOG_SEVERITY_MAP = {
    EMERGENCY_LEVEL: 0,  # Emergency
    ALERT_LEVEL: 1,      # Alert
    FATAL_LEVEL: 1,      # Fatal (no syslog standard)
    CRITICAL_LEVEL: 2,   # Critical
    logging.CRITICAL: 2, # Critical
    ERROR_LEVEL: 3,      # Error
    WARNING_LEVEL: 4,    # Warning
    NOTICE_LEVEL: 5,     # Notice
    INFO_LEVEL: 6,       # Informational
    DEBUG_LEVEL: 7,      # Debug
}

# Level to table name mapping for database
LEVEL_TO_TABLE = {
    EMERGENCY_LEVEL: "log_emergency",
    ALERT_LEVEL: "log_alert",
    FATAL_LEVEL: "log_fatal",
    CRITICAL_LEVEL: "log_critical",
    ERROR_LEVEL: "log_error",
    WARNING_LEVEL: "log_warning",
    NOTICE_LEVEL: "log_notice",
    INFO_LEVEL: "log_info",
    DEBUG_LEVEL: "log_debug",
}

# ==================== IPython/Jupyter Compatibility ====================

def _is_ipython():
    """Check if running in IPython/Jupyter."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except (ImportError, AttributeError):
        return False

def _configure_ipython_logging():
    """Configure logging to work properly in IPython."""
    if _is_ipython():
        import warnings
        # Suppress the async warning
        warnings.filterwarnings('ignore', 
                              category=RuntimeWarning,
                              message='.*coroutine.*was never awaited.*')
        
        # Disable Rich's automatic detection in IPython
        if 'JUPYTER_COLUMNS' in os.environ:
            # Force simple console in Jupyter
            os.environ['TERM'] = 'dumb'

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

# ======================================================================

def _add_custom_level_method(level_name: str, level_value: int):
    """Add a custom logging method to the Logger class."""
    def log_method(self, message, *args, **kwargs):
        if self.isEnabledFor(level_value):
            self._log(level_value, message, args, **kwargs)
    
    setattr(logging.Logger, level_name.lower(), log_method)


# Add custom logging methods
_add_custom_level_method("EMERGENCY", EMERGENCY_LEVEL)
_add_custom_level_method("ALERT", ALERT_LEVEL)
_add_custom_level_method("NOTICE", NOTICE_LEVEL)
_add_custom_level_method("FATAL", FATAL_LEVEL)


# ==================== Icon Support ====================

class Icon:
    """Icon mappings for different log levels."""
    debug     = "🐛"
    info      = "ℹ️"
    notice    = "📢"
    warning   = "⚠️"
    error     = "❌"
    critical  = "💥"
    alert     = "🚨"
    emergency = "🆘"
    fatal     = "☠"
    
    # Uppercase aliases
    DEBUG     = debug
    INFO      = info
    NOTICE    = notice
    WARNING   = warning
    ERROR     = error
    CRITICAL  = critical
    ALERT     = alert
    EMERGENCY = emergency
    FATAL     = fatal
    
    # Short aliases
    DEB  = debug
    INF  = info
    NOT  = notice
    WARN = warning
    ERR  = error
    CRI  = critical
    ALE  = alert
    EME  = emergency
    FAT  = fatal
    
    # Lowercase short aliases
    deb  = debug
    inf  = info
    noti = notice
    war  = warning
    warn = warning
    err  = error
    cri  = critical
    ale  = alert
    eme  = emergency
    fat  = fatal

class IconFilter(logging.Filter):
    """Filter to add icons to log messages."""
    
    LEVEL_ICON_MAP = {
        logging.DEBUG: Icon.debug,
        logging.INFO: Icon.info,
        logging.WARNING: Icon.warning,
        logging.ERROR: Icon.error,
        logging.CRITICAL: Icon.critical,
        EMERGENCY_LEVEL: Icon.emergency,
        ALERT_LEVEL: Icon.alert,
        CRITICAL_LEVEL: Icon.critical,
        NOTICE_LEVEL: Icon.notice,
        FATAL_LEVEL: Icon.fatal,
    }
    
    def __init__(self, icon_first=False):
        """
        Initialize IconFilter.
        
        Args:
            icon_first (bool): If True, icon appears before timestamp.
                             If False, icon appears before message (default).
        """
        super().__init__()
        self.icon_first = icon_first
    
    def filter(self, record):
        """Add icon to the record."""
        icon = self.LEVEL_ICON_MAP.get(record.levelno, "")
        if icon:
            if self.icon_first:
                # Store icon in record attribute for formatter to use
                record.icon = icon
            else:
                # Add icon to message (default behavior)
                if not str(record.msg).startswith(icon):
                    record.msg = f"{icon} {record.msg}"
        else:
            record.icon = ""
        return True

# Custom Logger: Override ._log so you can accept Lexer
# class RichLogger(logging.Logger):
#     """Custom logger class that supports lexer parameter."""
    
#     def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
#         if extra is None:
#             extra = {}
#         if "lexer" in kwargs:
#             extra["lexer"] = kwargs.pop("lexer")
#         super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
    
#     # TAMBAHKAN METHOD-METHOD INI:
#     def debug(self, msg, *args, **kwargs):
#         if self.isEnabledFor(logging.DEBUG):
#             self._log(logging.DEBUG, msg, args, **kwargs)
    
#     def info(self, msg, *args, **kwargs):
#         if self.isEnabledFor(logging.INFO):
#             self._log(logging.INFO, msg, args, **kwargs)
    
#     def warning(self, msg, *args, **kwargs):
#         if self.isEnabledFor(logging.WARNING):
#             self._log(logging.WARNING, msg, args, **kwargs)
    
#     def error(self, msg, *args, **kwargs):
#         if self.isEnabledFor(logging.ERROR):
#             self._log(logging.ERROR, msg, args, **kwargs)
    
#     def critical(self, msg, *args, **kwargs):
#         if self.isEnabledFor(logging.CRITICAL):
#             self._log(logging.CRITICAL, msg, args, **kwargs)

class CustomLogger(logging.Logger):
    """Custom logger class for ANSI output that supports lexer parameter."""
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        if extra is None:
            extra = {}
        if "lexer" in kwargs:
            extra["lexer"] = kwargs.pop("lexer")
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
    
    # TAMBAHKAN METHOD-METHOD YANG SAMA SEPERTI DI ATAS:
    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)

class CustomFormatter(logging.Formatter):
    """Custom formatter with ANSI color codes for different log levels."""
    
    COLORS = SafeDict({
        'debug': "\x1b[38;2;255;170;0m",
        'info': "\x1b[38;2;0;255;255m",
        'warning': "\x1b[30;48;2;255;255;0m",
        'error': "\x1b[97;41m",
        'critical': "\x1b[37;44m",
        'alert': "\x1b[97;48;2;0;85;0m",
        'emergency': "\x1b[97;48;2;170;0;255m",
        'notice': "\x1b[30;48;2;0;255;255m",
        'fatal': "\x1b[97;48;2;85;0;0m",
        'reset': "\x1b[0m"
    })
    
    FORMAT_TEMPLATE = "%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"


    def __init__(
        self,
        show_background: bool = True,
        format_template: Optional[str] = "[%(levelname)s] %(message)s",
        show_time: bool = True,
        show_name: bool = True,
        show_pid: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        icon_first: bool = False,
        lexer: str = '',
        use_colors: bool = True
    ):
        super().__init__()
        self.use_colors = use_colors and self._supports_color()
        self.icon_first = icon_first
        self.lexer = lexer

        self.default_formatter = logging.Formatter(self.FORMAT_TEMPLATE)
        
        if format_template:
            self.FORMAT_TEMPLATE = format_template
        else:
            self.FORMAT_TEMPLATE = self._build_format_template(
                show_time, show_name, show_pid, show_level, show_path
            )

        if not show_background:
            self.COLORS = self.COLORS.copy()
            self.COLORS.update({
                'warning': "\x1b[38;2;255;255;0m",
                'error': "\x1b[31m",
                'critical': "\x1b[38;2;85;0;0m",
                'alert': "\x1b[38;2;0;85;0m",
                'emergency': "\x1b[38;2;170;0;255m",
                'notice': "\x1b[38;2;0;255;255m",
                'fatal': "\x1b[38;2;0;85;255m",
            })

        self._build_formatters()
        
    def _build_formatters(self):
        """Build formatters for each log level."""
        icon_prefix = self.check_icon_first()
        if self.use_colors:
            self.formatters = {
                logging.DEBUG: logging.Formatter(icon_prefix + self.COLORS['debug'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.INFO: logging.Formatter(icon_prefix + self.COLORS['info'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.WARNING: logging.Formatter(icon_prefix + self.COLORS['warning'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.ERROR: logging.Formatter(icon_prefix + self.COLORS['error'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.CRITICAL: logging.Formatter(icon_prefix + self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                CRITICAL_LEVEL: logging.Formatter(icon_prefix + self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                EMERGENCY_LEVEL: logging.Formatter(icon_prefix + self.COLORS['emergency'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                ALERT_LEVEL: logging.Formatter(icon_prefix + self.COLORS['alert'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                NOTICE_LEVEL: logging.Formatter(icon_prefix + self.COLORS['notice'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                FATAL_LEVEL: logging.Formatter(icon_prefix + self.COLORS['fatal'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            }
        else:
            # self.formatters = {level: logging.Formatter(self.FORMAT_TEMPLATE) for level in LOGGING_LEVELS_LIST}
            base_format = icon_prefix + self.FORMAT_TEMPLATE
            self.formatters = {level: logging.Formatter(base_format) for level in LOGGING_LEVELS_LIST}

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

    def _supports_color(self) -> bool:
        """Check if terminal supports color output."""
        if os.getenv("FORCE_COLOR", "").lower() in ("1", "true"):
            return True
        if os.getenv("NO_COLOR") is not None:
            return False
        try:
            return sys.stdout.isatty() and os.getenv("TERM") != "dumb"
        except Exception:
            return False

    def check_icon_first(self) -> str:
        """Return icon placeholder if icon_first is enabled."""
        if self.icon_first:
            return "%(icon)s "
        return ''

    @performance_monitor
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        # Ensure icon always exists
        if not hasattr(record, "icon"):
            record.icon = ""

        # Select formatter based on level
        formatter = self.formatters.get(record.levelno)
        
        # Use default formatter if not found
        if formatter is None:
            formatter = self.default_formatter

        try:
            msg = formatter.format(record)
        except Exception as e:
            # Don't let logging crash
            msg = f"[FORMATTER ERROR] {record.getMessage()} - {str(e)}"

        return msg

class CustomRichFormatter(logging.Formatter):
    """Enhanced Rich formatter with syntax highlighting support."""
    
    LEVEL_STYLES = SafeDict({
        logging.DEBUG: "bold #FFAA00",
        logging.INFO: "bold #00FFFF",
        logging.WARNING: "black on #FFFF00",
        logging.ERROR: "white on red",
        logging.CRITICAL: "bright_white on #550000",
        FATAL_LEVEL: "bright_white on #0055FF",
        EMERGENCY_LEVEL: "bright_white on #AA00FF",
        ALERT_LEVEL: "bright_white on #005500",
        NOTICE_LEVEL: "black on #00FFFF",
    })

    def __init__(self, lexer: Optional[str] = None, show_background: bool = True, theme: str = "fruity", icon_first: bool = True):
        super().__init__()
        self.lexer = lexer
        self.theme = theme
        self.icon_first = icon_first
        
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
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with Rich styling."""
        # Get style color for this level
        style = self.LEVEL_STYLES.get(record.levelno, "")
        levelname = record.levelname
        location = f"({record.filename}:{record.lineno})"
        
        # Get original message (already processed by IconFilter if icon_first=False)
        raw_message = record.getMessage()
        safe_message = rich_escape(raw_message)

        # Get icon only if icon_first=True
        icon = getattr(record, 'icon', "")

        if self.icon_first and icon:
            prefix = f"{icon} [{style}]{levelname} - {location}[/]"
        else:
            prefix = f"[{style}]{levelname} - {location}[/]"

        return f"{prefix} {safe_message}"


class RichColorLogFormatter(CustomRichFormatter):
    """Adapter formatter for backward compatibility with standard logging.Formatter."""
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        show_background: bool = True,
        show_time: bool = True,
        show_name: bool = True,
        show_pid: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        lexer: str = '',
        theme: str = '',
        icon_first: bool = True
    ):
        super().__init__(
            lexer=lexer,
            show_background=show_background,
            theme=theme or 'fruity',
            icon_first=icon_first,
        )
        self._user_fmt = fmt
        self._datefmt = datefmt
        self._base_formatter = logging.Formatter(fmt, datefmt) if fmt else None

    def _level_to_key(self, levelno: int) -> str:
        """Map level number to color key."""
        if levelno >= EMERGENCY_LEVEL:
            return "emergency"
        if levelno >= ALERT_LEVEL:
            return "alert"
        if levelno >= CRITICAL_LEVEL:
            return "critical"
        if levelno >= logging.CRITICAL:
            return "critical"
        if levelno >= logging.ERROR:
            return "error"
        if levelno >= logging.WARNING:
            return "warning"
        if levelno >= NOTICE_LEVEL:
            return "notice"
        if levelno >= logging.INFO:
            return "info"
        return "debug"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color codes."""
        if self._base_formatter:
            try:
                key = self._level_to_key(record.levelno)
                start = CustomFormatter.COLORS.get(key, "")
                reset = CustomFormatter.COLORS.get("reset", "")
                setattr(record, "log_color", start)
                setattr(record, "reset", reset)
            except Exception:
                setattr(record, "log_color", "")
                setattr(record, "reset", "")
            return self._base_formatter.format(record)

        return super().format(record)

def _check_logging_disabled():
    """Check environment variables to see if logging should be disabled."""
    NO_LOGGING = os.getenv('NO_LOGGING', '0').lower() in ['1', 'true', 'yes']
    LOGGING_DISABLED = os.getenv('LOGGING', '1').lower() in ['0', 'false', 'no']

    if NO_LOGGING or LOGGING_DISABLED:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL + 99999)
        root_logger.handlers = []
        return True
    return False

# ==================== Message Broker Handlers ====================

class RabbitMQHandler(logging.Handler):
    """Handler to send a log to RabbitMQ with routing_key = level."""
    
    def __init__(self, host='localhost', port=5672, exchange='logs', 
                 username='guest', password='guest', vhost='/', level=logging.DEBUG):
        super().__init__(level)
        self.host = host
        self.port = port
        self.exchange = exchange
        self.username = username
        self.password = password
        self.vhost = vhost
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            import pika
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
        except ImportError:
            logging.error("pika library not installed. Install with: pip install pika")
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
    
    def emit(self, record):
        """Emit log record to RabbitMQ with routing_key = level."""
        if not self.channel:
            return
        
        try:
            import pika
            routing_key = record.levelname.lower()
            
            message = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'pathname': record.pathname,
                'process': record.process,
                'thread': record.thread,
            }
            
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        except Exception as e:
            logging.error(f"Failed to send log to RabbitMQ: {e}")
    
    def close(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

class KafkaHandler(logging.Handler):
    """Handler to send log to Kafka."""
    
    def __init__(self, host='localhost', port=9092, topic='logs', 
                 use_level_in_topic=False, level=logging.DEBUG):
        super().__init__(level)
        self.host = host
        self.port = port
        self.base_topic = topic
        self.use_level_in_topic = use_level_in_topic
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Kafka."""
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=f'{self.host}:{self.port}',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except ImportError:
            logging.error("kafka-python library not installed. Install with: pip install kafka-python")
        except Exception as e:
            logging.error(f"Failed to connect to Kafka: {e}")
    
    def emit(self, record):
        """Emit log record to Kafka."""
        if not self.producer:
            return
        
        try:
            level_name = record.levelname.lower()
            
            if self.use_level_in_topic:
                topic = f"{self.base_topic}.{level_name}"
            else:
                topic = self.base_topic
            
            message = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'pathname': record.pathname,
                'process': record.process,
                'thread': record.thread,
            }
            
            self.producer.send(
                topic=topic,
                key=level_name,
                value=message
            )
            self.producer.flush()
        except Exception as e:
            logging.error(f"Failed to send log to Kafka: {e}")
    
    def close(self):
        """Close Kafka producer."""
        if self.producer:
            self.producer.close()

class ZeroMQHandler(logging.Handler):
    """Handler to send log to ZeroMQ."""
    
    def __init__(self, host='localhost', port=5555, socket_type='PUB', level=logging.DEBUG):
        super().__init__(level)
        self.host = host
        self.port = port
        self.socket_type = socket_type
        self.context = None
        self.socket = None
        self._connect()
    
    def _connect(self):
        """Establish ZeroMQ connection."""
        try:
            import zmq
            self.context = zmq.Context()
            
            if self.socket_type == 'PUB':
                self.socket = self.context.socket(zmq.PUB)
                self.socket.bind(f"tcp://{self.host}:{self.port}")
            elif self.socket_type == 'PUSH':
                self.socket = self.context.socket(zmq.PUSH)
                self.socket.connect(f"tcp://{self.host}:{self.port}")
            else:
                raise ValueError(f"Unsupported socket type: {self.socket_type}")
        except ImportError:
            logging.error("pyzmq library not installed. Install with: pip install pyzmq")
        except Exception as e:
            logging.error(f"Failed to setup ZeroMQ: {e}")
    
    def emit(self, record):
        """Emit log record to ZeroMQ."""
        if not self.socket:
            return
        
        try:
            topic = record.levelname.lower()
            
            message = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'pathname': record.pathname,
                'process': record.process,
                'thread': record.thread,
            }
            
            self.socket.send_string(f"{topic} {json.dumps(message)}")
        except Exception as e:
            logging.error(f"Failed to send log to ZeroMQ: {e}")
    
    def close(self):
        """Close ZeroMQ socket."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

class SyslogHandler(logging.handlers.SysLogHandler):
    """Enhanced Syslog handler with proper severity mapping."""
    
    def __init__(self, host='localhost', port=514, facility=logging.handlers.SysLogHandler.LOG_USER, 
                 level=logging.DEBUG):
        super().__init__(address=(host, port), facility=facility)
        self.setLevel(level)
    
    def emit(self, record):
        """Emit log record to syslog with proper severity."""
        try:
            severity = SYSLOG_SEVERITY_MAP.get(record.levelno, 7)
            priority = self.encodePriority(self.facility, severity)
            msg = self.format(record)
            msg = self.ident + msg + '\000'
            msg = f'<{priority}>{msg}'
            
            if self.unixsocket:
                try:
                    self.socket.send(msg.encode('utf-8'))
                except OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg.encode('utf-8'))
            else:
                self.socket.sendto(msg.encode('utf-8'), self.address)
        except Exception:
            self.handleError(record)

class DatabaseHandler(logging.Handler):
    """Handler to send log to the database."""
    
    def __init__(self, db_type='postgresql', host='localhost', port=None, 
                 database='logs', user='postgres', password='', level=logging.DEBUG):
        super().__init__(level)
        self.db_type = db_type.lower()
        self.host = host
        self.port = port or self._get_default_port()
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _get_default_port(self):
        """Get default port for database type."""
        ports = {
            'postgresql': 5432,
            'mysql': 3306,
            'mariadb': 3306,
            'sqlite': None,
        }
        return ports.get(self.db_type, 5432)
    
    def _connect(self):
        """Establish database connection."""
        try:
            if self.db_type == 'postgresql':
                import psycopg2
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            elif self.db_type in ('mysql', 'mariadb'):
                import mysql.connector
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            elif self.db_type == 'sqlite':
                import sqlite3
                self.connection = sqlite3.connect(self.database)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except ImportError as e:
            logging.error(f"Database library not installed: {e}")
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
    
    def _create_tables(self):
        """Create log tables if they don't exist."""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == 'postgresql':
                table_schema = """
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    logger VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    module VARCHAR(255),
                    function VARCHAR(255),
                    lineno INTEGER,
                    pathname TEXT,
                    process INTEGER,
                    thread BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """
            elif self.db_type in ('mysql', 'mariadb'):
                table_schema = """
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    logger VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    module VARCHAR(255),
                    function VARCHAR(255),
                    lineno INT,
                    pathname TEXT,
                    process INT,
                    thread BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """
            else:  # sqlite
                table_schema = """
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    logger TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    function TEXT,
                    lineno INTEGER,
                    pathname TEXT,
                    process INTEGER,
                    thread INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                """
            
            for table_name in LEVEL_TO_TABLE.values():
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {table_schema}
                    )
                """)
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS log_syslog (
                    {table_schema}
                )
            """)
            
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logging.error(f"Failed to create log tables: {e}")
    
    def emit(self, record):
        """Emit log record to database."""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            data = (
                datetime.fromtimestamp(record.created),
                record.levelname,
                record.name,
                record.getMessage(),
                record.module,
                record.funcName,
                record.lineno,
                record.pathname,
                record.process,
                record.thread,
            )
            
            if self.db_type == 'postgresql':
                sql = """
                    INSERT INTO {} (timestamp, level, logger, message, module, function, 
                                  lineno, pathname, process, thread)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            elif self.db_type in ('mysql', 'mariadb'):
                sql = """
                    INSERT INTO {} (timestamp, level, logger, message, module, function,
                                  lineno, pathname, process, thread)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            else:  # sqlite
                sql = """
                    INSERT INTO {} (timestamp, level, logger, message, module, function,
                                  lineno, pathname, process, thread)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            
            level_table = LEVEL_TO_TABLE.get(record.levelno, 'log_info')
            cursor.execute(sql.format(level_table), data)
            cursor.execute(sql.format('log_syslog'), data)
            
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logging.error(f"Failed to write log to database: {e}")
            self.handleError(record)
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

# ==================== Handler Classes ====================

class AnsiLogHandler(logging.StreamHandler):
    """Custom Handler with enhanced color formatting and icon ANSI support."""
    
    def __init__(
        self,
        lexer=None,
        show_background=True,
        format_template=None,
        show_time=True,
        show_name=True,
        show_pid=True,
        show_level=True,
        show_path=True,
        show_icon=True,
        icon_first=False,
        **kwargs
    ):
        super().__init__()
        
        self.lexer = lexer
        self.show_icon = show_icon
        self.icon_first = icon_first
        self.format_template = format_template
        
        self.setFormatter(CustomFormatter(
            show_background,
            format_template,
            show_time,
            show_name,
            show_pid,
            show_level,
            show_path,
            icon_first,
            lexer
        ))
        
        if show_icon:
            icon_filter = IconFilter(icon_first=icon_first)
            self.addFilter(icon_filter)
    
    def emit(self, record):
        """Emit a record with pygments highlighting + icon."""
        try:
            msg = self.format(record)
            
            # Apply lexer highlighting if available
            lexer_name = getattr(record, "lexer", None) or self.lexer
            
            if lexer_name and PYGMENTS_AVAILABLE:
                try:
                    lexer_obj = get_lexer_by_name(lexer_name)
                    message_only = record.getMessage()
                    highlighted = highlight(message_only, lexer_obj, TerminalFormatter()).rstrip()
                    # Replace message part in formatted string
                    msg = msg.replace(message_only, highlighted)
                except Exception:
                    pass
            
            self.stream.write(msg + "\n")
            self.flush()
        except Exception:
            self.handleError(record)

class RichColorLogHandler1(RichHandler):
        """Custom RichHandler with enhanced color formatting and icon support."""

        def __init__(self, lexer=None, show_background=True, render_emoji=True, 
                     show_icon=True, icon_first=False, **kwargs):
            self.lexer = lexer
            self.show_background = show_background
            self.show_icon = show_icon
            self.icon_first = icon_first
            self._render_emoji_flag = render_emoji

            # Remove custom params from kwargs before passing to parent
            kwargs.pop("lexer", None)
            kwargs.pop("show_background", None)
            kwargs.pop("render_emoji", None)
            kwargs.pop("show_icon", None)
            kwargs.pop("icon_first", None)

            super().__init__(**kwargs)

            self.markup = True
            
            # Enable emoji rendering
            try:
                if hasattr(self, '_log_render'):
                    self._log_render.emojis = bool(self._render_emoji_flag)
            except Exception:
                pass

            if self.show_icon:
                icon_filter = IconFilter(icon_first=icon_first)
                self.addFilter(icon_filter)

            self.setFormatter(CustomRichFormatter(
                lexer=self.lexer, 
                show_background=self.show_background, 
                icon_first=self.icon_first
            ))

class RichColorLogHandler(RichHandler):
    """Custom RichHandler with compact layout."""

    LEVEL_STYLES = {
        logging.DEBUG: "bold #FFAA00",
        logging.INFO: "bold #00FFFF",
        logging.WARNING: "black on #FFFF00",  # ✅ Background
        logging.ERROR: "white on red",        # ✅ Background
        logging.CRITICAL: "bright_white on #550000",  # ✅ Background
        FATAL_LEVEL: "bright_white on #0055FF",
        EMERGENCY_LEVEL: "bright_white on #AA00FF",  # ✅ Background
        ALERT_LEVEL: "bright_white on #005500",      # ✅ Background
        NOTICE_LEVEL: "black on #00FFFF",            # ✅ Background
    }

    def __init__(self,
        lexer=None,
        show_background=True,
        render_emoji=True,
        show_icon=True,
        icon_first=False,
        theme="fruity",
        
        level: Union[int, str] = 'DEBUG',
        console: Optional[rich.console.Console] = None,
        show_time: bool = True,
        omit_repeated_times: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        enable_link_path: bool = True,        
        highlighter: Optional[rich.highlighter.Highlighter] = None,
        markup: bool = False,
        rich_tracebacks: bool = False,         
        tracebacks_width: Optional[int] = None,
        tracebacks_code_width: Optional[int] = 88,
        tracebacks_extra_lines: int = 3,      
        tracebacks_theme: Optional[str] = None,
        tracebacks_word_wrap: bool = True,
        tracebacks_show_locals: bool = False,         
        tracebacks_suppress: Iterable[Union[str, ModuleType]] = (),
        tracebacks_max_frames: int = 100,
        locals_max_length: int = 10,   
        locals_max_string: int = 80,
        log_time_format: Union[str, Callable[[datetime],
        rich.text.Text]] = '[%x %X]',     
        keywords: Optional[List[str]] = None,
        
        **kwargs):

        self.lexer = lexer
        self.show_background = show_background
        self.show_icon = show_icon
        self.icon_first = icon_first
        self.theme = theme
        self._render_emoji_flag = render_emoji

        self.level = level 
        self.console = console 
        self.show_time = show_time 
        self.omit_repeated_times = omit_repeated_times 
        self.show_level = show_level 
        self.show_path = show_path 
        self.enable_link_path = enable_link_path 
        self.highlighter = highlighter 
        self.markup = markup 
        self.rich_tracebacks = rich_tracebacks 
        self.tracebacks_width = tracebacks_width 
        self.tracebacks_code_width = tracebacks_code_width 
        self.tracebacks_extra_lines = tracebacks_extra_lines 
        self.tracebacks_theme = tracebacks_theme 
        self.tracebacks_word_wrap = tracebacks_word_wrap 
        self.tracebacks_show_locals = tracebacks_show_locals 
        self.tracebacks_suppress = tracebacks_suppress 
        self.tracebacks_max_frames = tracebacks_max_frames 
        self.locals_max_length = locals_max_length 
        self.locals_max_string = locals_max_string 
        self.log_time_format = log_time_format 
        self.keywords = keywords 
        
        # Remove custom params
        for key in ["lexer", "show_background", "render_emoji", "show_icon", "icon_first", "theme"]:
            kwargs.pop(key, None)

        super().__init__(**kwargs)

        self.markup = True
        
        # Update styles
        if not show_background:
            self.LEVEL_STYLES = {
                logging.DEBUG: "bold #FFAA00",
                logging.INFO: "bold #00FFFF",
                logging.WARNING: "#FFFF00",          # ❌ No background
                logging.ERROR: "red",                # ❌ No background
                logging.CRITICAL: "bold #550000",    # ❌ No background
                FATAL_LEVEL: "#0055FF",
                EMERGENCY_LEVEL: "#AA00FF",
                ALERT_LEVEL: "#005500",
                NOTICE_LEVEL: "#00FFFF",
            }

        try:
            if hasattr(self, '_log_render'):
                self._log_render.emojis = bool(self._render_emoji_flag)
        except Exception:
            pass

        if self.show_icon:
            icon_filter = IconFilter(icon_first=icon_first)
            self.addFilter(icon_filter)

    def get_level_text(self, record):
        """Override untuk compact level text."""
        level_name = record.levelname
        style = self.LEVEL_STYLES.get(record.levelno, "")
        
        # Icon handling
        icon = getattr(record, 'icon', "")
        if icon and self.icon_first:
            level_text = Text(f"{icon} ") + Text(f"{level_name}", style=style)
        else:
            level_text = Text(level_name, style=style)
        
        return level_text

    def emit(self, record):
        """Override emit untuk custom layout yang lebih compact."""
        try:
            # Get message
            message = self.render_message(record, record.getMessage())
            
            # Get level with icon
            level_text = self.get_level_text(record)
            
            # Get path (compact)
            path_text = Text(f"{record.filename}:{record.lineno}", style="log.path")
            
            # Build compact layout dengan Table
            output = Text()
            
            # Time (optional)
            if self.show_time:
                log_time = self.get_time_text(record)
                output.append(log_time)
                output.append(" ")
            
            # Level + icon (fixed width)
            # output.append(level_text)
            # output.append(" " * (12 - len(level_text.plain)))  # Padding
            
            # Message
            if isinstance(message, (Text, str)):
                output.append(level_text + " " +  message)
                output.append(" " * (12 - len(level_text.plain)))  # Padding
                # output.append(message)
            else:
                # Syntax atau Rich renderable
                self.console.print(output, end='')
                self.console.print(message)
                return

            
            # Path di akhir (compact, no excessive spacing)
            if self.show_path:
                output.append(" ")
                output.append(path_text)
            
            # Print ke console
            self.console.print(output)
            
        except Exception:
            self.handleError(record)
    
    def get_time_text(self, record):
        if self.formatter:
            log_time = self.formatter.formatTime(record, self.log_time_format)
        else:
            ct = datetime.fromtimestamp(record.created)
            if isinstance(self.log_time_format, str):
                log_time = ct.strftime(self.log_time_format.strip("[]"))
            elif callable(self.log_time_format):
                log_time = self.log_time_format(ct)
            else:
                log_time = str(ct)

        return Text(f"{log_time}", style="log.time")


    def render_message(self, record, message):
        """Override render_message untuk apply syntax highlighting dan styling."""
        # Get lexer
        lexer_name = getattr(record, "lexer", None) or self.lexer
        
        # Get style untuk level ini
        style = self.LEVEL_STYLES.get(record.levelno, "")
        
        # Jika ada lexer, apply syntax highlighting
        # print(f"str(message): {str(message)}")
        # print(f"str(message): {[str(message)]}")
        if lexer_name:
            try:
                from rich.syntax import Syntax
                syntax = Syntax(
                    str(message), 
                    lexer_name, 
                    theme=self.theme,
                    line_numbers=False,
                    word_wrap=True
                )
                return syntax  # ✅ Return Syntax object, bukan string
            except Exception:
                pass
        
        # Fallback: apply style level ke message
        if isinstance(message, Text):
            return message
        
        return Text(str(message), style=style)

class RichColorLogHandler2(RichHandler):
    """Custom RichHandler with compact layout."""

    LEVEL_STYLES = {
        logging.DEBUG: "bold #FFAA00",
        logging.INFO: "bold #00FFFF",
        logging.WARNING: "black on #FFFF00",  # ✅ Background
        logging.ERROR: "white on red",        # ✅ Background
        logging.CRITICAL: "bright_white on #550000",  # ✅ Background
        FATAL_LEVEL: "bright_white on #0055FF",
        EMERGENCY_LEVEL: "bright_white on #AA00FF",  # ✅ Background
        ALERT_LEVEL: "bright_white on #005500",      # ✅ Background
        NOTICE_LEVEL: "black on #00FFFF",            # ✅ Background
    }

    def __init__(self,
        lexer=None,
        show_background=True,
        render_emoji=True,
        show_icon=True,
        icon_first=False,
        theme="fruity",
        
        level: Union[int, str] = 'DEBUG',
        console: Optional[rich.console.Console] = None,
        show_time: bool = True,
        omit_repeated_times: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        enable_link_path: bool = True,        
        highlighter: Optional[rich.highlighter.Highlighter] = None,
        markup: bool = False,
        rich_tracebacks: bool = False,         
        tracebacks_width: Optional[int] = None,
        tracebacks_code_width: Optional[int] = 88,
        tracebacks_extra_lines: int = 3,      
        tracebacks_theme: Optional[str] = None,
        tracebacks_word_wrap: bool = True,
        tracebacks_show_locals: bool = False,         
        tracebacks_suppress: Iterable[Union[str, ModuleType]] = (),
        tracebacks_max_frames: int = 100,
        locals_max_length: int = 10,   
        locals_max_string: int = 80,
        log_time_format: Union[str, Callable[[datetime],
        rich.text.Text]] = '[%x %X]',     
        keywords: Optional[List[str]] = None,
        
        **kwargs):

        self.lexer = lexer
        self.show_background = show_background
        self.show_icon = show_icon
        self.icon_first = icon_first
        self.theme = theme
        self._render_emoji_flag = render_emoji

        self.level = level 
        self.console = console 
        self.show_time = show_time 
        self.omit_repeated_times = omit_repeated_times 
        self.show_level = show_level 
        self.show_path = show_path 
        self.enable_link_path = enable_link_path 
        self.highlighter = highlighter 
        self.markup = markup 
        self.rich_tracebacks = rich_tracebacks 
        self.tracebacks_width = tracebacks_width 
        self.tracebacks_code_width = tracebacks_code_width 
        self.tracebacks_extra_lines = tracebacks_extra_lines 
        self.tracebacks_theme = tracebacks_theme 
        self.tracebacks_word_wrap = tracebacks_word_wrap 
        self.tracebacks_show_locals = tracebacks_show_locals 
        self.tracebacks_suppress = tracebacks_suppress 
        self.tracebacks_max_frames = tracebacks_max_frames 
        self.locals_max_length = locals_max_length 
        self.locals_max_string = locals_max_string 
        self.log_time_format = log_time_format 
        self.keywords = keywords 
        
        # Remove custom params
        for key in ["lexer", "show_background", "render_emoji", "show_icon", "icon_first", "theme"]:
            kwargs.pop(key, None)

        super().__init__(**kwargs)

        self.markup = True
        
        # Update styles
        if not show_background:
            self.LEVEL_STYLES = {
                logging.DEBUG: "bold #FFAA00",
                logging.INFO: "bold #00FFFF",
                logging.WARNING: "#FFFF00",          # ❌ No background
                logging.ERROR: "red",                # ❌ No background
                logging.CRITICAL: "bold #550000",    # ❌ No background
                FATAL_LEVEL: "#0055FF",
                EMERGENCY_LEVEL: "#AA00FF",
                ALERT_LEVEL: "#005500",
                NOTICE_LEVEL: "#00FFFF",
            }

        try:
            if hasattr(self, '_log_render'):
                self._log_render.emojis = bool(self._render_emoji_flag)
        except Exception:
            pass

        if self.show_icon:
            icon_filter = IconFilter(icon_first=icon_first)
            self.addFilter(icon_filter)

    def get_level_text(self, record):
        """Override untuk compact level text."""
        from rich.text import Text
        
        level_name = record.levelname
        style = self.LEVEL_STYLES.get(record.levelno, "")
        
        # Icon handling
        icon = getattr(record, 'icon', "")
        if icon and self.icon_first:
            level_text = Text(f"{icon} {level_name}", style=style)
        else:
            level_text = Text(level_name, style=style)
        
        return level_text

    def emit(self, record):
        """Override emit untuk custom layout yang lebih compact."""
        from rich.text import Text
        from rich.table import Table
        
        try:
            # Get message
            message = self.render_message(record, record.getMessage())
            
            # Get level with icon
            level_text = self.get_level_text(record)
            
            # Get path (compact)
            path_text = Text(f"{record.filename}:{record.lineno}", style="log.path")
            
            # Build compact layout dengan Table
            output = Text()
            
            # Time (optional)
            if self.show_time:
                log_time = self.get_time_text(record)
                output.append(log_time)
                output.append(" ")
            
            # Level + icon (fixed width)
            output.append(level_text)
            output.append(" " * (12 - len(level_text.plain)))  # Padding
            
            # Message
            if isinstance(message, (Text, str)):
                output.append(message)
            else:
                # Syntax atau Rich renderable
                self.console.print(output, message)
                return

            # Path di akhir (compact, no excessive spacing)
            if self.show_path:
                output.append(" ")
                output.append(path_text)
            
            # Print ke console
            self.console.print(output)
            
        except Exception:
            self.handleError(record)
        
    def get_time_text(self, record):
        if self.formatter:
            log_time = self.formatter.formatTime(record, self.log_time_format)
        else:
            ct = datetime.fromtimestamp(record.created)
            if isinstance(self.log_time_format, str):
                log_time = ct.strftime(self.log_time_format.strip("[]"))
            elif callable(self.log_time_format):
                log_time = self.log_time_format(ct)
            else:
                log_time = str(ct)

        return Text(f"{log_time}", style="log.time")

    def render_message(self, record, message):
        from rich.text import Text

        lexer_name = getattr(record, "lexer", None) or self.lexer
        style = self.LEVEL_STYLES.get(record.levelno, "")

        if lexer_name:
            try:
                syntax = Syntax(
                    str(message),
                    lexer_name,
                    theme=self.theme,
                    line_numbers=False,
                    word_wrap=True,
                )
                return syntax  # ✅ biarkan Syntax, nanti emit handle
            except Exception:
                pass

        if isinstance(message, Text):
            return message

        return Text(str(message), style=style)


class RichColorLogHandler4(RichHandler):
    """Custom RichHandler with compact layout."""

    LEVEL_STYLES = {
        logging.DEBUG: "bold #FFAA00",
        logging.INFO: "bold #00FFFF",
        logging.WARNING: "black on #FFFF00",
        logging.ERROR: "white on red",
        logging.CRITICAL: "bright_white on #550000",
        # custom levels (pastikan sudah didaftarkan jika pakai)
        # FATAL_LEVEL, EMERGENCY_LEVEL, ...
    }

    def __init__(self,
        lexer=None,
        show_background=True,
        render_emoji=True,
        show_icon=True,
        icon_first=False,
        theme="fruity",

        level: Union[int, str] = 'DEBUG',
        console: Optional[object] = None,
        show_time: bool = True,
        omit_repeated_times: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        enable_link_path: bool = True,
        highlighter: Optional[object] = None,
        markup: bool = False,
        rich_tracebacks: bool = False,
        tracebacks_width: Optional[int] = None,
        tracebacks_code_width: Optional[int] = 88,
        tracebacks_extra_lines: int = 3,
        tracebacks_theme: Optional[str] = None,
        tracebacks_word_wrap: bool = True,
        tracebacks_show_locals: bool = False,
        tracebacks_suppress: Iterable[Union[str, ModuleType]] = (),
        tracebacks_max_frames: int = 100,
        locals_max_length: int = 10,
        locals_max_string: int = 80,
        log_time_format: Union[str, Callable[[object], object]] = '[%x %X]',
        keywords: Optional[List[str]] = None,

        **kwargs):

        # --- keep your assignments ---
        self.lexer = lexer
        self.show_background = show_background
        self.show_icon = show_icon
        self.icon_first = icon_first
        self.theme = theme
        self._render_emoji_flag = render_emoji

        self.level = level
        self.console = console
        self.show_time = show_time
        self.omit_repeated_times = omit_repeated_times
        self.show_level = show_level
        self.show_path = show_path
        self.enable_link_path = enable_link_path
        self.highlighter = highlighter
        self.markup = markup
        self.rich_tracebacks = rich_tracebacks
        self.tracebacks_width = tracebacks_width
        self.tracebacks_code_width = tracebacks_code_width
        self.tracebacks_extra_lines = tracebacks_extra_lines
        self.tracebacks_theme = tracebacks_theme
        self.tracebacks_word_wrap = tracebacks_word_wrap
        self.tracebacks_show_locals = tracebacks_show_locals
        self.tracebacks_suppress = tracebacks_suppress
        self.tracebacks_max_frames = tracebacks_max_frames
        self.locals_max_length = locals_max_length
        self.locals_max_string = locals_max_string
        self.log_time_format = log_time_format
        self.keywords = keywords

        # Remove custom params from kwargs
        for key in ["lexer", "show_background", "render_emoji", "show_icon", "icon_first", "theme"]:
            kwargs.pop(key, None)

        super().__init__(**kwargs)

        self.markup = True

        # CHANGED: gunakan instance-level styles agar tidak menimpa class var
        self.level_styles = dict(self.LEVEL_STYLES)
        if not show_background:
            # override dengan versi tanpa background
            self.level_styles = {
                logging.DEBUG: "bold #FFAA00",
                logging.INFO: "bold #00FFFF",
                logging.WARNING: "#FFFF00",          # no background
                logging.ERROR: "red",
                logging.CRITICAL: "bold #550000",
                # custom levels keep same mapping but no backgrounds
            }

        try:
            if hasattr(self, '_log_render'):
                self._log_render.emojis = bool(self._render_emoji_flag)
        except Exception:
            pass

        if self.show_icon:
            icon_filter = IconFilter(icon_first=icon_first)
            self.addFilter(icon_filter)

    def get_level_text(self, record):
        """Override untuk compact level text."""
        level_name = record.levelname
        style = self.level_styles.get(record.levelno, "")
        icon = getattr(record, 'icon', "")
        if icon and self.icon_first:
            return Text(f"{icon} {level_name}", style=style)
        return Text(level_name, style=style)

    def get_time_text(self, record):
        """Get formatted time text. (CHANGED: robust fallback, no super().format_time call)"""
        
        # Jika ada formatter pada handler, pakai itu (formatTime menerima datefmt tanpa [] biasanya)
        log_time = None
        fmt = None
        if isinstance(self.log_time_format, str):
            fmt = self.log_time_format.strip("[]") or None

        if getattr(self, "formatter", None):
            try:
                # gunakan formatter.formatTime(record, datefmt)
                log_time = self.formatter.formatTime(record, fmt)
            except Exception:
                log_time = None

        if log_time is None:
            # fallback manual
            ct = datetime.fromtimestamp(record.created)
            if isinstance(self.log_time_format, str):
                try:
                    log_time = ct.strftime(self.log_time_format.strip("[]"))
                except Exception:
                    log_time = ct.strftime("%x %X")
            elif callable(self.log_time_format):
                try:
                    # jika user memberikan callable untuk format
                    log_time = self.log_time_format(ct)
                except Exception:
                    log_time = ct.strftime("%x %X")
            else:
                log_time = ct.strftime("%x %X")

        return Text(f"[{log_time}]", style="log.time")

    def render_message(self, record, message):
        """Override render_message untuk apply syntax highlighting dan styling.
           Kita biarkan mengembalikan Syntax (renderable) bila lexer dipakai."""
        
        lexer_name = getattr(record, "lexer", None) or self.lexer
        style = self.level_styles.get(record.levelno, "")

        if lexer_name:
            try:
                from rich.syntax import Syntax
                syntax = Syntax(
                    str(message),
                    lexer_name,
                    theme=self.theme,
                    line_numbers=False,
                    word_wrap=True
                )
                return syntax  # return Syntax object (ditangani di emit)
            except Exception:
                pass

        if isinstance(message, Text):
            return message

        return Text(str(message), style=style)

    def emit(self, record):
        """Override emit untuk compact layout dengan path right-aligned.
           (CHANGED: pakai Table.grid + truncation untuk mencegah baris melebihi console width)"""
        
        try:
            message = self.render_message(record, record.getMessage())
            level_text = self.get_level_text(record)
            path_text = Text(f"{record.filename}:{record.lineno}", style="log.path")

            # buat grid 2 kolom: kiri expand, kanan no_wrap justify right
            table = Table.grid(expand=True)
            table.add_column(ratio=1)
            table.add_column(no_wrap=True, justify="right")

            left = Text()

            if self.show_time:
                left.append(self.get_time_text(record))
                left.append(" ")

            left.append(level_text)
            left.append(" ")

            # hitung lebar konsol dan alokasi untuk path
            console_obj = self.console or Console()
            console_width = getattr(console_obj, "width", 80)

            # plain path length (sederhana)
            path_plain = getattr(path_text, "plain", str(path_text))
            path_col_w = max(6, len(path_plain) + 2)  # reserve sedikit ruang

            # sediakan margin ekstra supaya icon/emoji tidak menempel
            safe_margin = 3
            left_available_total = max(10, console_width - path_col_w - safe_margin)

            # panjang prefix di left (waktu + level + spaces)
            left_prefix_len = len(left.plain)
            avail_for_msg_first = max(0, left_available_total - left_prefix_len)

            # Putuskan bagaimana menampilkan first-line:
            need_print_full_below = False

            if isinstance(message, Text):
                # ambil baris pertama tanpa preserving spans (simple)
                msg_plain = message.plain or ""
                first_line = msg_plain.splitlines()[0] if msg_plain else ""
                first_text = Text(first_line)
                # truncate agar tidak melewati width
                if avail_for_msg_first > 0:
                    first_text.truncate(avail_for_msg_first, overflow="ellipsis")
                left.append(first_text)
                # jika ada more lines atau first_line lebih panjang
                need_print_full_below = ("\n" in msg_plain) or (len(msg_plain) > avail_for_msg_first)
            elif isinstance(message, str):
                msg_plain = message
                first_line = msg_plain.splitlines()[0] if msg_plain else ""
                first_text = Text(first_line)
                if avail_for_msg_first > 0:
                    first_text.truncate(avail_for_msg_first, overflow="ellipsis")
                left.append(first_text)
                need_print_full_below = ("\n" in msg_plain) or (len(msg_plain) > avail_for_msg_first)
            else:
                # message adalah renderable (contoh: Syntax) -> tidak append ke left (agar tidak memecah rendering)
                # kita hanya menandai bahwa perlu cetak penuh di bawah
                need_print_full_below = True

            # tambahkan row pertama: left (terpotong) + path (right-aligned)
            table.add_row(left, path_text if self.show_path else "")

            # print the table (first line)
            console_obj.print(table)

            # jika perlu, print full message di bawah (Syntax atau sisa Text)
            if need_print_full_below:
                # Untuk Syntax atau renderable lain, print langsung
                if not isinstance(message, (str, Text)):
                    console_obj.print(message)
                else:
                    # print sisa lines (kalau ada)
                    lines = str(message).splitlines()
                    if len(lines) > 1:
                        # print lines[1:] sebagai satu blok; rich akan wrap sesuai console width
                        rest = "\n".join(lines[1:])
                        console_obj.print(rest)

        except Exception:
            self.handleError(record)

# ==================== Setup Functions ====================

def setup_logging_custom(
    name = __name__,
    level: Union[str, int] = 'DEBUG',
    show_background=True,
    format_template=None,
    show_time=True,
    show_name=True,
    show_pid=True,
    show_level=True,
    show_path=True,
    icon_first=True,
    exceptions=None,
    show=True,
    lexer=None,
    use_colors=True
):
    """Setup basic logging with custom formatter (ANSI colors)."""

    if exceptions is None:
        exceptions = []

    if isinstance(level, str):
        level=getattr(logging, level.upper())
    else:
        level=level

    # if isinstance(level, str):
    #     logging.basicConfig(level=getattr(logging, level.upper()))
    # else:
    #     logging.basicConfig(level=level)
        
    if not show:
        level = 'CRITICAL'
        os.environ['NO_LOGGING'] = '1'
        logging.basicConfig(level=logging.CRITICAL)

    if _check_logging_disabled():
        return logging.getLogger()

    logger = logging.getLogger(name)
    logger.__class__ = CustomLogger
    logger.setLevel(level)

    # Just delete Streamhandler and Richhandler, leave other handlers (Syslog, RabbitMQ, etc)
    handlers_to_remove = []
    for handler in logger.handlers:
        if isinstance(handler, (logging.StreamHandler, RichHandler if RICH_AVAILABLE else type(None))):
            handlers_to_remove.append(handler)
    
    for handler in handlers_to_remove:
        logger.removeHandler(handler)
    
    # Make a new handler
    # handler = logging.StreamHandler(sys.stdout)
    handler = AnsiLogHandler()
    handler.setLevel(level)

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): 
                logging.getLogger(str(i)).setLevel(logging.CRITICAL)

    # for handler in logger.handlers:
    handler.setFormatter(CustomFormatter(
        show_background,
        format_template,
        show_time,
        show_name,
        show_pid,
        show_level,
        show_path,
        icon_first,
        lexer,
        use_colors
    ))

    if icon_first:
        icon_filter = IconFilter(icon_first=True)
        handler.addFilter(icon_filter)
    
    logger.addHandler(handler)
    return logger


def setup_logging(
    name: Optional[str] = None,
    lexer: Optional[str] = None,
    show_locals: bool = False, 
    level: Union[str, int] = 'DEBUG',
    show_level: bool = False,
    show_time: bool = True,
    omit_repeated_times: bool = True,
    show_path: bool = True,
    enable_link_path: bool = True,
    highlighter=None,
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
    show_background=True,
    show_icon=True,
    icon_first=True,
    exceptions=None,
    show=True,
    basic=True,
    theme: str ='fruity',
    # File logging
    log_file: bool = False,
    log_file_name: Optional[str] = None,
    log_file_level: Union[str, int] = logging.INFO,
    # RabbitMQ
    rabbitmq=False,
    rabbitmq_host='localhost',
    rabbitmq_port=5672,
    rabbitmq_exchange='logs',
    rabbitmq_username='guest',
    rabbitmq_password='guest',
    rabbitmq_vhost='/',
    rabbitmq_level=logging.DEBUG,
    # Kafka
    kafka=False,
    kafka_host='localhost',
    kafka_port=9092,
    kafka_topic='logs',
    kafka_use_level_in_topic=False,
    kafka_level=logging.DEBUG,
    # ZeroMQ
    zeromq=False,
    zeromq_host='localhost',
    zeromq_port=5555,
    zeromq_socket_type='PUB',
    zeromq_level=logging.DEBUG,
    # Syslog
    syslog=False,
    syslog_host='localhost',
    syslog_port=514,
    syslog_facility=logging.handlers.SysLogHandler.LOG_USER,
    syslog_level=logging.DEBUG,
    # Database
    db=False,
    db_type='postgresql',
    db_host='localhost',
    db_port=None,
    db_name='logs',
    db_user='postgres',
    db_password='',
    db_level=logging.DEBUG,
    HANDLER: RichColorLogHandler = RichColorLogHandler,
) -> logging.Logger:
    """
    Setup enhanced logging with Rich formatting and multiple output handlers.
    
    Returns:
        logging.Logger: Configured logger instance
    """

    if exceptions is None:
        exceptions = []

    if isinstance(level, str):
        level=getattr(logging, level.upper())
    else:
        level=level

    if not show:
        level = 'CRITICAL'
        os.environ['NO_LOGGING'] = '1'
        logging.basicConfig(level=logging.CRITICAL)

    if _check_logging_disabled():
        return logging.getLogger(name)

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): 
                logging.getLogger(str(i)).setLevel(logging.CRITICAL)
    
    logger = logging.getLogger(name) 
    logger.__class__ = CustomLogger
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # if basic: logging.basicConfig(level=level)

    # Auto-generate log_file_name if needed
    if log_file_name is None and log_file:
        try:
            main_file = inspect.stack()[-1].filename
            if not main_file or main_file.startswith('<') or not main_file.endswith(('.py', '.pyc')):
                log_file_name = "app.log"
            else:
                base = os.path.splitext(os.path.basename(main_file))[0]
                log_file_name = f"{base}.log"
        except Exception:
            log_file_name = "app.log"
    
    # ===== File handler =====
    if log_file and log_file_name:
        if isinstance(log_file_level, str):
            log_file_level = getattr(logging, log_file_level.upper(), logging.INFO)
        
        file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
        file_handler.setLevel(log_file_level)
        
        class LevelBasedFileFormatter(logging.Formatter):
            """Formatter with different formats for different log levels."""
            
            info_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)"
            debug_format = "%(asctime)s - %(levelname)s - %(name)s - %(process)d - %(thread)d - %(funcName)s - %(message)s (%(pathname)s:%(lineno)d)"
            
            def __init__(self):
                super().__init__()
                self.info_formatter = logging.Formatter(self.info_format)
                self.debug_formatter = logging.Formatter(self.debug_format)
            
            def format(self, record):
                if record.levelno <= logging.DEBUG:
                    return self.debug_formatter.format(record)
                else:
                    return self.info_formatter.format(record)
        
        file_handler.setFormatter(LevelBasedFileFormatter())
        logger.addHandler(file_handler)
    
    # ===== Console Handler =====
    if RICH_AVAILABLE:
        rich_handler = HANDLER(
            lexer=lexer,
            show_background=show_background,
            show_time=show_time,
            omit_repeated_times=omit_repeated_times,
            show_level=show_level,
            show_path=show_path,
            enable_link_path=enable_link_path,
            highlighter=highlighter,
            markup=markup,
            rich_tracebacks=rich_tracebacks,
            tracebacks_width=tracebacks_width,
            tracebacks_extra_lines=tracebacks_extra_lines,
            tracebacks_theme=tracebacks_theme or 'fruity',
            tracebacks_word_wrap=tracebacks_word_wrap,
            tracebacks_show_locals=show_locals or tracebacks_show_locals,
            tracebacks_suppress=tracebacks_suppress,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            log_time_format=log_time_format,
            keywords=keywords,
            show_icon=show_icon,
            icon_first=icon_first,
        )
        rich_handler.setLevel(level)
        rich_handler.setFormatter(CustomRichFormatter(
            lexer=lexer,
            show_background=show_background,
            theme=theme,
            icon_first=icon_first
        ))
        if icon_first:
            icon_filter = IconFilter(icon_first=True)
            rich_handler.addFilter(icon_filter)

        logger.addHandler(rich_handler)
    else:
        console_handler = AnsiLogHandler(
            lexer=lexer,
            show_background=show_background,
            format_template=None,
            show_time=show_time,
            show_name=True,
            show_pid=True,
            show_level=show_level,
            show_path=show_path,
            show_icon=show_icon,
            icon_first=icon_first,
        )
        logger.addHandler(console_handler)
    
    # ===== RabbitMQ Handler =====
    if rabbitmq:
        try:
            rabbitmq_handler = RabbitMQHandler(
                host=rabbitmq_host,
                port=rabbitmq_port,
                exchange=rabbitmq_exchange,
                username=rabbitmq_username,
                password=rabbitmq_password,
                vhost=rabbitmq_vhost,
                level=rabbitmq_level
            )
            logger.addHandler(rabbitmq_handler)
        except Exception as e:
            logging.error(f"Failed to setup RabbitMQ handler: {e}")
    
    # ===== Kafka Handler =====
    if kafka:
        try:
            kafka_handler = KafkaHandler(
                host=kafka_host,
                port=kafka_port,
                topic=kafka_topic,
                use_level_in_topic=kafka_use_level_in_topic,
                level=kafka_level
            )
            logger.addHandler(kafka_handler)
        except Exception as e:
            logging.error(f"Failed to setup Kafka handler: {e}")
    
    # ===== ZeroMQ Handler =====
    if zeromq:
        try:
            zeromq_handler = ZeroMQHandler(
                host=zeromq_host,
                port=zeromq_port,
                socket_type=zeromq_socket_type,
                level=zeromq_level
            )
            logger.addHandler(zeromq_handler)
        except Exception as e:
            logging.error(f"Failed to setup ZeroMQ handler: {e}")
    
    # ===== Syslog Handler =====
    if syslog:
        try:
            syslog_handler = SyslogHandler(
                host=syslog_host,
                port=syslog_port,
                facility=syslog_facility,
                level=syslog_level
            )
            syslog_formatter = logging.Formatter(
                '%(name)s[%(process)d]: %(levelname)s - %(message)s'
            )
            syslog_handler.setFormatter(syslog_formatter)
            logger.addHandler(syslog_handler)
        except Exception as e:
            logging.error(f"Failed to setup Syslog handler: {e}")
    
    # ===== Database Handler =====
    if db:
        try:
            db_handler = DatabaseHandler(
                db_type=db_type,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                level=db_level
            )
            logger.addHandler(db_handler)
        except Exception as e:
            logging.error(f"Failed to setup Database handler: {e}")
    
    # Prevent propagation to root logger if this is a named logger
    if name:
        logger.propagate = False
    
    return logger

def get_def() -> str:
    """Get current function/class definition name for logging context."""
    name = ''
    
    try:
        frame = inspect.stack()[1]
        name = str(frame.function)
    except (IndexError, AttributeError) as e:
        logging.debug("Error getting name from stack[1]: %s", e)
    
    if not name:
        try:
            frame = inspect.stack()[2]
            name = str(frame.function)
        except (IndexError, AttributeError) as e:
            logging.debug("Error getting name from stack[2]: %s", e)
    
    if not name or name == "<module>":
        try:
            frame = inspect.stack()[1]
            self_obj = frame.frame.f_locals.get('self')
            if self_obj:
                class_name = self_obj.__class__.__name__
                if class_name != "NoneType":
                    name = f"[#00ffff]({class_name}) --> "
        except Exception as e:
            logging.debug("Error getting class from stack[1]: %s", e)
        
        if not name or name == "<module>":
            try:
                for frame_info in inspect.stack()[3:]:
                    if isinstance(frame_info.lineno, int) and frame_info.function != '<module>':
                        name = f"[#ff5500]{frame_info.function}\\[[white on red]{frame_info.lineno}][/] --> "
                        break
            except Exception as e:
                logging.debug("Error scanning stack: %s", e)
    
    if not name or name == "<module>":
        try:
            filename = os.path.basename(inspect.stack()[0].filename)
            name = filename
        except Exception as e:
            logging.debug("Error getting filename: %s", e)
            name = "unknown"
    
    return name or "unknown"

# ==================== Helper Functions ====================

def _is_notebook():
    """Check if running in Jupyter/IPython notebook."""
    try:
        from IPython import get_ipython
        if 'IPKernelApp' in get_ipython().config:
            return True
    except (ImportError, AttributeError):
        pass
    return False

def suppress_async_warning():
    """Suppress async warnings in Jupyter/IPython."""
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning, 
                          message='coroutine.*was never awaited')

def getLogger(*args, **kwargs):
    kwargs.update({'HANDLER': RichColorLogHandler2})
    return setup_logging(*args, **kwargs)

def getLogger1(name=None, show_icon=True, show_time=True, show_level=False, 
              show_path=False, level=logging.DEBUG, icon_first=False, 
              show_background=True, force_color=None, lexer=None):
    """
    Quick logger setup with icon support.
    
    Args:
        name (str, optional): Logger name
        show_icon (bool): Show emoji icons
        show_time (bool): Show timestamp
        show_level (bool): Show log level text
        show_path (bool): Show file path
        level (int): Logging level
        icon_first (bool): If True, icon appears before datetime
        show_background (bool): Show background colors for log levels
        force_color (bool, optional): Force color output
        lexer (str, optional): Syntax lexer for highlighting
        
    Returns:
        logging.Logger: Configured logger with icons
    """
    _configure_ipython_logging()

    use_rich = RICH_AVAILABLE and console

    # if use_rich:
    #     logging.setLoggerClass(RichLogger)
    # else:
    logging.setLoggerClass(CustomLogger)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    if _is_ipython() and force_color is None:
        use_rich = False
    
    if force_color is False:
        use_rich = False

    if use_rich:
        try:
            handler = RichColorLogHandler(
                lexer=lexer,
                show_time=show_time,
                show_level=show_level,
                show_path=show_path,
                show_icon=show_icon,
                icon_first=icon_first,
                show_background=show_background,
                markup=False,
                omit_repeated_times=True,
            )
            logger.addHandler(handler)
        except Exception:
            use_rich = False
    
    if not use_rich:
        handler = AnsiLogHandler(
            lexer=lexer,
            show_time=show_time,
            show_path=show_path,
            icon_first=icon_first,
            show_background=show_background,
            show_name=True,
            show_pid=False,
            show_level=show_level,
            show_icon=show_icon,
        )
        logger.addHandler(handler)

    logger.propagate = False

    return logger

def getLoggerSimple(name=None, show_icon=True, icon_first=False, 
                    show_background=True, level=logging.DEBUG):
    """
    Simple logger without Rich - perfect for IPython/Jupyter.
    Uses basic ANSI colors, no async issues.
    
    Args:
        name (str, optional): Logger name
        show_icon (bool): Show emoji icons
        icon_first (bool): Icon before datetime
        show_background (bool): Background colors
        level (int): Logging level
        
    Returns:
        logging.Logger: Simple configured logger
    """
    _configure_ipython_logging()
    
    logging.setLoggerClass(CustomLogger)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    handler = AnsiLogHandler(
        show_time=True,
        show_path=False,
        icon_first=icon_first,
        show_background=show_background,
        show_name=False,
        show_pid=False,
        show_level=False,
        show_icon=show_icon,
    )
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

# ==================== Test Functions ====================

def test():
    """Test function to verify logger setup with different configurations."""
    logger = setup_logging_custom()
    
    if console:
        console.print("[italic]Test function to verify logger setup (CustomFormatter).[/]\n")
    else:
        print("Test function to verify logger setup (CustomFormatter).\n")
    
    logger.emergency("This is an emergency message")
    logger.alert("This is an alert message")
    logger.critical("This is a critical message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.info("This is an info message")
    logger.debug("This is a debug message")
    print("=" * shutil.get_terminal_size()[0])
    
    if RICH_AVAILABLE:
        logger = setup_logging(log_file=True, log_file_level='DEBUG')
        
        if console:
            console.print("[italic]Test function (CustomRichFormatter) with File Logging.[/]\n")
        else:
            print("Test function (CustomRichFormatter) with File Logging.\n")
        
        logger.emergency("This is an emergency message")
        logger.alert("This is an alert message")
        logger.critical("This is a critical message")
        logger.error("This is an error message")
        logger.warning("This is a warning message")
        logger.notice("This is a notice message")
        logger.info("This is an info message")
        logger.debug("This is a debug message - will have detailed format in file")
        print("=" * shutil.get_terminal_size()[0])
        
        logger = setup_logging(show_background=False)
        
        if console:
            console.print("[italic]Test function (CustomRichFormatter), No Background.[/]\n")
        else:
            print("Test function (CustomRichFormatter), No Background.\n")
        
        logger.emergency("This is an emergency message")
        logger.alert("This is an alert message")
        logger.critical("This is a critical message")
        logger.error("This is an error message")
        logger.warning("This is a warning message")
        logger.notice("This is a notice message")
        logger.info("This is an info message")
        logger.debug("This is a debug message")


def test_brokers():
    """Test message broker handlers."""
    if console:
        console.print("\n[bold cyan]Testing Message Broker Handlers[/]\n")
    else:
        print("\nTesting Message Broker Handlers\n")
    
    logger = setup_logging(
        name='broker_test',
        level='DEBUG',
        log_file=True,
        log_file_name='broker_test.log',
    )
    
    if console:
        console.print("[yellow]Testing all log levels with brokers...[/]\n")
    else:
        print("Testing all log levels with brokers...\n")
    
    logger.debug("Debug message - testing brokers")
    logger.info("Info message - testing brokers")
    logger.notice("Notice message - testing brokers")
    logger.warning("Warning message - testing brokers")
    logger.error("Error message - testing brokers")
    logger.critical("Critical message - testing brokers")
    logger.alert("Alert message - testing brokers")
    logger.emergency("Emergency message - testing brokers")
    
    if console:
        console.print("\n[green]Broker tests completed![/]")
        console.print("[dim]Note: Enable specific brokers by passing parameters to setup_logging()[/]\n")
    else:
        print("\nBroker tests completed!")
        print("Note: Enable specific brokers by passing parameters to setup_logging()\n")


def test_lexer():
    """Test lexer functionality with both setup_logging and getLogger."""
    print("\n" + "=" * 70)
    print("TESTING LEXER FUNCTIONALITY")
    print("=" * 70 + "\n")
    
    # Test 1: setup_logging with lexer
    print("Test 1: setup_logging() with lexer parameter")
    print("-" * 70)
    logger1 = setup_logging(name='test_setup', level='DEBUG', lexer='python')
    
    code_sample = """def hello():
    print("Hello World")
    return True"""
    
    logger1.info("Python code sample:", extra={'lexer': 'python'})
    logger1.debug(code_sample, extra={'lexer': 'python'})
    
    # Test 2: getLogger with lexer
    print("\nTest 2: getLogger() with lexer parameter")
    print("-" * 70)
    logger2 = getLogger('test_get', level=logging.DEBUG, lexer='python')
    
    logger2.info("Another Python code sample:")
    logger2.debug(code_sample, extra={'lexer': 'python'})
    
    # Test 3: Without lexer
    print("\nTest 3: Without lexer (normal text)")
    print("-" * 70)
    logger3 = getLogger('test_plain', level=logging.DEBUG)
    logger3.info("Regular info message without syntax highlighting")
    logger3.debug("Regular debug message without syntax highlighting")
    
    print("\n" + "=" * 70)
    print("LEXER TEST COMPLETED")
    print("=" * 70 + "\n")


def run_test():
    """Run comprehensive tests for the logger."""
    test()
    
    print(f"\nget_def() test: {get_def()}")
    
    try:
        from .example_usage import main as example, ExampleClass
    except (ImportError, ValueError):
        try:
            from example_usage import main as example, ExampleClass
        except ImportError:
            print("\nSkipping example_usage tests (module not found)")
            example = None
            ExampleClass = None
    
    if example:
        example()
    
    if ExampleClass:
        obj = ExampleClass()
        result = obj.example_method()
        print(f"Result: {result}")
    
    print()
    print("=" * shutil.get_terminal_size()[0])
    print("Check log file 'app.log' for file logging output.")
    print("DEBUG level logs will have detailed format with process/thread info.\n")

    if not RICH_AVAILABLE:
        print("Rich library not available. Skipping Rich-specific tests.\n")
        return

    print("Example usage of RichColorLogFormatter for default logger:\n")
    
    handler = logging.StreamHandler()
    formatter = RichColorLogFormatter(
        fmt="%(log_color)s[%(levelname)s]%(reset)s %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    try:
        import requests
        
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        resp = requests.get("https://httpbin.org/get", timeout=5)
        print(f"Response status: {resp.status_code}")
    except ImportError:
        print("Requests library not available. Skipping requests test.")
    except Exception as e:
        print(f"Error during requests test: {e}")
    
    print()
    print("Example usage of setup_logging for default logger:\n")
    
    logger = setup_logging(level='DEBUG', show_background=True)

    for name in ("urllib3", "requests", "chardet"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
        lg.setLevel(logging.DEBUG)

    try:
        import requests
        
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        resp = requests.get("https://httpbin.org/get", timeout=5)
        logger.info("Request completed with status %s", resp.status_code)
    except ImportError:
        logger.info("Requests library not available for final test")
    except Exception as e:
        logger.error("Error during final requests test: %s", e)
    
    # Test broker handlers
    test_brokers()
    
    # Test lexer functionality
    test_lexer()


if __name__ == "__main__":
    run_test()

    logger = setup_logging(level='DEBUG', show_background=True)
    logger.critical("This is a critical message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.notice("This is a notice message")
    logger.info("This is an info message")
    logger.debug("This is a debug message")
    print("=" * shutil.get_terminal_size()[0])
    
    logger = setup_logging_custom(show_background=False)
    
    if console:
        console.print("[italic]Test function (CustomFormatter), No Background Color.[/]\n")
    else:
        print("Test function (CustomFormatter), No Background Color.\n")
    
    logger.emergency("This is an emergency message")
    logger.alert("This is an alert message")
    