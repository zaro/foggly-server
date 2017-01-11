from django import template

register = template.Library()


class DummyConfig(dict):
    def __init__(self, *args):
        dict.__init__(self, args)

    def __missing__(self, key):
        return '[' + key + ']'


class DomainConfigDoc:
    def __init__(self, context):
        self.d = context.get('domain')

    def key(self, key):
        dc = self.d.domainconfig_set.filter(key=key) if self.d else None
        return dc[0].value if dc else '[' + key + ']'

    def asDict(self):
        if self.d:
            r = {}
            for c in self.d.domainconfig_set.all():
                r[c.key] = c.value
            return r
        else:
            return DummyConfig()

    def gitRemote(self):
        d = self.asDict()
        return 'ssh://www-data@{DOMAIN}:{SSH_PORT}/www'.format_map(d)


@register.simple_tag(takes_context=True)
def dConf(context, key):
    return DomainConfigDoc(context).key(key)


@register.simple_tag(takes_context=True)
def gitRemote(context):
    return DomainConfigDoc(context).gitRemote()
