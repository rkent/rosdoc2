{{ root_title }}
{{ root_title_underline }}

{{ package_description }}

.. only:: url_any

   Links
   -----
   {{ url_repository }}
   {{ url_website }}
   {{ url_bugtracker }}

{% if has_user_docs -%}
Project Documentation
---------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *

{%- endif -%}
Package API
-----------

.. toctree::
   :maxdepth: 2
   {{ package_toc_entry }}

Indices and Search
==================

* :ref:`genindex`
* :ref:`search`
