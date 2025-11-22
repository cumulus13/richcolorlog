============
Contributing
============

Thank you for considering contributing to RichColorLog!

Getting Started
---------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/richcolorlog.git
      cd richcolorlog

3. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      venv\Scripts\activate     # Windows

4. Install development dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

Development Setup
-----------------

Install all optional dependencies for full testing:

.. code-block:: bash

   pip install -e ".[all,dev]"

This includes:

* ``rich`` - Rich library
* ``pygments`` - Syntax highlighting
* ``pika`` - RabbitMQ
* ``kafka-python`` - Kafka
* ``pyzmq`` - ZeroMQ
* ``psycopg2-binary`` - PostgreSQL
* ``mysql-connector-python`` - MySQL
* ``pytest`` - Testing
* ``sphinx`` - Documentation

Running Tests
-------------

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=richcolorlog

   # Run specific test
   pytest tests/test_logger.py -v

   # Run the built-in test
   python -c "from richcolorlog import test; test()"

Code Style
----------

We use the following style guidelines:

* **PEP 8** for Python code style
* **Black** for code formatting (optional)
* **Type hints** where practical
* **Docstrings** for public APIs

.. code-block:: bash

   # Format code (optional)
   black richcolorlog/

   # Check style
   flake8 richcolorlog/

Making Changes
--------------

1. Create a branch for your changes:

   .. code-block:: bash

      git checkout -b feature/my-new-feature

2. Make your changes and add tests

3. Run the tests to ensure nothing is broken:

   .. code-block:: bash

      pytest

4. Commit your changes:

   .. code-block:: bash

      git add .
      git commit -m "Add: description of changes"

5. Push to your fork:

   .. code-block:: bash

      git push origin feature/my-new-feature

6. Create a Pull Request on GitHub

Commit Messages
---------------

Use clear, descriptive commit messages:

* ``Add:`` New features
* ``Fix:`` Bug fixes
* ``Update:`` Changes to existing functionality
* ``Docs:`` Documentation changes
* ``Test:`` Test additions/changes
* ``Refactor:`` Code refactoring

Example:

.. code-block:: text

   Add: Support for Redis handler

   - Implement RedisHandler class
   - Add configuration parameters to setup_logging
   - Add tests for Redis functionality
   - Update documentation

Pull Request Guidelines
-----------------------

* Include tests for new functionality
* Update documentation for API changes
* Keep changes focused and atomic
* Write clear PR descriptions
* Reference related issues

Reporting Issues
----------------

When reporting issues, please include:

* Python version
* Operating system
* RichColorLog version
* Minimal code to reproduce the issue
* Full traceback if applicable

Example issue report:

.. code-block:: text

   **Environment:**
   - Python: 3.11.0
   - OS: Ubuntu 22.04
   - RichColorLog: 1.0.0

   **Description:**
   The logger crashes when using the RabbitMQ handler with...

   **Code to reproduce:**
   ```python
   from richcolorlog import setup_logging
   logger = setup_logging(rabbitmq=True, ...)
   ```

   **Traceback:**
   ```
   Traceback (most recent call last):
   ...
   ```

Documentation
-------------

Build documentation locally:

.. code-block:: bash

   cd docs
   pip install -r requirements.txt
   make html

   # View in browser
   open _build/html/index.html  # macOS
   xdg-open _build/html/index.html  # Linux

Adding New Features
-------------------

When adding new features:

1. Discuss in an issue first for major changes
2. Add type hints to function signatures
3. Add docstrings following Google style
4. Add tests with good coverage
5. Update relevant documentation
6. Add changelog entry

Example new handler:

.. code-block:: python

   class MyNewHandler(logging.Handler):
       """
       Handler for sending logs to MyService.

       Args:
           host: Service hostname.
           port: Service port.
           level: Minimum logging level.

       Example:
           >>> handler = MyNewHandler(host='localhost', port=9999)
           >>> logger.addHandler(handler)
       """

       def __init__(self, host='localhost', port=9999, level=logging.DEBUG):
           super().__init__(level)
           self.host = host
           self.port = port
           self._connect()

       def _connect(self):
           """Establish connection to service."""
           pass

       def emit(self, record):
           """Send log record to service."""
           pass

       def close(self):
           """Close connection."""
           pass

Code of Conduct
---------------

* Be respectful and inclusive
* Focus on constructive feedback
* Help others learn and grow
* Keep discussions professional

Questions?
----------

* Open an issue on GitHub
* Email: cumulus13@gmail.com

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.