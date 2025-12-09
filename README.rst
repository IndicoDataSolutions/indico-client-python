indicoio-py
===============

A wrapper for the `indico API <http://indico.io>`__.

The indico API is free to use, and no training data is required.

Installation
------------

From PyPI:

.. code:: bash

    pip install indico-client

From source:

Using UV (recommended):

.. code:: bash

    curl -LsSf https://astral.sh/uv/install.sh | sh
    git clone https://github.com/IndicoDataSolutions/indico-client-python.git
    cd indico-client-python
    uv pip install -e ".[all]"

Or using pip:

.. code:: bash

    git clone https://github.com/IndicoDataSolutions/indico-client-python.git
    cd indico-client-python
    pip install -e ".[all]"
