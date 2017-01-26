"""
    systemd interface module
"""
import time
import platform
if platform.system() == 'Linux':
    # from pydbus import SystemBus
    from pydbus.bus import connect


class SystemdCtl:
    def __init__(self):
        # self.bus = SystemBus()
        self.bus = connect('unix:path=/var/run/dbus/system_bus_socket')
        self.systemd = self.bus.get(".systemd1")
        self.manager = self.systemd[".Manager"]

    def _waitUnitState(self, unitName, waitForState, timeout=10):
        unit = self.bus.get('.systemd1', self.manager.GetUnit(unitName))
        while timeout > 0:
            if unit.SubState == waitForState:
                return True
            time.sleep(.2)
            timeout -= .2
        return False

    def startUnit(self, unitName):
        self.manager.StartUnit(unitName, 'replace')
        return self._waitUnitState(unitName, 'running')

    def stopUnit(self, unitName):
        self.manager.StopUnit(unitName, 'replace')
        return self._waitUnitState(unitName, 'dead')

    def restartUnit(self, unitName):
        self.manager.RestartUnit(unitName, 'replace')
        return self._waitUnitState(unitName, 'running')

    def reloadUnit(self, unitName):
        self.manager.ReloadUnit(unitName, 'replace')
        return self._waitUnitState(unitName, 'running')


if __name__ == '__main__':
    sctl = SystemdCtl()
    print("restart:", sctl.restartUnit('nginx.service'))
    print("stop:", sctl.stopUnit('nginx.service'))
    print("start:", sctl.startUnit('nginx.service'))
    print("reload:", sctl.reloadUnit('nginx.service'))
