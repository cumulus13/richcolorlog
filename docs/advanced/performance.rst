===========
Performance
===========

RichColorLog includes performance monitoring and optimization features.

Performance Tracker
-------------------

Built-in performance tracking for logging operations:

.. code-block:: python

   from richcolorlog.logger import _performance

   # After logging operations
   stats = _performance.get_stats()
   print(stats)

   # Output:
   # {
   #     'format': {'count': 1000, 'avg': 0.0001, 'min': 0.00005, 'max': 0.001},
   # }

Performance Decorator
---------------------

Monitor custom functions:

.. code-block:: python

   from richcolorlog.logger import performance_monitor

   @performance_monitor
   def my_expensive_operation():
       # ... do work
       pass

   # Stats recorded in _performance tracker

Optimization Tips
-----------------

1. Disable Unused Features
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       show_icon=False,        # Skip icon lookup
       show_path=False,        # Skip path resolution
       show_time=False,        # Skip time formatting
       rich_tracebacks=False,  # Skip rich traceback
       markup=False,           # Skip markup parsing
       lexer=None,             # Skip syntax highlighting
   )

2. Use Appropriate Handler
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from richcolorlog import setup_logging
   from richcolorlog.logger import AnsiLogHandler

   # ANSI handler is lighter than Rich handler
   logger = setup_logging(HANDLER=AnsiLogHandler)

3. Check Level Before Expensive Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   if logger.isEnabledFor(logging.DEBUG):
       # Only compute if DEBUG is enabled
       expensive_data = compute_debug_info()
       logger.debug(f"Debug info: {expensive_data}")

4. Use Lazy Formatting
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Good - formatting happens only if logged
   logger.debug("Data: %s", expensive_object)

   # Less efficient - always formats
   logger.debug(f"Data: {expensive_object}")

5. Batch Logging
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Collect messages, log once
   messages = []
   for item in items:
       messages.append(f"Processed {item}")

   logger.info("Batch result:\n" + "\n".join(messages))

6. Async Logging
~~~~~~~~~~~~~~~~

For high-throughput applications:

.. code-block:: python

   import logging
   from logging.handlers import QueueHandler, QueueListener
   import queue

   log_queue = queue.Queue(-1)

   # Main thread uses queue handler
   queue_handler = QueueHandler(log_queue)
   logger.addHandler(queue_handler)

   # Separate thread processes logs
   file_handler = logging.FileHandler('app.log')
   listener = QueueListener(log_queue, file_handler)
   listener.start()

   # Don't forget to stop
   # listener.stop()

7. Memory Handler for Buffering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from logging.handlers import MemoryHandler

   # Buffer 1000 records before flushing
   memory_handler = MemoryHandler(
       capacity=1000,
       flushLevel=logging.ERROR,
       target=file_handler
   )
   logger.addHandler(memory_handler)

Benchmarking
------------

Compare handler performance:

.. code-block:: python

   import time
   import logging
   from richcolorlog import setup_logging
   from richcolorlog.logger import AnsiLogHandler, RichColorLogHandler

   def benchmark(name, logger, iterations=10000):
       start = time.time()
       for i in range(iterations):
           logger.info(f"Test message {i}")
       elapsed = time.time() - start
       print(f"{name}: {elapsed:.3f}s ({iterations/elapsed:.0f} msg/s)")

   # Benchmark Rich handler
   logger1 = setup_logging(name='rich_bench')
   benchmark("Rich Handler", logger1)

   # Benchmark ANSI handler
   logger2 = setup_logging(name='ansi_bench', HANDLER=AnsiLogHandler)
   benchmark("ANSI Handler", logger2)

   # Benchmark with features disabled
   logger3 = setup_logging(
       name='minimal_bench',
       show_icon=False,
       show_path=False,
       HANDLER=AnsiLogHandler
   )
   benchmark("Minimal Handler", logger3)

Disabling Logging
-----------------

Completely disable logging for maximum performance:

.. code-block:: python

   import os

   # Via environment variable
   os.environ['NO_LOGGING'] = '1'

   # Or
   os.environ['LOGGING'] = '0'

   # Then import
   from richcolorlog import setup_logging
   logger = setup_logging()  # Returns disabled logger

Or programmatically:

.. code-block:: python

   import logging

   # Disable all logging
   logging.disable(logging.CRITICAL)

   # Re-enable
   logging.disable(logging.NOTSET)

Production Recommendations
--------------------------

.. code-block:: python

   import os

   is_production = os.getenv('ENV') == 'production'

   logger = setup_logging(
       name='myapp',
       level='INFO' if is_production else 'DEBUG',

       # Minimize console overhead in production
       show_icon=not is_production,
       show_background=not is_production,
       show_path=not is_production,

       # Use file logging in production
       log_file=True,
       log_file_name='/var/log/myapp/app.log',
       log_file_level='DEBUG',

       # Use async handlers for high throughput
       # (implement custom async handler)
   )

Memory Usage
------------

Monitor memory usage:

.. code-block:: python

   import tracemalloc

   tracemalloc.start()

   # Logging operations
   for i in range(10000):
       logger.info(f"Message {i}")

   current, peak = tracemalloc.get_traced_memory()
   print(f"Current: {current / 1024:.1f} KB")
   print(f"Peak: {peak / 1024:.1f} KB")

   tracemalloc.stop()