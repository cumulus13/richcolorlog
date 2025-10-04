#!/usr/bin/env python3
# file: richcolorlog/logger3.py
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
    from typing import Callable
    FormatTimeCallable = Callable[[float], str]

try:
    from rich.logging import RichHandler
    from rich.text import Text
    from rich.console import Console
    from rich.syntax import Syntax
    from rich import traceback as rich_traceback
    from rich.markup import escape as rich_escape
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None


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
        import os
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


# ==================== Icon Support ====================

class Icon:
    """Icon mappings for different log levels."""
    debug     = "🐞"
    info      = "ℹ️"
    notice    = "🔔"
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

# 🛠️ Custom Logger: Override ._log so you can accept Lexer
class RichLogger(logging.Logger):
    print("3"*os.get_terminal_size()[0])
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        print("4"*os.get_terminal_size()[0])
        if extra is None:
            extra = {}
        if "lexer" in kwargs:
            extra["lexer"] = kwargs.pop("lexer")
        print(f"EXTRA: {extra}")
        print(f"LEXER RichLogger: {extra.get('lexer')}")
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

class AnsiLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        if extra is None:
            extra = {}
        if "lexer" in kwargs:
            extra["lexer"] = kwargs.pop("lexer")
        print(f"LEXER AnsiLogger: {lexer}")
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

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
            'reset': "\x1b[0m"
        })
    
    FORMAT_TEMPLATE = "%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(
        self,
        show_background:bool = True,
        format_template: Optional[str] = "[%(levelname)s] %(message)s",
        show_time:bool = True,
        show_name:bool = True,
        show_pid:bool = True,
        show_level:bool = True,
        show_path:bool = True,
        icon_first:bool = False,  # NEW PARAMETER
        lexer:str = '',
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

                'WARNING': "\x1b[38;2;255;255;0m",    # yellow
                'ERROR': "\x1b[31m",                  # red
                'CRITICAL': "\x1b[38;2;85;0;0m",      # #550000
                'FATAL': "\x1b[38;2;0;85;255m",       # #0055FF
                'EMERGENCY': "\x1b[38;2;170;0;255m",  # #AA00FF
                'ALERT': "\x1b[38;2;0;85;0m",         # #005500
                'NOTICE': "\x1b[38;2;0;255;255m",     # #00FFFF
            })

        self._build_formatters()
        
    def _build_formatters(self):
        if self.use_colors:
            self.formatters = {
                logging.DEBUG: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['debug'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.INFO: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['info'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.WARNING: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['warning'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.ERROR: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['error'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                logging.CRITICAL: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                CRITICAL_LEVEL: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['critical'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                EMERGENCY_LEVEL: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['emergency'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                ALERT_LEVEL: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['alert'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
                NOTICE_LEVEL: logging.Formatter(self.check_icon_first(self.icon_first) + self.COLORS['notice'] + self.FORMAT_TEMPLATE + self.COLORS['reset']),
            }
        else:
            self.formatters = {level: logging.Formatter(self.FORMAT_TEMPLATE) for level in logging_levels_list}

    def _build_format_template(self, show_time, show_name, show_pid, show_level, show_path) -> str:
        """Build format template based on options."""
        parts = []
        # Add icon placeholder if icon_first is True
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

    def _supports_color1(self) -> bool:
        """Check if terminal supports color output."""
        try:
            return (
                hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
                os.environ.get('TERM') != 'dumb' and
                os.environ.get('NO_COLOR') is None
            )
        except (AttributeError, OSError):
            return False

    def _supports_color(self) -> bool:
        if os.getenv("FORCE_COLOR", "").lower() in ("1", "true"):
            return True
        if os.getenv("NO_COLOR") is not None:
            return False
        try:
            return sys.stdout.isatty() and os.getenv("TERM") != "dumb"
        except Exception:
            return False

    def check_icon_first(self, icon_first = True):
        if icon_first:
            return "%(icon)s "
        else:
            return ''

    @performance_monitor
    def format(self, record: logging.LogRecord) -> str:
        # Pastikan icon selalu ada
        if not hasattr(record, "icon"):
            record.icon = ""

        # Pilih formatter berdasarkan level
        formatter = getattr(self, "formatters", {}).get(record.levelno, None)
        
        # Jika tidak ada, gunakan default formatter
        if formatter is None:
            formatter = getattr(self, "default_formatter", None)
            if formatter is None:
                # Buat fallback formatter on the fly
                formatter = logging.Formatter(self.FORMAT_TEMPLATE)

        try:
            msg = formatter.format(record)
        except Exception as e:
            # Jangan biarkan logging crash
            msg = f"[FORMATTER ERROR] {record.getMessage()} - {str(e)}"

        return msg

class CustomRichFormatter1(logging.Formatter):
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

    def __init__(self, lexer: Optional[str] = None, show_background: bool = True, theme: str = "fruity", icon_first = True):
        """Initialize EnhancedRichFormatter."""
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
    def format(self, record: logging.LogRecord) -> Union[Text, str]:
        """Format log record with Rich styling."""
        try:
            lexer = getattr(record, "lexer", self.lexer or None)
            level_style = self.LEVEL_STYLES[record.levelno] or ""
            
            # Build prefix
            prefix = f"{record.levelname} - ({record.filename}:{record.lineno}) "
            if self.icon_first and hasattr(record, 'icon'):
                prefix = f"{record.icon} " + prefix
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

class CustomRichFormatter(logging.Formatter):
    LEVEL_STYLES = {
        logging.DEBUG: "bold #FFAA00",
        logging.INFO: "bold #00FFFF",
        logging.WARNING: "black on #FFFF00",
        logging.ERROR: "white on red",
        logging.CRITICAL: "bright_white on #550000",
        FATAL_LEVEL: "bright_white on #0055FF",
        EMERGENCY_LEVEL: "bright_white on #AA00FF",
        ALERT_LEVEL: "bright_white on #005500",
        NOTICE_LEVEL: "black on #00FFFF",
    }

    def __init__(self, lexer: Optional[str] = None, show_background: bool = True, theme: str = "fruity", icon_first=True):
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

    def format(self, record: logging.LogRecord) -> str:
    
        # Dapatkan style warna untuk level ini
        style = self.LEVEL_STYLES.get(record.levelno, "")
        levelname = record.levelname
        location = f"({record.filename}:{record.lineno})"
        
        # Ambil pesan asli (sudah diproses oleh IconFilter jika icon_first=False)
        raw_message = record.getMessage()
        safe_message = rich_escape(raw_message)  # Escape agar markup tidak bentrok

        # Ambil icon hanya jika icon_first=True
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
            theme=theme,
            icon_first=True,
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
                start = self.COLORS.get(key, "")
                reset = self.COLORS.get("reset", "")
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
            # Declare exchange sebagai topic untuk routing berdasarkan level
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
            # routing_key is level name (debug, info, warning, error, critical, etc.)
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
                    delivery_mode=2,  # make message persistent
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
    """
    Handler to send log to Kafka.
    Saran: Use topics based on level (logs.debug, logs.info, etc.)
    Or use a single topic with a level as a key for partitioning.
    """
    
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
        """
        Emit log record to Kafka.
        Opsi 1: Single topic, level as key for partitioning
        Opsi 2: Multiple topics based on levels (logs.debug, logs.info, etc.)
        """
        if not self.producer:
            return
        
        try:
            level_name = record.levelname.lower()
            
            # Determine topics based on configuration
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
            
            # Kirim dengan level sebagai key untuk partitioning yang konsisten
            self.producer.send(
                topic=topic,
                key=level_name,  # Key untuk partitioning
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
    """
    Handler to send log to Zeromq.
    Suggestion: Use a pub/sub pattern with topic = level for filtering in subscriber.
    """
    
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
        """
        Emit log record to ZeroMQ.
        Format: [topic] [message]
        Topic is a level name for filtering in subscriber side.
        """
        if not self.socket:
            return
        
        try:
            topic = record.levelname.lower()  # Topic = level for filtering
            
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
            
            # Send with topic prefix untuk PUB/SUB filtering
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
            # Map log level ke syslog severity
            severity = SYSLOG_SEVERITY_MAP.get(record.levelno, 7)  # default to DEBUG
            
            # Calculate priority (facility * 8 + severity)
            priority = self.encodePriority(self.facility, severity)
            
            # Format message
            msg = self.format(record)
            
            # Send to syslog
            msg = self.ident + msg + '\000'
            
            # Prepend priority
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
        except Exception as e:
            self.handleError(record)

class DatabaseHandler(logging.Handler):
    """
    Handler to send log to the database.
    Each level has its own table + Syslog table for all logs.
    """
    
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
            
            # Define table schema
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
            
            # Create table for each level
            for table_name in LEVEL_TO_TABLE.values():
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {table_schema}
                    )
                """)
            
            # CREATE SYSLOG TABLE for all logs
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
        """Emit log record to database (2 tables: level-specific + syslog)."""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare data
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
            
            # SQL query
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
            
            # Insert to table based on level
            level_table = LEVEL_TO_TABLE.get(record.levelno, 'log_info')
            cursor.execute(sql.format(level_table), data)
            
            # Insert to Table Syslog (all logs)
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

# ==================== Rich Handler ====================

class AnsiLogHandler(logging.StreamHandler):
    """Custom Handler with enhanced color formatting and icon Ansi support ."""
    
    # Icon mapping untuk setiap level
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
    }
    
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
        super().__init__()  # ← BARIS BARU: WAJIB!

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
            icon_filter = IconFilter(icon_first=icon_first)  # NEW
            self.addFilter(icon_filter)
        
        
    def emit(self, record):
        """Emit a record with pygments highlighting + icon."""
        try:
            msg = self.format(record)  # basic formatting
            msg = self.render_message(record, record.getMessage())
            self.stream.write(msg + "\n")
            self.flush()
        except Exception:
            self.handleError(record)

    def render_message(self, record, message):
        """Apply lexer highlighting (pygments) and add icon."""
        # Get lexer for this record
        lexer_name = getattr(record, "lexer", self.lexer)
        try:
            lexer_obj = get_lexer_by_name(lexer_name) if lexer_name else TextLexer()
        except Exception:
            lexer_obj = TextLexer()

        try:
            rendered = highlight(str(message), lexer_obj, TerminalFormatter()).rstrip()
        except Exception:
            rendered = str(message)

        # Add icon
        icon = ""
        if self.show_icon:
            icon = self.LEVEL_ICON_MAP.get(record.levelno, "")
        if icon:
            rendered = f"{icon} {rendered}" if self.icon_first else f"{rendered} {icon}"

        return rendered

if RICH_AVAILABLE:
    class RichColorLogHandler(RichHandler):
        """Custom RichHandler with enhanced color formatting and icon support."""

        def __init__(self, lexer=None, show_background=True, render_emoji=True, show_icon=True, icon_first=False, **kwargs):
            # simpan argumen custom
            self.lexer = lexer
            self.show_background = show_background
            self.show_icon = show_icon
            self.icon_first = icon_first
            self._render_emoji_flag = render_emoji

            kwargs.pop("lexer", None)
            kwargs.pop("show_background", None)
            kwargs.pop("render_emoji", None)
            kwargs.pop("show_icon", None)
            kwargs.pop("icon_first", None)

            super().__init__(**kwargs)

            self.markup = True
            self.emoji = render_emoji

            # aktifkan emoji di renderer Rich
            try:
                self._log_render.emojis = bool(self._render_emoji_flag)
            except Exception:
                pass

            if self.show_icon:
                icon_filter = IconFilter(icon_first=icon_first)  # NEW
                self.addFilter(icon_filter)

            self.setFormatter(CustomRichFormatter(lexer=self.lexer, show_background=self.show_background, icon_first=self.icon_first))

        # def emit(self, record):
        #     """Emit a record with icon and optional syntax highlighting."""
        #     # Handle lexer
        #     lexer_name = getattr(record, "lexer", None)
        #     if lexer_name:
        #         try:
        #             message = record.getMessage()
        #             syntax = Syntax(
        #                 message,
        #                 lexer_name,
        #                 theme=self.tracebacks_theme,
        #                 line_numbers=False,
        #                 word_wrap=True
        #             )
        #             record.msg = syntax  # Replace msg with Syntax object
        #         except Exception:
        #             pass  # fallback to plain text

        #     # Handle icon
        #     if self.show_icon:
        #         icon = self.LEVEL_ICON_MAP.get(record.levelno, "")
        #         if icon:
        #             if isinstance(record.msg, Text):
        #                 record.msg = Text(icon + " ", style="") + record.msg
        #             else:
        #                 msg_str = str(record.msg)
        #                 if not msg_str.startswith(icon):
        #                     record.msg = f"{icon} {msg_str}"

        #     try:
        #         super().emit(record)
        #     except Exception as e:
        #         self.handleError(record)

        # def render_message(self, record, message):
        #     """Custom render message with icon support."""
        #     use_markup = getattr(record, "markup", self.markup)
            
        #     # Get icon if enabled
        #     icon = ""
        #     if self.show_icon:
        #         icon = self.LEVEL_ICON_MAP.get(record.levelno, "")
            
        #     # Convert message to string first
        #     if isinstance(message, Text):
        #         message_str = message.plain
        #     else:
        #         message_str = str(message)
            
        #     # Add icon to message
        #     if icon:
        #         final_message = f"{icon} {message_str}"
        #     else:
        #         final_message = message_str
            
        #     # Return as Text object
        #     if use_markup:
        #         try:
        #             return Text.from_markup(final_message)
        #         except Exception:
        #             return Text(final_message)
        #     else:
        #         return Text(final_message)
    
else:
    CustomRichFormatter = CustomFormatter
    RichColorLogHandler = AnsiLogHandler
    RichLogger = AnsiLogger

# ==================== Setup Functions ====================

def setup_logging_custom(
    level: Union[str, int] = 'DEBUG',
    show_background=True,
    format_template=None,
    show_time=True,
    show_name=True,
    show_pid=True,
    show_level=True,
    show_path=True,
    icon_first=True,  # NEW PARAMETER
    exceptions=None,
    show=True,
):
    """Setup basic logging with custom formatter (ANSI colors)."""

    if _check_logging_disabled():
        return  # logging disabled, jangan pasang handler apapun

    if exceptions is None:
        exceptions = []
        
    if not show:
        level = 'CRITICAL'
        os.environ['NO_LOGGING'] = '1'
        
    if _check_logging_disabled():
        return logging.getLogger()

    if isinstance(level, str):
        logging.basicConfig(level=getattr(logging, level.upper()))
    else:
        logging.basicConfig(level=level)

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): 
                logging.getLogger(str(i)).setLevel(logging.CRITICAL)

    logger = logging.getLogger()

    for handler in logger.handlers:
        handler.setFormatter(CustomFormatter(
                show_background,
                format_template,
                show_time,
                show_name,
                show_pid,
                show_level,
                show_path,
                icon_first,  # NEW
            )
        )
    
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
) -> logging.Logger:
    """
    Setup enhanced logging with Rich formatting and multiple output handlers.
    
    Args:
        name (str, optional): Logger name
        lexer (str, optional): Syntax highlighter for code
        show_locals (bool): Show local variables in tracebacks
        level (Union[str, int]): Logging level
        show_level (bool): Show log level in console
        show_time (bool): Show timestamp in console
        omit_repeated_times (bool): Omit repeated timestamps
        show_path (bool): Show file path in console
        enable_link_path (bool): Enable clickable file paths
        highlighter: Rich highlighter instance
        markup (bool): Enable Rich markup in log messages
        rich_tracebacks (bool): Use Rich formatted tracebacks
        tracebacks_width (int, optional): Width of traceback display
        tracebacks_extra_lines (int): Extra lines in tracebacks
        tracebacks_theme (str, optional): Traceback syntax theme
        tracebacks_word_wrap (bool): Wrap long lines in tracebacks
        tracebacks_show_locals (bool): Show local variables in tracebacks
        tracebacks_suppress (Iterable): Modules to suppress in tracebacks
        locals_max_length (int): Max length of local variable representations
        locals_max_string (int): Max length of string representations
        log_time_format (Union[str, FormatTimeCallable]): Time format
        keywords (List[str], optional): Keywords to highlight
        show_background (bool): Show background colors for log levels
        exceptions (list): Logger names to set to CRITICAL level
        show (bool): Whether to show logs at all
        basic (bool): Whether to call logging.basicConfig
        
        # File Logging
        log_file (bool): Enable file logging
        log_file_name (str, optional): Log file path
        log_file_level (Union[str, int]): File logging level
        
        # RabbitMQ
        rabbitmq (bool): Enable RabbitMQ logging
        rabbitmq_host (str): RabbitMQ host
        rabbitmq_port (int): RabbitMQ port
        rabbitmq_exchange (str): RabbitMQ exchange name
        rabbitmq_username (str): RabbitMQ username
        rabbitmq_password (str): RabbitMQ password
        rabbitmq_vhost (str): RabbitMQ virtual host
        rabbitmq_level (int): RabbitMQ logging level
        
        # Kafka
        kafka (bool): Enable Kafka logging
        kafka_host (str): Kafka host
        kafka_port (int): Kafka port
        kafka_topic (str): Kafka topic name
        kafka_use_level_in_topic (bool): Use level in topic name (logs.debug, logs.info, etc)
        kafka_level (int): Kafka logging level
        
        # ZeroMQ
        zeromq (bool): Enable ZeroMQ logging
        zeromq_host (str): ZeroMQ host
        zeromq_port (int): ZeroMQ port
        zeromq_socket_type (str): Socket type ('PUB' or 'PUSH')
        zeromq_level (int): ZeroMQ logging level
        
        # Syslog
        syslog (bool): Enable syslog logging
        syslog_host (str): Syslog host
        syslog_port (int): Syslog port
        syslog_facility: Syslog facility
        syslog_level (int): Syslog logging level
        
        # Database
        db (bool): Enable database logging
        db_type (str): Database type ('postgresql', 'mysql', 'mariadb', 'sqlite')
        db_host (str): Database host
        db_port (int, optional): Database port
        db_name (str): Database name
        db_user (str): Database user
        db_password (str): Database password
        db_level (int): Database logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """

    print(f"RICH_AVAILABLE: {RICH_AVAILABLE}")
    # Set custom logger class
    if RICH_AVAILABLE:
        print("1"*os.get_terminal_size()[0])
        logging.setLoggerClass(RichLogger)
    else:
        print("2"*os.get_terminal_size()[0])
        logging.setLoggerClass(AnsiLogger)
   
    if _check_logging_disabled():
        return  # logging disabled, jangan pasang handler apapun
 
    if exceptions is None:
        exceptions = []
        
    if not show:
        level = 'CRITICAL'
        os.environ['NO_LOGGING'] = '1'
    
    # if _check_logging_disabled():
        # return logging.getLogger(name)

    logger = logging.getLogger(name)
    
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)
    
    logger.setLevel(level)

    if exceptions:
        for i in exceptions:
            if isinstance(i, str): 
                logging.getLogger(str(i)).setLevel(logging.CRITICAL)
    
    if basic:# and name is None:
        logging.basicConfig(level=level)

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

    # Clear existing handlers
    logger.handlers.clear()

    # ===== File handler with different formats for info and debug =====
    if log_file and log_file_name:
        # Convert log_file_level to int if string
        if isinstance(log_file_level, str):
            log_file_level = getattr(logging, log_file_level.upper(), logging.INFO)
        
        file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
        file_handler.setLevel(log_file_level)
        
        # Custom formatter that distinguishes formats based on levels
        class LevelBasedFileFormatter(logging.Formatter):
            """Formatter with different formats for different log levels."""
            
            # Format for info and level above
            info_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)"
            
            # Detailed format for debug
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
    
    # ===== Console Handler (Rich) =====
    if RICH_AVAILABLE:
        rich_handler = RichColorLogHandler(
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
        logger.addHandler(rich_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter(
            show_background=show_background,
            icon_first=icon_first  # NEW
        ))
        
        if show_icon:
            icon_filter = IconFilter(icon_first=icon_first)  # NEW
            console_handler.addFilter(icon_filter)
        
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
            # Format untuk syslog
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

def getLogger1(name=None, show_icon=True, show_time=True, show_level=False, 
              show_path=False, level=logging.DEBUG, icon_first=False, 
              show_background=True):  # NEW PARAMETER
    """
    Quick logger setup with icon support (simpler alternative to setup_logging).
    
    Args:
        name (str, optional): Logger name
        show_icon (bool): Show emoji icons
        show_time (bool): Show timestamp
        show_level (bool): Show log level text
        show_path (bool): Show file path
        level (int): Logging level
        icon_first (bool): If True, icon appears before datetime
        show_background (bool): Show background colors for log levels
        
    Returns:
        logging.Logger: Configured logger with icons
    
    Example:
        >>> logger = getLogger('myapp', show_background=True)
        >>> logger.info("Hello")  # ℹ️ Hello (with background color)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    if RICH_AVAILABLE and console:
        try:
            handler = RichColorLogHandler(
                show_time=show_time,
                show_level=show_level,
                show_path=show_path,
                show_icon=show_icon,
                icon_first=icon_first,
                show_background=show_background,  # NEW
                markup=False,
                omit_repeated_times=True,
            )
            logger.addHandler(handler)
        except Exception as e:
            handler = logging.StreamHandler()
            formatter = CustomFormatter(
                show_time=show_time, 
                show_path=show_path,
                icon_first=icon_first,
                show_background=show_background  # NEW
            )
            handler.setFormatter(formatter)
            
            if show_icon:
                icon_filter = IconFilter(icon_first=icon_first)
                handler.addFilter(icon_filter)
            
            logger.addHandler(handler)
    else:
        handler = logging.StreamHandler()
        formatter = CustomFormatter(
            show_time=show_time, 
            show_path=show_path,
            icon_first=icon_first,
            show_background=show_background  # NEW
        )
        handler.setFormatter(formatter)
        
        if show_icon:
            icon_filter = IconFilter(icon_first=icon_first)
            handler.addFilter(icon_filter)
        
        logger.addHandler(handler)
    
    logger.propagate = False
    return logger

def getLogger(name=None, show_icon=True, show_time=True, show_level=False, 
              show_path=False, level=logging.DEBUG, icon_first=False, 
              show_background=True, force_color=None, lexer=None):
    """
    Quick logger setup with icon support (simpler alternative to setup_logging).
    
    Args:
        name (str, optional): Logger name
        show_icon (bool): Show emoji icons
        show_time (bool): Show timestamp
        show_level (bool): Show log level text
        show_path (bool): Show file path
        level (int): Logging level
        icon_first (bool): If True, icon appears before datetime
        show_background (bool): Show background colors for log levels
        force_color (bool, optional): Force color output (None=auto, True=force, False=disable)
        
    Returns:
        logging.Logger: Configured logger with icons
    """
    # Configure IPython compatibility
    _configure_ipython_logging()

    # Detect if we should use Rich
    use_rich = RICH_AVAILABLE and console
    # print(f"use_rich [0]: {use_rich}")

    # Use custom logger class based on Rich availability
    if use_rich:
        logging.setLoggerClass(RichLogger)
    else:
        logging.setLoggerClass(AnsiLogger)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    # In IPython, prefer simple formatter to avoid async issues
    if _is_ipython() and force_color is None:
        # print("check 1 ...")
        use_rich = False
        # print(f"use_rich [1]: {use_rich}")
    
    if force_color is False:
        # print("check 2 ...")
        use_rich = False
        # print(f"use_rich [2]: {use_rich}")
    
    # print(f"use_rich [3]: {use_rich}")

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
            # print(f"set handler to RichColorLogHandler: {handler}")
            logger.addHandler(handler)
        except Exception as e:
            print(traceback.format_exc()    )
            # Fallback to basic handler
            use_rich = False
    
    # print(f"use_rich: {use_rich}")
    if not use_rich:
        # print("run with not use_rich ...")
        handler = AnsiLogHandler(
            show_time=show_time,
            show_path=show_path,
            icon_first=icon_first,
            show_background=show_background,
            show_name=True,
            show_pid=False,
            show_level=show_level,
            show_icon=show_icon,
            lexer=None  # bisa di-override per log
        )
    
    if show_icon:
        icon_filter = IconFilter(icon_first=icon_first)
        handler.addFilter(icon_filter)
    
    logger.addHandler(handler)

    # print(f"handler: {handler}")
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
    # Suppress IPython warnings
    _configure_ipython_logging()
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Always use basic handler (no Rich)
    handler = logging.StreamHandler()
    formatter = CustomFormatter(
        show_time=True,
        show_path=False,
        icon_first=icon_first,
        show_background=show_background,
        show_name=False,
        show_pid=False,
        show_level=False
    )
    handler.setFormatter(formatter)
    
    if show_icon:
        icon_filter = IconFilter(icon_first=icon_first)
        handler.addFilter(icon_filter)
    
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
    
    logger = setup_logging_custom(show_background=False)
    
    if console:
        console.print("[italic]Test function (CustomFormatter), No Background Color.[/]\n")
    else:
        print("Test function (CustomFormatter), No Background Color.\n")
    
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
    
    # Test with all brokers enabled (will fail gracefully if not available)
    logger = setup_logging(
        name='broker_test',
        level='DEBUG',
        log_file=True,
        log_file_name='broker_test.log',
        # Uncomment to test specific brokers
        # rabbitmq=True,
        # kafka=True,
        # zeromq=True,
        # syslog=True,
        # db=True,
        # db_type='sqlite',
        # db_name='test_logs.db',
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
        console.print("[dim]Note: Enable specific brokers by uncommenting parameters in test_brokers()[/]\n")
    else:
        print("\nBroker tests completed!")
        print("Note: Enable specific brokers by uncommenting parameters in test_brokers()\n")


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


if __name__ == "__main__":
    run_test()