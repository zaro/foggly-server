from celery import chain
from core.tasks import *
from core.hosttasks import *  # noqa

import logging
log = logging.getLogger('hostjobs')


class DomainJobs:
    def __init__(self, hostMainDomain):
        self.hostMainDomain = hostMainDomain

    def create(self, cfg):
        return chain(
            createDomain.s(cfg).set(queue=self.hostMainDomain),
            createDomainRecord.s()
        )()

    def remove(self, cfg):
        return chain(
            removeDomain.s(cfg).set(queue=self.hostMainDomain),
            removeDomainRecord.s()
        )()

    def start(self, cfg):
        return startDomain.apply_async(cfg, queue=self.hostMainDomain)

    def stop(self, cfg):
        return stopDomain.apply_async(cfg, queue=self.hostMainDomain)


class MysqlJobs:
    def __init__(self, hostMainDomain):
        self.hostMainDomain = hostMainDomain

    def create(self, cfg):
        return chain(
            addMysqlDatabase.s(cfg).set(queue=self.hostMainDomain),
            addMysqlDatabaseRecord.s()
        )()

    def remove(self, cfg):
        return chain(
            removeMysqlDatabase.s(cfg).set(queue=self.hostMainDomain),
            removeMysqlDatabaseRecord.s()
        )()
