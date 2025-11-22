==============
ZeroMQ Handler
==============

Send log messages via ZeroMQ for high-performance, low-latency log distribution.

Installation
------------

.. code-block:: bash

   pip install richcolorlog[zeromq]
   # or
   pip install pyzmq

Basic Usage
-----------

.. code-block:: python

   from richcolorlog import setup_logging

   logger = setup_logging(
       zeromq=True,
       zeromq_host='localhost',
       zeromq_port=5555,
   )

   logger.info("This goes via ZeroMQ!")

Configuration Parameters
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Parameter
     - Default
     - Description
   * - ``zeromq``
     - ``False``
     - Enable ZeroMQ handler
   * - ``zeromq_host``
     - ``'localhost'``
     - ZeroMQ endpoint hostname
   * - ``zeromq_port``
     - ``5555``
     - ZeroMQ endpoint port
   * - ``zeromq_socket_type``
     - ``'PUB'``
     - Socket type: 'PUB' or 'PUSH'
   * - ``zeromq_level``
     - ``DEBUG``
     - Minimum level for ZeroMQ

Socket Types
------------

PUB Socket (Default)
~~~~~~~~~~~~~~~~~~~~

Publish-subscribe pattern. Logger binds, subscribers connect:

.. code-block:: python

   # Logger (Publisher)
   logger = setup_logging(
       zeromq=True,
       zeromq_socket_type='PUB',
       zeromq_port=5555,
   )

PUSH Socket
~~~~~~~~~~~

Pipeline pattern. Logger connects to a collector:

.. code-block:: python

   # Logger (Pusher)
   logger = setup_logging(
       zeromq=True,
       zeromq_socket_type='PUSH',
       zeromq_host='collector.example.com',
       zeromq_port=5555,
   )

Message Format
--------------

Messages are sent as space-separated topic and JSON:

.. code-block:: text

   info {"timestamp": "2025-01-15T10:30:45.123456", "level": "INFO", ...}

The topic is the lowercase log level.

Subscriber Example
------------------

PUB/SUB Pattern
~~~~~~~~~~~~~~~

.. code-block:: python

   import zmq
   import json

   context = zmq.Context()
   socket = context.socket(zmq.SUB)
   socket.connect("tcp://localhost:5555")

   # Subscribe to all messages
   socket.setsockopt_string(zmq.SUBSCRIBE, "")

   # Or subscribe to specific levels
   socket.setsockopt_string(zmq.SUBSCRIBE, "error")
   socket.setsockopt_string(zmq.SUBSCRIBE, "critical")

   while True:
       message = socket.recv_string()
       topic, json_data = message.split(" ", 1)
       log = json.loads(json_data)
       print(f"[{log['level']}] {log['message']}")

PUSH/PULL Pattern
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import zmq
   import json

   context = zmq.Context()
   socket = context.socket(zmq.PULL)
   socket.bind("tcp://*:5555")  # Collector binds

   while True:
       message = socket.recv_string()
       topic, json_data = message.split(" ", 1)
       log = json.loads(json_data)
       print(f"[{log['level']}] {log['message']}")

Multi-Subscriber Architecture
-----------------------------

.. code-block:: text

   App1 (PUB:5555) ──┐
                     │
   App2 (PUB:5556) ──┼──► Collector (SUB) ──► Database
                     │
   App3 (PUB:5557) ──┘

Proxy/Forwarder
---------------

For many-to-many routing:

.. code-block:: python

   import zmq

   context = zmq.Context()

   # Frontend: receive from publishers
   frontend = context.socket(zmq.XSUB)
   frontend.bind("tcp://*:5555")

   # Backend: send to subscribers
   backend = context.socket(zmq.XPUB)
   backend.bind("tcp://*:5556")

   # Start proxy
   zmq.proxy(frontend, backend)

Applications connect to 5555, subscribers to 5556.

Production Configuration
------------------------

.. code-block:: python

   logger = setup_logging(
       name='production_app',
       level='INFO',

       zeromq=True,
       zeromq_host='0.0.0.0',    # Bind to all interfaces
       zeromq_port=5555,
       zeromq_socket_type='PUB',
       zeromq_level='INFO',
   )

Performance Considerations
--------------------------

ZeroMQ is designed for high-throughput:

- Non-blocking sends
- In-memory queuing
- No broker overhead (peer-to-peer)

For extremely high volumes:

.. code-block:: python

   import zmq

   # Set high water mark to prevent memory issues
   socket.setsockopt(zmq.SNDHWM, 10000)

   # Set linger to avoid hanging on close
   socket.setsockopt(zmq.LINGER, 0)

Direct Handler Usage
--------------------

.. code-block:: python

   import logging
   from richcolorlog.logger import ZeroMQHandler

   handler = ZeroMQHandler(
       host='localhost',
       port=5555,
       socket_type='PUB',
       level=logging.WARNING
   )

   logger = logging.getLogger('myapp')
   logger.addHandler(handler)

Cleanup
-------

.. code-block:: python

   # Manual cleanup
   for handler in logger.handlers:
       if isinstance(handler, ZeroMQHandler):
           handler.close()

   # Or use logging shutdown
   logging.shutdown()