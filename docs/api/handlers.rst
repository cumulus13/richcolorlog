============
Handlers API
============

Handler classes for different output destinations.

RichColorLogHandler
-------------------

.. py:class:: RichColorLogHandler(RichHandler)

   Rich-based handler with table layout and syntax highlighting.

   :param lexer: Pygments lexer name.
   :type lexer: str, optional
   :param show_background: Enable background colors.
   :type show_background: bool
   :param render_emoji: Render emoji characters.
   :type render_emoji: bool
   :param show_icon: Show level icons.
   :type show_icon: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param theme: Pygments syntax theme.
   :type theme: str
   :param format_template: Custom format string.
   :type format_template: str, optional
   :param level_in_message: Include level in message.
   :type level_in_message: bool
   :param show_type: Show message type.
   :type show_type: bool

   Inherits all parameters from Rich's ``RichHandler``.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import RichColorLogHandler

      handler = RichColorLogHandler(
          show_background=True,
          show_icon=True,
          icon_first=True,
          theme='monokai',
      )

      logger = logging.getLogger('myapp')
      logger.addHandler(handler)

AnsiLogHandler
--------------

.. py:class:: AnsiLogHandler(logging.StreamHandler)

   ANSI escape code handler with icon support.

   :param lexer: Pygments lexer name.
   :type lexer: str, optional
   :param show_background: Enable background colors.
   :type show_background: bool
   :param format_template: Custom format string.
   :type format_template: str, optional
   :param show_time: Show timestamp.
   :type show_time: bool
   :param show_name: Show logger name.
   :type show_name: bool
   :param show_pid: Show process ID.
   :type show_pid: bool
   :param show_level: Show log level.
   :type show_level: bool
   :param show_path: Show file path.
   :type show_path: bool
   :param show_icon: Show level icons.
   :type show_icon: bool
   :param icon_first: Place icon before timestamp.
   :type icon_first: bool
   :param level_in_message: Include level in message.
   :type level_in_message: bool
   :param use_colors: Enable ANSI colors.
   :type use_colors: bool

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import AnsiLogHandler

      handler = AnsiLogHandler(
          show_background=True,
          show_icon=True,
          use_colors=True,
      )

RabbitMQHandler
---------------

.. py:class:: RabbitMQHandler(logging.Handler)

   Handler for sending logs to RabbitMQ.

   :param host: RabbitMQ server hostname.
   :type host: str
   :param port: RabbitMQ server port.
   :type port: int
   :param exchange: Exchange name.
   :type exchange: str
   :param username: Authentication username.
   :type username: str
   :param password: Authentication password.
   :type password: str
   :param vhost: Virtual host.
   :type vhost: str
   :param level: Minimum logging level.
   :type level: int

   .. py:method:: emit(record)

      Send log record to RabbitMQ with routing_key = level.

   .. py:method:: close()

      Close RabbitMQ connection.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import RabbitMQHandler

      handler = RabbitMQHandler(
          host='localhost',
          port=5672,
          exchange='app_logs',
          username='user',
          password='pass',
      )

KafkaHandler
------------

.. py:class:: KafkaHandler(logging.Handler)

   Handler for sending logs to Apache Kafka.

   :param host: Kafka broker hostname.
   :type host: str
   :param port: Kafka broker port.
   :type port: int
   :param topic: Topic name.
   :type topic: str
   :param use_level_in_topic: Append level to topic name.
   :type use_level_in_topic: bool
   :param level: Minimum logging level.
   :type level: int

   .. py:method:: emit(record)

      Send log record to Kafka.

   .. py:method:: close()

      Close Kafka producer.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import KafkaHandler

      handler = KafkaHandler(
          host='localhost',
          port=9092,
          topic='app_logs',
          use_level_in_topic=True,
      )

ZeroMQHandler
-------------

.. py:class:: ZeroMQHandler(logging.Handler)

   Handler for sending logs via ZeroMQ.

   :param host: ZeroMQ endpoint hostname.
   :type host: str
   :param port: ZeroMQ endpoint port.
   :type port: int
   :param socket_type: Socket type ('PUB' or 'PUSH').
   :type socket_type: str
   :param level: Minimum logging level.
   :type level: int

   .. py:method:: emit(record)

      Send log record via ZeroMQ.

   .. py:method:: close()

      Close ZeroMQ socket and context.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import ZeroMQHandler

      handler = ZeroMQHandler(
          host='localhost',
          port=5555,
          socket_type='PUB',
      )

SyslogHandler
-------------

.. py:class:: SyslogHandler(logging.handlers.SysLogHandler)

   Enhanced syslog handler with proper severity mapping.

   :param host: Syslog server hostname.
   :type host: str
   :param port: Syslog server port.
   :type port: int
   :param facility: Syslog facility code.
   :type facility: int
   :param level: Minimum logging level.
   :type level: int

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import SyslogHandler
      import logging.handlers

      handler = SyslogHandler(
          host='localhost',
          port=514,
          facility=logging.handlers.SysLogHandler.LOG_LOCAL0,
      )

DatabaseHandler
---------------

.. py:class:: DatabaseHandler(logging.Handler)

   Handler for storing logs in a database.

   :param db_type: Database type ('postgresql', 'mysql', 'mariadb', 'sqlite').
   :type db_type: str
   :param host: Database server hostname.
   :type host: str
   :param port: Database server port.
   :type port: int, optional
   :param database: Database name.
   :type database: str
   :param user: Database username.
   :type user: str
   :param password: Database password.
   :type password: str
   :param level: Minimum logging level.
   :type level: int

   .. py:method:: emit(record)

      Store log record in database.

   .. py:method:: close()

      Close database connection.

   **Example:**

   .. code-block:: python

      from richcolorlog.logger import DatabaseHandler

      handler = DatabaseHandler(
          db_type='postgresql',
          host='localhost',
          port=5432,
          database='logs',
          user='logger',
          password='password',
      )