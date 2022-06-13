.. GENERATED_CONTENT by rosdoc2.verbs.build.builders.SphinxBuilder.

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
{% if meta_dependencies %}
Dependencies of this Meta Package
---------------------------------------
{% for subproject in meta_dependencies %}
* :doc:`{{subproject}}:index`
{% endfor %}
{% endif %}
{% if has_user_docs %}
Project Documentation
---------------------

.. toctree::
   :maxdepth: 2
   :glob:

   doc/*
{%- for (relpath, docname) in extra_doc_files %}
   {{ relpath }} <{{ docname }}>
{%- endfor %}
{% endif %}
{% if has_standard_docs %}
Standard Documents
------------------
.. toctree::
   :maxdepth: 1
   :glob:

   generated/standard/*

{% endif -%}
{% if did_run_doxygen or has_python or has_msg_defs or has_srv_defs %}
Package API
-----------

.. toctree::
   :maxdepth: 4

   {% if has_python %}Python API <generated/python/modules>{% endif %}
   {% if did_run_doxygen %}C/C++ API <generated/cpp/index>{% endif %}
   {% if has_msg_defs %}generated/message_definitions{% endif %}
   {% if has_srv_defs %}generated/service_definitions{% endif %}

{% endif %}
.. toctree::
   :hidden:

   generated/index_and_search
