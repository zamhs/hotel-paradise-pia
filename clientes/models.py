from django.db import models
from django.db.models.functions import Lower

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=25)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['apellidos', 'nombre']
        constraints = [models.UniqueConstraint(Lower('correo'), name='cliente_correo_unico_ci')]

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'

    def save(self, *args, **kwargs):
        self.correo = self.correo.strip().lower()
        super().save(*args, **kwargs)
