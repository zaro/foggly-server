"""
    firewalld interface module
"""
import platform
if platform.system() == 'Linux':
    import dbus


class FirewalldCtl:
    def __init__(self):
        self.bus = dbus.SystemBus()
        dbusObj = self.bus.get_object('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
        self.fwZone = dbus.Interface(dbusObj, dbus_interface='org.fedoraproject.FirewallD1.zone')

    def addPort(self, port, zone='public', proto='tcp'):
        try:
            self.fwZone.addPort(zone, str(port), proto, 0)
            return True
        except dbus.exceptions.DBusException as e:
            if e.get_dbus_message().startswith('ALREADY_ENABLED'):
                return True
            raise e

    def removePort(self, port, zone='public', proto='tcp'):
        try:
            self.fwZone.removePort(zone, str(port), proto)
            return True
        except dbus.exceptions.DBusException as e:
            if e.get_dbus_message().startswith('NOT_ENABLED'):
                return True
            raise e

if __name__ == '__main__':
    fctl = FirewalldCtl()
    print('addPort(3333):', fctl.addPort(3333))
    print('addPort(3333):', fctl.addPort(3333))
    print('removePort(3333):', fctl.removePort(3333))
    print('removePort(3333):', fctl.removePort(3333))
