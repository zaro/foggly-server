from celery import chain
from core.tasks import *
from host_worker.tasks import *

import logging
log = logging.getLogger('hostjobs')


class DomainJobs:
    def __init__(self, hostMainDomain):
        self.hostMainDomain = hostMainDomain

    def create(self, cfg):
        return chain(
            createDomain.s(cfg).set(queue=self.hostMainDomain),
            createDomainRecord.s(cfg).set(queue='host_ctrl')
        )()

    def remove(self, cfg):
        return chain(
            removeDomain.s(cfg).set(queue=self.hostMainDomain),
            removeDomainRecord.s(cfg).set(queue='host_ctrl')
        )()

    def start(self, cfg):
        return chain(
            startDomain.s(cfg).set(queue=self.hostMainDomain),
            dockerStatus.s(cfg).set(queue=self.hostMainDomain)
        )()

    def stop(self, cfg):
        return chain(
            stopDomain.s(cfg).set(queue=self.hostMainDomain),
            dockerStatus.s(cfg).set(queue=self.hostMainDomain)
        )()

    def addPublicKey(self, cfg):
        return addPublicKey.s(cfg).set(queue=self.hostMainDomain).apply_async()


class MysqlJobs:
    def __init__(self, hostMainDomain):
        self.hostMainDomain = hostMainDomain

    def create(self, cfg):
        return chain(
            addMysqlDatabase.s(cfg).set(queue=self.hostMainDomain),
            addMysqlDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()

    def remove(self, cfg):
        return chain(
            removeMysqlDatabase.s(cfg).set(queue=self.hostMainDomain),
            removeMysqlDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()
