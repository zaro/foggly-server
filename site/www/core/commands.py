from django.core.management.base import BaseCommand, CommandError


class CommandCreateDomain(BaseCommand):
    help = "Create user's domain"

    def handle(self, * args, ** options):
        pass
