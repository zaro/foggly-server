from celery import chain
from core.tasks import *
from host_worker.tasks import *

import logging
log = logging.getLogger('hostjobs')


class JobsDecriptorBase:
    def __init__(self, hostMainDomain, user):
        self.hostMainDomain = hostMainDomain
        self.user = user

    def cfgDefaults(self, cfg):
        cfg['user'] = self.user


class DomainJobs(JobsDecriptorBase):

    def create(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            createDomain.s(cfg).set(queue=self.hostMainDomain),
            createDomainRecord.s(cfg).set(queue='host_ctrl')
        )()

    def remove(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            removeDomain.s(cfg).set(queue=self.hostMainDomain),
            removeDomainRecord.s(cfg).set(queue='host_ctrl')
        )()

    def start(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            startDomain.s(cfg).set(queue=self.hostMainDomain),
            dockerStatus.s(cfg).set(queue=self.hostMainDomain)
        )()

    def stop(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            stopDomain.s(cfg).set(queue=self.hostMainDomain),
            dockerStatus.s(cfg).set(queue=self.hostMainDomain)
        )()

    def addPublicKey(self, cfg):
        self.cfgDefaults(cfg)
        return addPublicKey.s(cfg).set(queue=self.hostMainDomain).apply_async()

    def enableSsl(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            enableDomainSsl.s(cfg).set(queue=self.hostMainDomain),
            updateDomainConfig.s(cfg).set(queue='host_ctrl')
        )()


class DatabaseJobs(JobsDecriptorBase):

    def create(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            addDatabase.s(cfg).set(queue=self.hostMainDomain),
            addDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()

    def remove(self, cfg):
        self.cfgDefaults(cfg)
        return chain(
            removeDatabase.s(cfg).set(queue=self.hostMainDomain),
            removeDatabaseRecord.s(cfg).set(queue='host_ctrl')
        )()
