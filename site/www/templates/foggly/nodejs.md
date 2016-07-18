{% extends 'base.md' %}
{% load markdown_deux_tags conf_helpers %}

{% block content %}
{% markdown %}
## write app

### Standalone
#### create package.json
```json
{
  "name": "test",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  }
}
```

#### create index.js with following content

```js
const http = require('http');

const server = http.createServer((req,res) => {
  res.setHeader('Content-Type', 'text/html');
  res.setHeader('X-Foo', 'bar');
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('ok');
});

server.listen(3000)
```
Your server MUST listen on port 3000.

{% endmarkdown %}
{% endblock %}
