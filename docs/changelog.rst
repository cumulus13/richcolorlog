=========
Changelog
=========

All notable changes to RichColorLog will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[Unreleased]
------------

[1.0.0] - 2025-10-02
--------------------

Added
~~~~~

* Initial release of RichColorLog
* Rich-based console handler with table layout
* ANSI-based console handler for simpler output
* Custom log levels: NOTICE, ALERT, EMERGENCY, FATAL
* Emoji icons for all log levels
* Automatic terminal color detection (TrueColor, 256-color, Basic, None)
* Syntax highlighting for code in log messages
* File logging with level-based formatting
* RabbitMQ handler with topic routing
* Kafka handler with optional level-based topics
* ZeroMQ handler (PUB/PUSH patterns)
* Syslog handler with RFC 5424 severity mapping
* Database handler (PostgreSQL, MySQL, MariaDB, SQLite)
* Custom color configuration
* Format templates support
* Performance monitoring
* IPython/Jupyter compatibility mode
* Windows ANSI support

Documentation
~~~~~~~~~~~~~

* Complete Sphinx documentation
* ReadTheDocs integration
* API reference
* Handler guides
* Configuration examples

[0.9.0] - 2025-09-15
--------------------

Added
~~~~~

* Beta release for testing
* Core logging functionality
* Rich handler implementation
* Basic color support

Fixed
~~~~~

* Icon display issues on Windows
* Color detection in non-TTY environments

[0.8.0] - 2025-09-01
--------------------

Added
~~~~~

* Alpha release
* Initial implementation of custom levels
* ANSI color support

Known Issues
------------

* ZeroMQ handler currently supports single endpoint only
* Kafka handler supports single broker only
* Database handler doesn't support connection pooling (use external pool)

Roadmap
-------

Future releases may include:

* Async logging handlers
* Multi-broker Kafka support
* Connection pooling for database handler
* Elasticsearch handler
* Cloud logging integrations (AWS CloudWatch, GCP Logging, Azure Monitor)
* Log aggregation utilities
* Structured logging format (JSON Lines)
* OpenTelemetry integration