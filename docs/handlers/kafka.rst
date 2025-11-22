=============
Kafka Handler
=============

Send log messages to Apache Kafka for distributed log aggregation.

Installation
------------

.. code-block:: bash

   pip install richcolorlog[kafka]
   # or
   pip install kafka-python

Basic Usage
-----------

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       kafka=True,
       kafka_host='localhost',
       kafka_port=9092,
       kafka_topic='logs',
   )

   logger.info("This goes to Kafka!")

Configuration Parameters
------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Default
     - Description
   * - ``kafka``
     - ``False``
     - Enable Kafka handler
   * - ``kafka_host``
     - ``'localhost'``
     - Kafka broker hostname
   * - ``kafka_port``
     - ``9092``
     - Kafka broker port
   * - ``kafka_topic``
     - ``'logs'``
     - Topic name for publishing
   * - ``kafka_use_level_in_topic``
     - ``False``
     - Append level to topic name
   * - ``kafka_level``
     - ``DEBUG``
     - Minimum level for Kafka

Topic Naming
------------

Single Topic
~~~~~~~~~~~~

All logs go to one topic:

.. code-block:: python

   logger = setup_logging(
       kafka=True,
       kafka_topic='app_logs',
       kafka_use_level_in_topic=False,
   )

   # All messages → 'app_logs' topic

Level-Based Topics
~~~~~~~~~~~~~~~~~~

Separate topics per log level:

.. code-block:: python

   logger = setup_logging(
       kafka=True,
       kafka_topic='app_logs',
       kafka_use_level_in_topic=True,
   )

   logger.debug("msg")    # → 'app_logs.debug'
   logger.info("msg")     # → 'app_logs.info'
   logger.error("msg")    # → 'app_logs.error'

Message Format
--------------

Messages are JSON-serialized:

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

The message key is set to the log level (e.g., ``info``, ``error``).

Consumer Example
----------------

Consume logs with kafka-python:

.. code-block:: python

   from kafka import KafkaConsumer
   import json

   consumer = KafkaConsumer(
       'app_logs',
       bootstrap_servers=['localhost:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       auto_offset_reset='latest',
       group_id='log_consumers'
   )

   for message in consumer:
       log = message.value
       print(f"[{log['level']}] {log['logger']}: {log['message']}")

Multi-Broker Setup
------------------

For production Kafka clusters:

.. code-block:: python

   from richcolorlog.logger import KafkaHandler
   import logging

   # Multiple brokers
   handler = KafkaHandler.__init__
   # Note: Current implementation supports single host
   # For multiple brokers, use direct kafka-python setup

   from kafka import KafkaProducer

   class MultiKafkaHandler(logging.Handler):
       def __init__(self, brokers, topic):
           super().__init__()
           self.producer = KafkaProducer(
               bootstrap_servers=brokers,
               value_serializer=lambda v: json.dumps(v).encode('utf-8')
           )
           self.topic = topic

       def emit(self, record):
           # ... emit logic

Production Configuration
------------------------

.. code-block:: python

   logger = setup_logging(
       name='production_app',
       level='INFO',

       kafka=True,
       kafka_host='kafka.example.com',
       kafka_port=9092,
       kafka_topic='production.logs',
       kafka_use_level_in_topic=True,
       kafka_level='INFO',
   )

Integration with ELK Stack
--------------------------

Kafka is commonly used with Elasticsearch, Logstash, and Kibana:

.. code-block:: text

   Application → Kafka → Logstash → Elasticsearch → Kibana
                    ↓
                Consumer (alerting)

Logstash configuration:

.. code-block:: ruby

   input {
     kafka {
       bootstrap_servers => "kafka:9092"
       topics => ["app_logs"]
       codec => json
     }
   }

   output {
     elasticsearch {
       hosts => ["elasticsearch:9200"]
       index => "app-logs-%{+YYYY.MM.dd}"
     }
   }

Direct Handler Usage
--------------------

.. code-block:: python

   import logging
   from richcolorlog.logger import KafkaHandler

   handler = KafkaHandler(
       host='localhost',
       port=9092,
       topic='custom_logs',
       use_level_in_topic=True,
       level=logging.WARNING
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Cleanup
-------

.. code-block:: python

   # Manual cleanup
   for handler in logger.handlers:
       if isinstance(handler, KafkaHandler):
           handler.close()

   # Or use logging shutdown
   logging.shutdown()