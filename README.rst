.. start-no-pypi

.. image:: https://travis-ci.org/mvantellingen/django-aws-xray.svg?branch=master
    :target: https://travis-ci.org/mvantellingen/django-aws-xray

.. image:: http://codecov.io/github/mvantellingen/django-aws-xray/coverage.svg?branch=master
    :target: http://codecov.io/github/mvantellingen/django-aws-xray?branch=master

.. image:: https://img.shields.io/pypi/v/django-aws-xray.svg
    :target: https://pypi.python.org/pypi/django-aws-xray/

.. end-no-pypi

===============
django-aws-xray
===============

Leverage AWS X-Ray for your Django projects! This Django app instruments your code
to send traces to the `X-Ray daemon`_.

.. _`X-Ray daemon`: http://docs.aws.amazon.com/xray/latest/devguide/xray-daemon.html


Installation
============

.. code-block:: shell

   pip install django-aws-xray



Update your Django settings:

.. code-block:: python


    INSTALLED_APPS += [
        'django_aws_xray'
    ]

    MIDDLEWARE.insert(0, 'django_aws_xray.middleware.XRayMiddleware')

    # Enable various instrumentation monkeypatches
    AWS_XRAY_PATCHES = [
        'django_aws_xray.patches.cache',
        'django_aws_xray.patches.redis',
        'django_aws_xray.patches.db',
        'django_aws_xray.patches.requests',
        'django_aws_xray.patches.templates',
    ]


Settings
========

=========================   =====================  ==========
Setting                     Name                   Default
=========================   =====================  ==========
`AWS_XRAY_SAMPLING_RATE`    Sampling rate          100
`AWS_XRAY_EXCLUDED_PATHS`   Exclude paths          `[]`
`AWS_XRAY_HOST`             IP of X-Ray Daemon     127.0.0.1
`AWS_XRAY_PORT`             Port of X-Ray Daemon   2000
`AWS_XRAY_PATCHES`          Patches                ``[]``
=========================   =====================  ==========


Credits
=======
The database and cache instrumention code was based on the code from django-statsd
