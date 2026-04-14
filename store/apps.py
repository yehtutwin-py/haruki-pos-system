from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import os
        from django.db import connection

        # Only run if database is ready
        try:
            from django.contrib.auth.models import User
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@1234')
            email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@haruki.com')

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                print(f'Admin user "{username}" created successfully!')
        except Exception as e:
            print(f'Error occurred while creating admin user: {e}')