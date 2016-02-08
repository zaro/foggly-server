from django.core.management.base import BaseCommand, CommandError
import core.tasks as tasks

class Command(BaseCommand):
    help = 'Invoke a Celery task'

    def add_arguments(self, parser):
        parser.add_argument('task', nargs=1, type=str)
        parser.add_argument('user', nargs=1, type=str)
        parser.add_argument('domain', nargs=1, type=str)

    def handle(self, *args, **options):
        for k in options.keys():
            if type(options[k]) == list and len(options[k]) == 1:
                options[k] = options[k][0]
        print('Execute task {task} with user={user} domain={domain}'.format(**options))
        task = getattr(tasks, options['task'], None)
        if not task:
            print('Invalid task')
            return
        result = task.delay(options)
        print(result.get())
