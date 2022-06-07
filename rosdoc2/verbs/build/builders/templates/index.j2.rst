{{ root_title }}
{{ root_title_underline }}

{{ package_description }}

.. only:: url_any

   Links
   -----
   {% if url_repository %}{{ url_repository }}{% endif %}
   {% if url_website %}{{ url_website }}{% endif %}
   {% if url_bugtracker %}{{ url_bugtracker }}{% endif %}

{% if has_user_docs -%}
Project Documentation
---------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *
   generated/standards

{% endif -%}
Package API
-----------

.. toctree::
   :maxdepth: 2
   {{ package_toc_entry }}
   {% if has_message_definitions %}generated/message_definitions{% endif %}
   {% if has_service_definitions %}generated/service_definitions{% endif %}

Indices and Search
==================

* :ref:`genindex`
* :ref:`search`
