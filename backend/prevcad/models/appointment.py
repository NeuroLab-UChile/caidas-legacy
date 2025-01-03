from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción', blank=True)
    date = models.DateField('Fecha')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Usuario'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}" 