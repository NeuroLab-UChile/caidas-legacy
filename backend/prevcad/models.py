class HealthCategory(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('reviewed', 'Revisada'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(CategoryTemplate, on_delete=models.CASCADE)
    responses = models.JSONField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    status_color = models.CharField(max_length=10, null=True, blank=True)
    doctor_recommendations = models.TextField(null=True, blank=True) 