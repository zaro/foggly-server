"""
    firewalld interface module
"""
import platform
if platform.system() == 'Linux':
    # from pydbus import SystemBus
    from pydbus.bus import connect


class FirewalldCtl:
    def __init__(self):
        # self.bus = SystemBus()
        self.bus = connect('unix:path=/host_run/dbus/system_bus_socket')
        self.firewallD = self.bus.get('org.fedoraproject.FirewallD1')

    def addPort(self, port, zone='public', proto='tcp'):
        try:
            self.firewallD.addPort(zone, str(port), proto, 0)
            return True
        except Exception as e:
            if e.message.find('ALREADY_ENABLED:'):
                return True
            raise e

    def removePort(self, port, zone='public', proto='tcp'):
        try:
            self.firewallD.removePort(zone, str(port), proto)
            return True
        except Exception as e:
            if e.message.find('NOT_ENABLED:'):
                return True
            raise e

if __name__ == '__main__':
    fctl = FirewalldCtl()
    print('addPort(3333):', fctl.addPort(3333))
    print('addPort(3333):', fctl.addPort(3333))
    print('removePort(3333):', fctl.removePort(3333))
    print('removePort(3333):', fctl.removePort(3333))
