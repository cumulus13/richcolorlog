================
RabbitMQ Handler
================

Send log messages to RabbitMQ with routing keys based on log level.

Installation
------------

.. code-block:: bash

   pip install richcolorlog[rabbitmq]
   # or
   pip install pika

Basic Usage
-----------

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       rabbitmq=True,
       rabbitmq_host='localhost',
       rabbitmq_port=5672,
       rabbitmq_exchange='logs',
       rabbitmq_username='guest',
       rabbitmq_password='guest',
   )

   logger.info("This goes to RabbitMQ!")

Configuration Parameters
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Parameter
     - Default
     - Description
   * - ``rabbitmq``
     - ``False``
     - Enable RabbitMQ handler
   * - ``rabbitmq_host``
     - ``'localhost'``
     - RabbitMQ server hostname
   * - ``rabbitmq_port``
     - ``5672``
     - RabbitMQ server port
   * - ``rabbitmq_exchange``
     - ``'logs'``
     - Exchange name for publishing
   * - ``rabbitmq_username``
     - ``'guest'``
     - Authentication username
   * - ``rabbitmq_password``
     - ``'guest'``
     - Authentication password
   * - ``rabbitmq_vhost``
     - ``'/'``
     - Virtual host
   * - ``rabbitmq_level``
     - ``DEBUG``
     - Minimum level for RabbitMQ

Message Format
--------------

Messages are published as JSON:

.. code-block:: json

   {
     "timestamp": "2025-01-15T10:30:45.123456",
     "level": "INFO",
     "logger": "myapp",
     "message": "User logged in",
     "module": "auth",
     "funcName": "login",
     "lineno": 42,
     "pathname": "/app/auth.py",
     "process": 12345,
     "thread": 140123456789
   }

Routing Keys
------------

Messages are routed using the log level as routing key:

- ``debug`` → DEBUG messages
- ``info`` → INFO messages
- ``warning`` → WARNING messages
- ``error`` → ERROR messages
- ``critical`` → CRITICAL messages
- ``notice`` → NOTICE messages
- ``alert`` → ALERT messages
- ``emergency`` → EMERGENCY messages
- ``fatal`` → FATAL messages

Consumer Example
----------------

Consume logs from RabbitMQ:

.. code-block:: python

   import pika
   import json

   connection = pika.BlockingConnection(
       pika.ConnectionParameters('localhost')
   )
   channel = connection.channel()

   # Declare exchange
   channel.exchange_declare(
       exchange='logs',
       exchange_type='topic',
       durable=True
   )

   # Queue for all logs
   result = channel.queue_declare(queue='all_logs', exclusive=True)
   channel.queue_bind(
       exchange='logs',
       queue=result.method.queue,
       routing_key='#'  # All levels
   )

   # Queue for errors only
   channel.queue_declare(queue='error_logs')
   channel.queue_bind(
       exchange='logs',
       queue='error_logs',
       routing_key='error'
   )
   channel.queue_bind(
       exchange='logs',
       queue='error_logs',
       routing_key='critical'
   )

   def callback(ch, method, properties, body):
       log = json.loads(body)
       print(f"[{log['level']}] {log['message']}")

   channel.basic_consume(
       queue='all_logs',
       on_message_callback=callback,
       auto_ack=True
   )

   channel.start_consuming()

Exchange Configuration
----------------------

The handler creates a topic exchange:

.. code-block:: python

   channel.exchange_declare(
       exchange='logs',
       exchange_type='topic',
       durable=True
   )

You can consume with different routing patterns:

- ``#`` - All messages
- ``error`` - Only errors
- ``*.error`` - Error from any app
- ``myapp.*`` - All levels from myapp

Production Configuration
------------------------

.. code-block:: python

   logger = setup_logging(
       name='production_app',
       level='INFO',

       # RabbitMQ with credentials
       rabbitmq=True,
       rabbitmq_host='rabbitmq.example.com',
       rabbitmq_port=5672,
       rabbitmq_exchange='app_logs',
       rabbitmq_username='app_logger',
       rabbitmq_password='secure_password',
       rabbitmq_vhost='/production',
       rabbitmq_level='WARNING',  # Only warnings and above
   )

Error Handling
--------------

Connection failures are handled gracefully:

.. code-block:: python

   # If RabbitMQ is unavailable, logs still go to console
   # Error message is logged via standard logging

   logger = setup_logging(
       rabbitmq=True,
       rabbitmq_host='unavailable-host',
   )

   # This still works (console output)
   logger.info("Message logged to console")

Direct Handler Usage
--------------------

Use the handler directly for more control:

.. code-block:: python

   import logging
   from richcolorlog.logger import RabbitMQHandler

   handler = RabbitMQHandler(
       host='localhost',
       port=5672,
       exchange='custom_logs',
       username='user',
       password='pass',
       vhost='/custom',
       level=logging.WARNING
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Cleanup
-------

The handler closes connections properly:

.. code-block:: python

   # Manual cleanup
   for handler in logger.handlers:
       if isinstance(handler, RabbitMQHandler):
           handler.close()

   # Or use logging shutdown
   logging.shutdown()