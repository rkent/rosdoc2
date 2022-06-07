{{ root_title }}
{{ root_title_underline }}

{{ package_description }}

{% if url_repository or url_website or url_bugtracker %}
Links
-----
{% if url_repository %}{{ url_repository }}{% endif %}
{% if url_website %}{{ url_website }}{% endif %}
{% if url_bugtracker %}{{ url_bugtracker }}{% endif %}

{% endif %} 
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
   :maxdepth: 4
   {{ package_toc_entry }}
   {% if has_message_definitions %}generated/message_definitions{% endif %}
   {% if has_service_definitions %}generated/service_definitions{% endif %}

.. toctree::
   :hidden:

   generated/indices_and_search
