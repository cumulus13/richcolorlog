=======
Filters
=======

Filters provide fine-grained control over which log records are processed.

IconFilter
----------

Built-in filter that adds emoji icons to log records.

.. code-block:: python

   from richcolorlog.logger import IconFilter

   filter = IconFilter(icon_first=True)

   # Adds record.icon attribute based on level:
   # DEBUG    → 🐛
   # INFO     → 🔔
   # NOTICE   → 📢
   # WARNING  → ⛔
   # ERROR    → ❌
   # CRITICAL → 💥
   # FATAL    → 💀
   # ALERT    → 🚨
   # EMERGENCY → 🆘

Usage with Handler
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from richcolorlog.logger import IconFilter, AnsiLogHandler

   handler = AnsiLogHandler()
   handler.addFilter(IconFilter(icon_first=True))

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Creating Custom Filters
-----------------------

Level Filter
~~~~~~~~~~~~

.. code-block:: python

   import logging

   class LevelRangeFilter(logging.Filter):
       """Only allow logs within a level range."""

       def __init__(self, min_level, max_level):
           super().__init__()
           self.min_level = min_level
           self.max_level = max_level

       def filter(self, record):
           return self.min_level <= record.levelno <= self.max_level


   # Only WARNING and ERROR (not CRITICAL)
   handler.addFilter(LevelRangeFilter(
       logging.WARNING,
       logging.ERROR
   ))

Module Filter
~~~~~~~~~~~~~

.. code-block:: python

   class ModuleFilter(logging.Filter):
       """Filter by module name."""

       def __init__(self, modules, exclude=False):
           super().__init__()
           self.modules = set(modules)
           self.exclude = exclude

       def filter(self, record):
           match = record.module in self.modules
           return not match if self.exclude else match


   # Only logs from specific modules
   handler.addFilter(ModuleFilter(['auth', 'api']))

   # Exclude noisy modules
   handler.addFilter(ModuleFilter(['urllib3', 'requests'], exclude=True))

Message Filter
~~~~~~~~~~~~~~

.. code-block:: python

   import re

   class MessageFilter(logging.Filter):
       """Filter based on message content."""

       def __init__(self, patterns, exclude=False):
           super().__init__()
           self.patterns = [re.compile(p) for p in patterns]
           self.exclude = exclude

       def filter(self, record):
           msg = record.getMessage()
           match = any(p.search(msg) for p in self.patterns)
           return not match if self.exclude else match


   # Only logs containing "user" or "auth"
   handler.addFilter(MessageFilter([r'user', r'auth']))

   # Exclude health check logs
   handler.addFilter(MessageFilter([r'health', r'ping'], exclude=True))

Rate Limit Filter
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from collections import defaultdict

   class RateLimitFilter(logging.Filter):
       """Limit repeated log messages."""

       def __init__(self, rate=1.0, per=60.0):
           super().__init__()
           self.rate = rate
           self.per = per
           self.last_logged = defaultdict(float)
           self.counts = defaultdict(int)

       def filter(self, record):
           key = (record.name, record.levelno, record.msg)
           now = time.time()

           if now - self.last_logged[key] >= self.per / self.rate:
               if self.counts[key] > 0:
                   record.msg = f"{record.msg} (repeated {self.counts[key]} times)"
               self.last_logged[key] = now
               self.counts[key] = 0
               return True

           self.counts[key] += 1
           return False


   # Max 1 message per 60 seconds for duplicates
   handler.addFilter(RateLimitFilter(rate=1, per=60))

Context Filter
~~~~~~~~~~~~~~

.. code-block:: python

   import threading

   class ContextFilter(logging.Filter):
       """Add context data to log records."""

       def __init__(self):
           super().__init__()
           self.context = threading.local()

       def set_context(self, **kwargs):
           for key, value in kwargs.items():
               setattr(self.context, key, value)

       def clear_context(self):
           self.context = threading.local()

       def filter(self, record):
           for key in dir(self.context):
               if not key.startswith('_'):
                   setattr(record, key, getattr(self.context, key))
           return True


   # Usage
   ctx_filter = ContextFilter()
   handler.addFilter(ctx_filter)

   ctx_filter.set_context(request_id='abc123', user_id=42)
   logger.info("Processing request")  # Has request_id and user_id

Sampling Filter
~~~~~~~~~~~~~~~

.. code-block:: python

   import random

   class SamplingFilter(logging.Filter):
       """Sample logs at a given rate."""

       def __init__(self, rate=0.1, levels=None):
           super().__init__()
           self.rate = rate
           self.levels = levels or [logging.DEBUG]

       def filter(self, record):
           if record.levelno in self.levels:
               return random.random() < self.rate
           return True


   # Sample 10% of DEBUG logs
   handler.addFilter(SamplingFilter(rate=0.1, levels=[logging.DEBUG]))

Sensitive Data Filter
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import re

   class SensitiveDataFilter(logging.Filter):
       """Mask sensitive data in log messages."""

       PATTERNS = [
           (r'\b\d{16}\b', '****-****-****-****'),  # Credit card
           (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),  # SSN
           (r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'password=***'),
           (r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'api_key=***'),
       ]

       def filter(self, record):
           msg = record.getMessage()
           for pattern, replacement in self.PATTERNS:
               msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
           record.msg = msg
           record.args = ()
           return True


   handler.addFilter(SensitiveDataFilter())

Combining Filters
-----------------

Multiple filters are AND-ed together:

.. code-block:: python

   handler.addFilter(ModuleFilter(['auth', 'api']))
   handler.addFilter(LevelRangeFilter(logging.INFO, logging.ERROR))
   handler.addFilter(SensitiveDataFilter())

   # Only logs that pass ALL filters are emitted

Filter Placement
----------------

Filters can be added to loggers or handlers:

.. code-block:: python

   # Logger-level filter (affects all handlers)
   logger.addFilter(ContextFilter())

   # Handler-level filter (affects only this handler)
   file_handler.addFilter(LevelRangeFilter(logging.WARNING, logging.CRITICAL))
   console_handler.addFilter(LevelRangeFilter(logging.DEBUG, logging.INFO))