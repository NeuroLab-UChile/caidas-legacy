# Usage:
#
# To run from the console:
#   poetry run python manage.py change_user_password <email> [<new_password>]
#

import getpass
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Change a user's password or create the user if it does not exist."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the user to update or create")
        parser.add_argument(
            "password",
            nargs="?",
            help="New password. If omitted, the command prompts for it interactively.",
        )

    def _confirm(self, prompt):
        if not self.stdin.isatty():
            raise CommandError("Confirmation required but stdin is not interactive.")
        self.stdout.write(prompt, ending="")
        self.stdout.flush()
        answer = self.stdin.readline().strip().lower()
        return answer in {"y", "yes"}

    def _confirm_unusable_password(self):
        return self._confirm(
            "Blank password provided. Set an unusable password for this user? [y/N]: "
        )

    def _confirm_create_user(self, email):
        return self._confirm(
            f"User with email {email} does not exist. Create it? [y/N]: "
        )

    def handle(self, *args, **options):
        email = options["email"]
        password = options.get("password")
        self.stdin = sys.stdin

        user_model = get_user_model()
        user = user_model.objects.filter(email=email).first()

        if password is None:
            if not self.stdin.isatty():
                raise CommandError(
                    "Password argument is required when running non-interactively."
                )
            password = getpass.getpass("New password: ")

        set_unusable = password == ""
        if set_unusable and not self._confirm_unusable_password():
            self.stdout.write(self.style.WARNING("Password change aborted."))
            return

        if user is None:
            if not self._confirm_create_user(email):
                self.stdout.write(self.style.WARNING("User creation aborted."))
                return

            user = user_model.objects.create_user(email=email, password=None)
            action = "created"
        else:
            action = "updated"

        if set_unusable:
            user.set_unusable_password()
            password_state = "set to unusable"
        else:
            user.set_password(password)
            password_state = "updated"

        user.save(update_fields=["password"])
        self.stdout.write(
            self.style.SUCCESS(
                f"User {user.email} {action} successfully; password {password_state}."
            )
        )
