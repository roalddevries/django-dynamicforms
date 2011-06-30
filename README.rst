.. |...| unicode:: U+2026   .. ellipsis

===================
django-dynamicforms
===================

Dynamically add forms to your site through the admin interface.

With django-dynamicforms you can:

- add forms through the admin interface
- add (custom) form fields through the admin interface
- reuse form fields in different forms
- customize predefined forms through the admin interface
- send personalized e-mails to submitters of dynamicforms
- download data posted to forms as CSV

Install
=======

- ``pip install django-dynamicforms``
- add ``'dynamicforms'`` to your ``INSTALLED_APPS``
- add ``(r'^dynamicforms/', include('dynamicforms.urls'))`` to your ``urls.py``

Dependencies
============

``django 1.3``
``html2text``

Settings
========

There are two optional settings: ``DYNAMICFORM_TYPES`` and ``DYNAMICFIELD_TYPES``, which define custom form and field types respectively. For example::

    DYNAMICFORM_TYPES = {
        'newsletter-subscription': {
            'VERBOSE_NAME':   'Newsletter subscription',
            'BASE_FORM':      'newsletters.forms.SubscriptionForm',
            'SUCCESS_URL':    '/newsletter/thanks/',
            'TEMPLATE':       'dynamicforms/form.html',
            'TAG_TEMPLATE':   'dynamicforms/_form.html',
            'EMAIL_TEMPLATE': 'dynamicforms/notification.html',
        },
    }

    DYNAMICFIELD_TYPES = {
        'phone': {
            'VERBOSE_NAME': 'Phone number',
            'FIELD':        'phone.forms.PhoneField',
            'HAS_CHOICES':  False,
            'DEFAULT':      '',
            'WIDGET':       'django.forms.TextInput'
        },
    }

Response e-mails are sent from ``settings.DEFAULT_FROM_EMAIL``.
Notification e-mails are sent from ``settings.SERVER_EMAIL``.

Usage
=====

Template tag
------------

Every form has its own page, but can also be included in other pages with::

    {% load dynamicform_tags %}
    ...
    {% show_dynamicform %}

It will always post to its own url, though, and validation errors will have to be corrected there.

Templates
---------

The templates used to render dynamicforms can be overridden by custom form types, but default to:
- ``dynamicforms/form.html`` for the form url
- ``dynamicforms/_form.html`` for the template tag
- ``dynamicforms/notification.eml`` for the notification e-mail

Wishlist
========

- adapt labels/help_text/|...| of (predefined) base form fields
- nicer report of data
- optional integration with messages framework
- dynamicformwizard
- better/more tests

.. vim: ft=rst
