============
Installation
============

Requirements
------------

* Python 3.7 or higher
* ``rich`` library (optional but recommended for best experience)
* ``pygments`` library (optional, for syntax highlighting)

Basic Installation
------------------

Install from PyPI:

.. code-block:: bash

   pip install richcolorlog

Install from source:

.. code-block:: bash

   git clone https://github.com/cumulus13/richcolorlog.git
   cd richcolorlog
   pip install -e .

Optional Dependencies
---------------------

RichColorLog supports various message brokers and databases. Install the extras you need:

RabbitMQ Support
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install richcolorlog[rabbitmq]

This installs ``pika`` for RabbitMQ connectivity.

Kafka Support
~~~~~~~~~~~~~

.. code-block:: bash

   pip install richcolorlog[kafka]

This installs ``kafka-python`` for Apache Kafka connectivity.

ZeroMQ Support
~~~~~~~~~~~~~~

.. code-block:: bash

   pip install richcolorlog[zeromq]

This installs ``pyzmq`` for ZeroMQ messaging.

Database Support
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # PostgreSQL
   pip install richcolorlog[postgresql]

   # MySQL/MariaDB
   pip install richcolorlog[mysql]

   # All databases
   pip install richcolorlog[database]

All Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install richcolorlog[all]

Verifying Installation
----------------------

.. code-block:: python

   >>> import richcolorlog
   >>> from richcolorlog import setup_logging
   >>> logger = setup_logging()
   >>> logger.info("RichColorLog is working!")

You should see a colorful log message in your terminal.

Development Installation
------------------------

For development, clone the repository and install in editable mode with dev dependencies:

.. code-block:: bash

   git clone https://github.com/cumulus13/richcolorlog.git
   cd richcolorlog
   pip install -e ".[dev]"

This includes testing and documentation tools.