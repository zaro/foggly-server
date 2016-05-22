from django.core.management.base import BaseCommand
from celery.app.control import Inspect
import celery.app


class Command(BaseCommand):
    help = 'List Celery workers'

    def add_arguments(self, parser):
        # parser.add_argument('task', nargs=1, type=str)
        # parser.add_argument('user', nargs=1, type=str)
        # parser.add_argument('domain', nargs=1, type=str)
        # parser.add_argument('--mysql_user', type=str)
        # parser.add_argument('--mysql_password', type=str)
        # parser.add_argument('--mysql_db', type=str)
        # parser.add_argument('--app_type', type=str, default='zaro/php7')
        pass

    def printRow(self, columns):
        numSpaces = 1 + (self.maxNameLen - len(columns[0]))
        print(columns[0] + (' ' * numSpaces) + '| ', end="")
        print(' '.join(columns[1:]))

    def handle(self, *args, **options):
        celeryApp = celery.app.app_or_default()
        activeQueues = Inspect(app=celeryApp).active_queues()
        self.maxNameLen = max([len(name) for name in activeQueues.keys() ])
        if self.maxNameLen < len('Worker Name'):
            self.maxNameLen = len('Worker Name')
        self.printRow(['Worker Name', 'Queues'])
        print('-' * 80)
        for workerName, queues in activeQueues.items():
            self.printRow([workerName, ', '.join([q['name'] for q in queues])])
