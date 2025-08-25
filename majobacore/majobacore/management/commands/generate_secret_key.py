"""
Custom management command to create a new secret key.
Usage: python manage.py generate_secret_key
"""

from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = 'Generate a new Django secret key'

    def handle(self, *args, **options):
        secret_key = get_random_secret_key()
        self.stdout.write(
            self.style.SUCCESS(f'New secret key generated: {secret_key}')
        )
        self.stdout.write(
            self.style.WARNING('Please update your .env file with this new secret key.')
        )
