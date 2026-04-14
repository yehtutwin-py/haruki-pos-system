from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create superuser from environment variables automatically'

    def handle(self, *args, **kwargs):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@haruki.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@1234')

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Admin user "{username}" already exists.')
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(f'Admin user "{username}" created successfully!')