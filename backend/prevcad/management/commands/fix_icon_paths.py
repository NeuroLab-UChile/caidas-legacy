from django.core.management.base import BaseCommand
from prevcad.models import CategoryTemplate

class Command(BaseCommand):
    help = 'Fix icon paths by removing leading slashes'

    def handle(self, *args, **options):
        templates = CategoryTemplate.objects.all()
        for template in templates:
            if template.icon and str(template.icon).startswith('/'):
                old_path = str(template.icon)
                template.icon = old_path.lstrip('/')
                template.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed icon path for template {template.id}: {old_path} -> {template.icon}'
                    )
                ) 