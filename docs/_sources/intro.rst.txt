Getting Started
***************

Installation
============

Requires python 3.6 or above.

To install the Python Client Library::

    pip install indico-client

To upgrade the Python Client Library::

    pip install --upgrade indico-client

Afterwards, proper installation can be verified with the following in a python shell::

    import indico
    print(indico.__version__)

Authentication
==============

The Indico Platform and Client Libraries use JSON Web Tokens (JWT) for user authentication. You can
download a token from your `user dashboard`_ by clicking the large, blue "Download new API Token" button.
Most browsers will download the API token as ``indico_api_token.txt`` and place it in your Downloads directory. You
should move the token file from Downloads to either your home directory or another location in your development
environment.

Configuration
=============

Environment Variables
---------------------

You can use environment variables to control the default configuration of the Python Client Library as follows:

.. csv-table::
    :file: env-vars.csv
    :widths: 25 60
    :header-rows: 1

IndicoConfig Class
------------------

The IndicoConfig class gives you the maximum control over Python Client Library configuration. Here's how you
might instantiate an IndicoConfig object and set the host and token path::

    from indico import IndicoClient, IndicoConfig

    my_config = IndicoConfig(
        host='app.mycompany.com',
        api_token_path='path/to/indico_api_token.txt'
    )


API Client
==========

The Indico Platform uses GraphQL to communicate with ALL clients including the company's own web application
and also the Indico Python Client. You'll use an ``IndicoClient`` object to pass GraphQL queries to the
Indico Platform. Here's a simple way to create a client::

    client = IndicoClient()

The IndicoClient constructor will read configuation options from the environment variables described above.
If you would like to manually set configuration options in an ``IndicoConfig`` object then you can pass your
config to IndicoClient as follows::

    client = IndicoClient(config=my_config)

If you want to learn more about GraphQL, the `How to GraphQL`_ tutorial is a great place to start.


Indico GraphQL Schema
======================

The Indico Platform ships with a built-in sandbox environment that both documents and allows you to
interactively explore the Platform's GraphQL schema. You can find the sandbox at ``/graph/api/graphql``
on your Indico Platform installation. If your Platform's host is ``indico.my_company.com`` then the full
sandbox URL would be ``https://indico.my_company.com/graph/api/graphql``


Pre-Built GraphQL queries
=========================

GraphQL is extremely powerful, flexible and efficient but can be a bit verbose. To make things easier
for day-to-day use of the Platform and Client Library, the developers at Indico created a collection of
Python Classes to generate the most often used queries for you. You can find the collection documented
in the Reference section of the Client Libreary Docs.


.. _user dashboard: https://app.indico.io/auth/user
.. _How to GraphQL: https://www.howtographql.com/
