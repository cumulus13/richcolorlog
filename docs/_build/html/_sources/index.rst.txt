.. richcolorlog documentation master file

====================================
RichColorLog Documentation
====================================

.. image:: _static/screenshot.png
   :alt: RichColorLog Screenshot
   :align: center
   :width: 100%

|

**RichColorLog** is an enhanced Python logging library with Rich formatting, 
custom log levels, and support for multiple output backends including Console, 
File, RabbitMQ, Kafka, ZeroMQ, Syslog, and Database.

.. note::
   This library extends Python's standard logging module with colorful output,
   emoji icons, syntax highlighting, and enterprise-grade logging backends.

Features
--------

✨ **Rich Console Output**
   Beautiful, colorful log messages with customizable themes

🎨 **Multiple Color Modes**
   Automatic detection of terminal color support (TrueColor, 256-color, Basic, None)

📊 **Custom Log Levels**
   Extended syslog-compatible levels: EMERGENCY, ALERT, FATAL, NOTICE

🔌 **Multiple Backends**
   Console, File, RabbitMQ, Kafka, ZeroMQ, Syslog, Database

💡 **Syntax Highlighting**
   Code highlighting in log messages using Pygments

🎯 **Icon Support**
   Emoji icons for different log levels

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install richcolorlog

   # With optional dependencies
   pip install richcolorlog[rabbitmq]  # RabbitMQ support
   pip install richcolorlog[kafka]     # Kafka support
   pip install richcolorlog[zeromq]    # ZeroMQ support
   pip install richcolorlog[database]  # Database support
   pip install richcolorlog[all]       # All backends

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from richcolorlog import setup_logging

   # Simple setup
   logger = setup_logging()

   logger.debug("Debug message")
   logger.info("Info message")
   logger.warning("Warning message")
   logger.error("Error message")
   logger.critical("Critical message")

   # Custom levels
   logger.notice("Notice message")
   logger.alert("Alert message")
   logger.emergency("Emergency message")
   logger.fatal("Fatal message")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   configuration
   custom_levels
   color_modes

.. toctree::
   :maxdepth: 2
   :caption: Handlers

   handlers/console
   handlers/file
   handlers/rabbitmq
   handlers/kafka
   handlers/zeromq
   handlers/syslog
   handlers/database

.. toctree::
   :maxdepth: 2
   :caption: Advanced

   advanced/formatters
   advanced/filters
   advanced/syntax_highlighting
   advanced/performance

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/logger
   api/handlers
   api/formatters
   api/colors
   api/utilities

.. toctree::
   :maxdepth: 1
   :caption: Development

   changelog
   contributing
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
-----

* **Source Code**: `GitHub <https://github.com/cumulus13/richcolorlog>`_
* **Issue Tracker**: `GitHub Issues <https://github.com/cumulus13/richcolorlog/issues>`_
* **Author**: Hadi Cahyadi <cumulus13@gmail.com>