"""
    systemd interface module
"""

import dbus
import time


class SystemdCtl:
    def __init__(self):
        self.bus = dbus.SystemBus()
        proxy = self.bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self.manager = dbus.Interface(proxy, dbus_interface='org.freedesktop.systemd1.Manager')

    def _getUnit(self, unitName):
        unitPath = self.manager.GetUnit(unitName)
        proxy = self.bus.get_object('org.freedesktop.systemd1', str(unitPath))
        unitInterface = dbus.Interface(proxy, dbus_interface='org.freedesktop.systemd1.Unit')
        return (proxy, unitInterface)

    def _getUnitProperty(self, unitProxy, propName, unitType="Service"):
        return unitProxy.Get('org.freedesktop.systemd1.' + unitType, propName, dbus_interface='org.freedesktop.DBus.Properties')

    def _waitJobEnd(self, unitProxy, timeout=10):
        while timeout > 0:
            if self._getUnitProperty(unitProxy, 'Job', 'Unit')[0] == 0:
                return True
            time.sleep(.2)
            timeout -= .2
        return False

    def startUnit(self, unitName):
        proxy, interface = self._getUnit(unitName)
        interface.Start('replace')
        self._waitJobEnd(proxy)
        return self._getUnitProperty(proxy, 'Result')

    def stopUnit(self, unitName):
        proxy, interface = self._getUnit(unitName)
        interface.Stop('replace')
        self._waitJobEnd(proxy)
        return self._getUnitProperty(proxy, 'Result')

    def restartUnit(self, unitName):
        proxy, interface = self._getUnit(unitName)
        interface.Restart('replace')
        self._waitJobEnd(proxy)
        return self._getUnitProperty(proxy, 'Result')

    def reloadUnit(self, unitName):
        proxy, interface = self._getUnit(unitName)
        interface.Reload('replace')
        self._waitJobEnd(proxy)
        return self._getUnitProperty(proxy, 'Result')


if __name__ == '__main__':
    sctl = SystemdCtl()
    print("restart:", sctl.restartUnit('nginx.service'))
    print("stop:", sctl.stopUnit('nginx.service'))
    print("start:", sctl.startUnit('nginx.service'))
    print("reload:", sctl.reloadUnit('nginx.service'))
