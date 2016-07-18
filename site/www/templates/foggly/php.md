{% extends 'base.md' %}
{% load markdown_deux_tags conf_helpers %}

{% block content %}
{% markdown %}
## write app

### Standalone
#### create index.php with following content

```php
<?php
  phpinfo()
?>
```
Composer is supported, just add composer.json

{% endmarkdown %}
{% endblock %}
