==============
Syslog Handler
==============

Send log messages to syslog with proper RFC 5424 severity mapping.

Basic Usage
-----------

No additional installation required - uses Python's built-in syslog support.

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       syslog=True,
       syslog_host='localhost',
       syslog_port=514,
   )

   logger.info("This goes to syslog!")

Configuration Parameters
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Parameter
     - Default
     - Description
   * - ``syslog``
     - ``False``
     - Enable syslog handler
   * - ``syslog_host``
     - ``'localhost'``
     - Syslog server hostname
   * - ``syslog_port``
     - ``514``
     - Syslog server port
   * - ``syslog_facility``
     - ``LOG_USER``
     - Syslog facility code
   * - ``syslog_level``
     - ``DEBUG``
     - Minimum level for syslog

Severity Mapping
----------------

RichColorLog maps levels to RFC 5424 severities:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - RichColorLog Level
     - Severity
     - Description
   * - EMERGENCY (60)
     - 0
     - System is unusable
   * - ALERT (59)
     - 1
     - Action must be taken immediately
   * - FATAL (55)
     - 1
     - Fatal error (maps to Alert)
   * - CRITICAL (58, 50)
     - 2
     - Critical conditions
   * - ERROR (40)
     - 3
     - Error conditions
   * - WARNING (30)
     - 4
     - Warning conditions
   * - NOTICE (25)
     - 5
     - Normal but significant
   * - INFO (20)
     - 6
     - Informational messages
   * - DEBUG (10)
     - 7
     - Debug-level messages

Syslog Facilities
-----------------

Common facilities:

.. code-block:: python

   import logging.handlers as handlers

   logger = setup_logging(
       syslog=True,
       syslog_facility=handlers.SysLogHandler.LOG_USER,      # Default
   )

   # Other facilities
   handlers.SysLogHandler.LOG_LOCAL0  # Local use 0
   handlers.SysLogHandler.LOG_LOCAL1  # Local use 1
   handlers.SysLogHandler.LOG_LOCAL2  # Local use 2
   handlers.SysLogHandler.LOG_LOCAL3  # Local use 3
   handlers.SysLogHandler.LOG_LOCAL4  # Local use 4
   handlers.SysLogHandler.LOG_LOCAL5  # Local use 5
   handlers.SysLogHandler.LOG_LOCAL6  # Local use 6
   handlers.SysLogHandler.LOG_LOCAL7  # Local use 7
   handlers.SysLogHandler.LOG_DAEMON  # System daemons
   handlers.SysLogHandler.LOG_AUTH    # Security/auth

Message Format
--------------

Default format:

.. code-block:: text

   myapp[12345]: INFO - User logged in

Customize with formatter:

.. code-block:: python

   import logging
   from richcolorlog import setup_logging

   logger = setup_logging(syslog=True)

   # Find and update syslog handler
   for handler in logger.handlers:
       if isinstance(handler, logging.handlers.SysLogHandler):
           handler.setFormatter(logging.Formatter(
               '%(name)s: %(levelname)s %(message)s'
           ))

Local Syslog (Unix Socket)
--------------------------

For local syslog on Unix systems:

.. code-block:: python

   import logging.handlers

   # Use Unix socket instead of network
   handler = logging.handlers.SysLogHandler(
       address='/dev/log',  # Linux
       # address='/var/run/syslog',  # macOS
       facility=logging.handlers.SysLogHandler.LOG_USER
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Remote Syslog Server
--------------------

Send to a remote syslog server:

.. code-block:: python

   logger = setup_logging(
       syslog=True,
       syslog_host='syslog.example.com',
       syslog_port=514,
   )

For TLS-encrypted syslog, use a dedicated library like ``syslog-rfc5424-formatter``.

rsyslog Configuration
---------------------

Configure rsyslog to receive logs:

.. code-block:: text

   # /etc/rsyslog.conf

   # Enable UDP
   module(load="imudp")
   input(type="imudp" port="514")

   # Route by facility
   local0.*    /var/log/myapp.log

systemd-journald
----------------

On systemd systems, logs can go to journald:

.. code-block:: python

   import logging
   from systemd.journal import JournalHandler

   logger = logging.getLogger('myapp')
   logger.addHandler(JournalHandler())

   # Works with richcolorlog too
   from richcolorlog import setup_logging
   logger = setup_logging()
   logger.addHandler(JournalHandler())

Production Configuration
------------------------

.. code-block:: python

   import logging.handlers

   logger = setup_logging(
       name='production_app',
       level='INFO',

       syslog=True,
       syslog_host='syslog.example.com',
       syslog_port=514,
       syslog_facility=logging.handlers.SysLogHandler.LOG_LOCAL0,
       syslog_level='WARNING',  # Only warnings and above to syslog
   )

Viewing Syslog
--------------

.. code-block:: bash

   # Linux
   tail -f /var/log/syslog
   journalctl -f

   # macOS
   log stream --predicate 'process == "python"'

   # Filter by facility
   tail -f /var/log/local0.log

Direct Handler Usage
--------------------

.. code-block:: python

   import logging
   from richcolorlog.logger import SyslogHandler

   handler = SyslogHandler(
       host='localhost',
       port=514,
       facility=logging.handlers.SysLogHandler.LOG_LOCAL0,
       level=logging.WARNING
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)