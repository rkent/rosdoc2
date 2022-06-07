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
Testing
-------
Testing of index.j2.rst

{% if has_user_docs -%}
Project Documentation
---------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *
   {% if has_standard_docs %}generated/standards{% endif %}

{% endif -%}
{% if has_cpp or has_python or has_msg_defs or has_srv_defs %}
Packageses API
--------------

.. toctree::
   :maxdepth: 4

   {% if has_python %}Python API<generated/python/modules>{% endif %}
   {% if has_cpp %}C/C++ API<generated/cpp/index>{% endif %}
   {% if has_msg_defs %}generated/message_definitions{% endif %}
   {% if has_srv_defs %}generated/service_definitions{% endif %}

{% endif %}
.. toctree::
   :hidden:

   generated/indices_and_search

