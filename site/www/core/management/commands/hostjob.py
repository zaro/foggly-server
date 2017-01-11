from django.core.management.base import BaseCommand
import core.hostjobs as tasks
import tempfile, os, re
import argparse
import inspect


def getJobList():
    l = []
    for klass in dir(tasks):
        if klass.endswith('Jobs'):
            jobsClass = getattr(tasks, klass, None)
            if jobsClass and inspect.isclass(jobsClass):
                l += [ klass + '.' + job for job in dir(jobsClass) if not job.startswith('_')]
    return l


def getJob(job, host):
    klass, method = job.split('.')
    jobsClass = getattr(tasks, klass, None)
    if jobsClass and inspect.isclass(jobsClass):
        jcInstance = jobsClass(host)
        jobMethod = getattr(jcInstance, method, None)
        if jobMethod:
            return jobMethod
    return None


class StoreNameValuePair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        cfg = {}
        setattr(namespace, 'cfg', cfg)
        for value in values:
            if value.find('=') > 0:
                n, v = value.split('=')
                cfg[n] = v
            else:
                cfg[value] = True


class Command(BaseCommand):
    help = 'Invoke a host job, one of:\n' + '\n'.join(getJobList())

    def add_arguments(self, parser):
        parser.add_argument('job', type=str)
        parser.add_argument('host', type=str)
        parser.add_argument('user', type=str)
        parser.add_argument('domain', type=str)
        parser.add_argument('cfg', nargs='*', type=str, action=StoreNameValuePair)

    def handle(self, *args, **options):
        print('Execute job {job} with user={user} domain={domain} cfg={cfg}'.format(**options))
        job = getJob(options['job'], options['host'])
        if not job:
            print('Invalid job')
            return
        cfg = dict(options['cfg'])
        if options['job'].endswith('PublicKey'):
            tfd, path = tempfile.mkstemp()
            os.write(tfd, b'# paste public key below\n')
            os.close(tfd)
            os.system('nano {}'.format(path))
            with open(path, 'r') as f:
                lines = f.readlines()
                line = None
                for l in lines:
                    if re.match('\s*#', l) or re.match('\s*$', l):
                        continue
                    line = l.strip()
                    break
            os.unlink(path)
            if not line:
                print('You must specify public key to add')
                return
            cfg['publicKey'] = line
        cfg['user'] = options['user']
        cfg['domain'] = options['domain']
        cfg['host'] = options['host']
        result = job(cfg)
        print(result.get())
