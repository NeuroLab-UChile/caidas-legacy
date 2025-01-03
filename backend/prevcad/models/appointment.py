from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Usuario'
    )
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción', blank=True)
    date = models.DateTimeField('Fecha y Hora')
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%d/%m/%Y %H:%M')}" 