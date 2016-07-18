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

    $cat Procfile
    web: uwsgi --module DJANGO_APP.wsgi --static-map /static=./static/

The following uwsgi arguments are recognized:

    - --module
    - --wsgi-file
    - --static-map
    - --processes
    - --max-requests

#### Create executable .hooks/on_deploy for migrations

    $chmod a+x .hooks/on_deploy
    $cat .hooks/on_deploy
    #/bin/sh
    manage.py migrate --noinput

{% include 'common_post.md' %}
{% endmarkdown %}
{% endblock %}
