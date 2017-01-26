from django.core.management.base import BaseCommand, CommandError
from host_worker import tasks
import tempfile, os, re


class Command(BaseCommand):
    help = 'Invoke a Celery task'

    def add_arguments(self, parser):
        parser.add_argument('task', nargs=1, type=str)
        parser.add_argument('user', nargs=1, type=str)
        parser.add_argument('domain', nargs=1, type=str)
        parser.add_argument('--host', required=True, type=str)
        parser.add_argument('--mysql_user', type=str)
        parser.add_argument('--mysql_password', type=str)
        parser.add_argument('--mysql_db', type=str)
        parser.add_argument('--container_id', type=str, default='foggly/php7')
        parser.add_argument('--proxy_type', type=str, default='http')

    def handle(self, *args, **options):
        for k in options.keys():
            if type(options[k]) == list and len(options[k]) == 1:
                options[k] = options[k][0]
        print('Execute task {task} with user={user} domain={domain}'.format(**options))
        task = getattr(tasks, options['task'], None)
        if not task:
            print('Invalid task')
            return
        if options['task'].endswith('PublicKey'):
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
            options['publicKey'] = line
        params = dict(options)
        params['app_type'] = {
            'container_id': options['container_id'],
            'proxy_type': options['proxy_type'],
        }
        result = task.s(params).set(queue=options['host']).apply_async()
        print(result.get())
