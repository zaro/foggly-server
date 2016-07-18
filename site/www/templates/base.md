{% extends 'base.html' %}
{% load markdown_deux_tags conf_helpers %}


{% block pre_content %}
{% markdown %}
# Quick start for foggly/python app runtime

## Clone the repo or add remote to existing repo
### clone

    $ git clone {% gitRemote %}

### add remote to existing repo

    $ git remote add deploy {% gitRemote %}

{% endmarkdown %}
{% endblock%}
{% block content %}
{% endblock%}
{% block post_content %}
{% markdown %}
## add code && push

    $ git add *
    $ git commit -m 'cool'
    $ git push

## your app is now running at

  [http://{% dConf 'DOMAIN' %}/](http://{% dConf 'DOMAIN' %}/)

{% endmarkdown %}
{% endblock%}
