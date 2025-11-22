================
Database Handler
================

Store log messages in PostgreSQL, MySQL/MariaDB, or SQLite databases.

Installation
------------

.. code-block:: bash

   # PostgreSQL
   pip install richcolorlog[postgresql]
   # or
   pip install psycopg2-binary

   # MySQL/MariaDB
   pip install richcolorlog[mysql]
   # or
   pip install mysql-connector-python

   # SQLite - included with Python

Basic Usage
-----------

.. code-block:: python

   from richcolorlog import setup_logging

   # PostgreSQL
   logger = setup_logging(
       db=True,
       db_type='postgresql',
       db_host='localhost',
       db_name='logs',
       db_user='postgres',
       db_password='password',
   )

   logger.info("This goes to the database!")

Configuration Parameters
------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Default
     - Description
   * - ``db``
     - ``False``
     - Enable database handler
   * - ``db_type``
     - ``'postgresql'``
     - Database type: postgresql, mysql, mariadb, sqlite
   * - ``db_host``
     - ``'localhost'``
     - Database server hostname
   * - ``db_port``
     - Auto
     - Database port (auto-detected by type)
   * - ``db_name``
     - ``'logs'``
     - Database name (or file path for SQLite)
   * - ``db_user``
     - ``'postgres'``
     - Database username
   * - ``db_password``
     - ``''``
     - Database password
   * - ``db_level``
     - ``DEBUG``
     - Minimum level for database

Database-Specific Examples
--------------------------

PostgreSQL
~~~~~~~~~~

.. code-block:: python

   logger = setup_logging(
       db=True,
       db_type='postgresql',
       db_host='localhost',
       db_port=5432,
       db_name='app_logs',
       db_user='logger',
       db_password='secure_password',
   )

MySQL
~~~~~

.. code-block:: python

   logger = setup_logging(
       db=True,
       db_type='mysql',
       db_host='localhost',
       db_port=3306,
       db_name='app_logs',
       db_user='logger',
       db_password='secure_password',
   )

MariaDB
~~~~~~~

.. code-block:: python

   logger = setup_logging(
       db=True,
       db_type='mariadb',
       db_host='localhost',
       db_port=3306,
       db_name='app_logs',
       db_user='logger',
       db_password='secure_password',
   )

SQLite
~~~~~~

.. code-block:: python

   logger = setup_logging(
       db=True,
       db_type='sqlite',
       db_name='logs.db',  # File path
   )

Table Schema
------------

Tables are created automatically for each log level:

.. code-block:: sql

   -- Created tables:
   -- log_emergency, log_alert, log_fatal, log_critical,
   -- log_error, log_warning, log_notice, log_info, log_debug
   -- log_syslog (combined)

   CREATE TABLE log_info (
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
   );

Level-Based Tables
------------------

Logs are stored in level-specific tables:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Level
     - Table Name
   * - EMERGENCY
     - ``log_emergency``
   * - ALERT
     - ``log_alert``
   * - FATAL
     - ``log_fatal``
   * - CRITICAL
     - ``log_critical``
   * - ERROR
     - ``log_error``
   * - WARNING
     - ``log_warning``
   * - NOTICE
     - ``log_notice``
   * - INFO
     - ``log_info``
   * - DEBUG
     - ``log_debug``

All logs also go to ``log_syslog`` for unified queries.

Querying Logs
-------------

.. code-block:: sql

   -- All errors from today
   SELECT * FROM log_error
   WHERE timestamp >= CURRENT_DATE
   ORDER BY timestamp DESC;

   -- All logs from a specific logger
   SELECT * FROM log_syslog
   WHERE logger = 'myapp.auth'
   ORDER BY timestamp DESC
   LIMIT 100;

   -- Count by level
   SELECT level, COUNT(*) as count
   FROM log_syslog
   WHERE timestamp >= NOW() - INTERVAL '1 hour'
   GROUP BY level;

   -- Search in messages
   SELECT * FROM log_syslog
   WHERE message LIKE '%user%'
   ORDER BY timestamp DESC;

Database Setup
--------------

PostgreSQL
~~~~~~~~~~

.. code-block:: sql

   -- Create database
   CREATE DATABASE app_logs;

   -- Create user
   CREATE USER logger WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE app_logs TO logger;

   -- Connect and grant schema permissions
   \c app_logs
   GRANT ALL ON SCHEMA public TO logger;
   GRANT ALL ON ALL TABLES IN SCHEMA public TO logger;
   GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO logger;

MySQL
~~~~~

.. code-block:: sql

   -- Create database
   CREATE DATABASE app_logs;

   -- Create user
   CREATE USER 'logger'@'%' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON app_logs.* TO 'logger'@'%';
   FLUSH PRIVILEGES;

Production Configuration
------------------------

.. code-block:: python

   logger = setup_logging(
       name='production_app',
       level='INFO',

       # Database - store warnings and above
       db=True,
       db_type='postgresql',
       db_host='db.example.com',
       db_port=5432,
       db_name='production_logs',
       db_user='logger',
       db_password='secure_password',
       db_level='WARNING',
   )

Connection Pooling
------------------

For high-volume logging, use connection pooling:

.. code-block:: python

   import logging
   from richcolorlog.logger import DatabaseHandler

   # Custom handler with pooling
   class PooledDatabaseHandler(DatabaseHandler):
       def __init__(self, pool, **kwargs):
           self.pool = pool
           super().__init__(**kwargs)

       def _connect(self):
           self.connection = self.pool.getconn()

       def close(self):
           self.pool.putconn(self.connection)

Indexing
--------

Add indexes for better query performance:

.. code-block:: sql

   -- Index for timestamp queries
   CREATE INDEX idx_log_syslog_timestamp
   ON log_syslog(timestamp);

   -- Index for logger queries
   CREATE INDEX idx_log_syslog_logger
   ON log_syslog(logger);

   -- Composite index
   CREATE INDEX idx_log_syslog_timestamp_level
   ON log_syslog(timestamp, level);

Cleanup/Retention
-----------------

Implement log retention:

.. code-block:: sql

   -- Delete logs older than 30 days
   DELETE FROM log_syslog
   WHERE timestamp < NOW() - INTERVAL '30 days';

   -- PostgreSQL: partitioning for large tables
   CREATE TABLE log_syslog_2025_01 PARTITION OF log_syslog
   FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

Direct Handler Usage
--------------------

.. code-block:: python

   import logging
   from richcolorlog.logger import DatabaseHandler

   handler = DatabaseHandler(
       db_type='postgresql',
       host='localhost',
       port=5432,
       database='logs',
       user='logger',
       password='password',
       level=logging.WARNING
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Cleanup
-------

.. code-block:: python

   # Manual cleanup
   for handler in logger.handlers:
       if isinstance(handler, DatabaseHandler):
           handler.close()

   # Or use logging shutdown
   logging.shutdown()