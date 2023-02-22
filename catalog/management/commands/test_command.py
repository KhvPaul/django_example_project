from django.core.management.base import BaseCommand

from catalog.models import Genre


class Command(BaseCommand):
    help = "Test command"  # noqa: A003

    def handle(self, *args, **options):
        for i in Genre.objects.filter(name__iendswith="fiction"):
            self.stdout.write(str(i))
        self.stdout.write(self.style.SUCCESS("Successful!"))
