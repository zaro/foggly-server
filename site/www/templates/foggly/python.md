{% extends 'base.html' %}
{% load markdown_deux_tags conf_helpers %}

{% block content %}
{% markdown %}

# Quick start for foggly/python app runtime
{% include 'common_pre.md' %}
## write app

###Simple WSGI app
#### create app.py with following content

    def application(env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"Hi there"]

### Django
#### create Procfile like this

    cat Procfile
    web: uwsgi --module DJANGO_APP.wsgi --static-map /static=./static/

The following uwsgi arguments are recognized:

  - [--module](http://uwsgi-docs.readthedocs.io/en/latest/Options.html?highlight=module#module)
  - [--wsgi-file](http://uwsgi-docs.readthedocs.io/en/latest/Options.html?highlight=wsgi-file#wsgi-file)
  - [--static-map](http://uwsgi-docs.readthedocs.io/en/latest/Options.html?highlight=wsgi-file#static-map)
  - [--processes](http://uwsgi-docs.readthedocs.io/en/latest/Options.html?highlight=wsgi-file#processes)
  - [--max-requests](http://uwsgi-docs.readthedocs.io/en/latest/Options.html?highlight=wsgi-file#max-requests)

#### Create executable .hooks/on_deploy for migrations like this

```sh
#/bin/sh
manage.py migrate --noinput
```

{% include 'common_post.md' %}
{% endmarkdown %}
{% endblock %}
