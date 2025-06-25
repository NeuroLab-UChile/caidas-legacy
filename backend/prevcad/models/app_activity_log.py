from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
from typing import (
    Any,
    List,
    cast,
    Dict,
    Optional,
    Union,
    Type,
    Literal,
    Optional,
    LiteralString,
)
from pydantic import BaseModel, RootModel, Field, ValidationError, constr


class AppActivityLog(models.Model):
    """Modelo para registrar actividades de la aplicación"""

    class Meta:
        verbose_name = "Registro de Actividad de la Aplicación"
        verbose_name_plural = "Registros de Actividad de la Aplicación"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["user"]),
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Usuario",
    )
    # action = models.CharField(max_length=255, verbose_name="Acción")
    # timestamp = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
    actions = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="Acciones",
        help_text="Registro de acciones realizadas por el usuario con timestamp, en formato JSON. Ejemplo"
        "{'08:02:33': 'Login', '08:02:35': 'Logout'}",
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Fecha",
        help_text="Fecha de la actividad registrada",
    )
    n_entries = models.IntegerField(
        null=True, blank=True, verbose_name="Número de Entradas"
    )
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class SchemaGenerator:
        """
        Base class for dynamically defining RootModel types.
        A Pydantic model for daily readings with dynamic keys (timestamps) and flexible values.
        Keys must be in the format HH:MM:SS, and values can be either a float or a ComplexReading object.
        """

        accepted_values: Type = str

        @classmethod
        def create_model(cls):
            """
            Dynamically create a RootModel class based on `accepted_values`.
            Restrict keys to be timestamps in the format HH:MM:SS.
            """
            return RootModel[
                Dict[constr(pattern=r"^\d{2}:\d{2}:\d{2}$"), cls.accepted_values]
            ]

    Schema = SchemaGenerator.create_model()

    def validate_schema(self, actions: Dict[str, str]):
        """Validate the structure of the provided actions."""
        try:
            self.Schema.model_validate(actions)
        except ValidationError as e:
            raise ValueError(f"Invalid actions structure: {e.errors()}")

    def add_actions(self, new_actions: Dict[str, str]):
        """
        Add multiple actions to the log after schema validation.

        Args:
            new_actions (Dict[str, str]): Dictionary of timestamped actions.
        """
        self.validate_schema(new_actions)

        # Ensure all actions are lowercase
        new_actions = {k: v.lower() for k, v in new_actions.items()}

        if not self.actions:
            self.actions = {}
        # By using update, we can add new actions with different timestamps without altering the rest
        self.actions.update(new_actions)
        self.n_entries = len(self.actions)
        self.save()

    @classmethod
    def add_action_for_user(
        cls, user, date, actions, **additional_fields
    ) -> "AppActivityLog":
        """
        Get or create an object for a user for a given date,
        and add actions to the log.
        """
        instance, created = cls.objects.get_or_create(
            user=user,
            date=date,
            defaults={**additional_fields, "actions": {}, "n_entries": 0},
        )
        instance.add_actions(actions)
        return instance

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the actions for the day."""

        print("Getting summary")
        n_logins = sum(1 for action in self.actions.values() if action == "login")

        # Estimate time_in_app with this simple logic:
        # Assuming each login is the start of a session, let's count the time between a login
        # and the last action before the next login (or the end of the day).
        # This is a simplification and may not reflect actual time spent in the app.
        time_in_app = 0  # In seconds
        sorted_actions = sorted(self.actions.items())
        session_start = None
        previous_timestamp = None

        def add_delta(start, end):
            nonlocal time_in_app
            start_dt = datetime.datetime.combine(datetime.date.today(), start)
            end_dt = datetime.datetime.combine(datetime.date.today(), end)
            session_duration = (end_dt - start_dt).total_seconds()
            if session_duration > 0:
                time_in_app += session_duration

        for timestamp_str, action in sorted_actions:
            timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S").time()
            if action == "login":
                if session_start is not None and previous_timestamp is not None:
                    add_delta(session_start, previous_timestamp)
                # Register the start of a new session
                session_start = timestamp
                previous_timestamp = None
            else:
                previous_timestamp = timestamp

        # Count the last session if it was not closed
        if session_start is not None and previous_timestamp is not None:
            add_delta(session_start, previous_timestamp)

        # Now have a version in the form of "HH:MM:SS"
        time_in_app = int(time_in_app)  # Convert to seconds
        time_in_app_str = str(datetime.timedelta(seconds=time_in_app))

        return {
            "user": self.user,
            "date": self.date,
            "n_entries": self.n_entries,
            "n_logins": n_logins,
            "time_in_app": time_in_app,
            "time_in_app_str": time_in_app_str,
        }
