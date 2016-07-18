{% load conf_helpers %}
## add code && push

    $ git add *
    $ git commit -m 'cool'
    $ git push

## your app is now running at

  [http://{% dConf 'DOMAIN' %}/](http://{% dConf 'DOMAIN' %}/)
