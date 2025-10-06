import logging

# Try to import Rich
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.logging import RichHandler
    from rich.theme import Theme

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter

    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


if RICH_AVAILABLE:
    custom_theme = Theme({
        "log.time": "cyan",
        "log.level.debug": "bold #FFAA00",
        "log.level.info": "bold #00ffff",
        "log.level.warning": "black on yellow",
        "log.level.error": "white on red",
        "log.level.critical": "bold white on magenta",
        "log.message": "white",
    })
    console = Console(theme=custom_theme)

    class SyntaxRichHandler(RichHandler):
        def render_message(self, record, message):
            lexer = getattr(record, "lexer", None)
            if lexer:
                return Syntax(message, lexer, theme="monokai", line_numbers=False)
            return super().render_message(record, message)

    class RichLogger(logging.Logger):
        def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
            if extra is None:
                extra = {}
            if "lexer" in kwargs:
                extra["lexer"] = kwargs.pop("lexer")
            super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

    logging.setLoggerClass(RichLogger)
    handler = SyntaxRichHandler(console=console, show_time=True, show_level=True, show_path=False)
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

else:
    # Fallback handler with pygments or plain text
    class FallbackHandler(logging.StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            lexer = getattr(record, "lexer", None)
            if lexer and PYGMENTS_AVAILABLE:
                try:
                    lexer_obj = get_lexer_by_name(lexer)
                    msg = highlight(msg, lexer_obj, TerminalFormatter())
                except Exception:
                    pass  # If it fails, keep plain text
            self.stream.write(msg + "\n")
            self.flush()

    class FallbackLogger(logging.Logger):
        def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
            if extra is None:
                extra = {}
            if "lexer" in kwargs:
                extra["lexer"] = kwargs.pop("lexer")
            super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

    logging.setLoggerClass(FallbackLogger)
    handler = FallbackHandler()
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])


# 🚀 Example Usage
logger = logging.getLogger("ZMQServer")

logger.debug("print('hello')", lexer="python")
logger.info("SELECT * FROM users;", lexer="sql")
logger.warning("Normal warning tanpa lexer")
