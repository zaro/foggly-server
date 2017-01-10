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

    def enableSsl(self, cfg):
        return chain(
            enableDomainSsl.s(cfg).set(queue=self.hostMainDomain),
            updateDomainConfig.s(cfg).set(queue='host_ctrl')
        )()


class DatabaseJobs:
    def __init__(self, hostMainDomain):
        self.hostMainDomain = hostMainDomain

    def create(self, cfg):
        return chain(
            addDatabase.s(cfg).set(queue=self.hostMainDomain),
            addDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()

    def remove(self, cfg):
        return chain(
            removeDatabase.s(cfg).set(queue=self.hostMainDomain),
            removeDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()
