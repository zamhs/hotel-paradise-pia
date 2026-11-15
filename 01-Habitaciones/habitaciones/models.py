from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

class HabitacionQuerySet(models.QuerySet):
    def delete(self):
        if self.filter(reservaciones__estado__in=['confirmada', 'hospedado']).exists():
            raise ValidationError('No se pueden eliminar habitaciones con reservaciones activas.')
        return super().delete()

class Habitacion(models.Model):
    objects = HabitacionQuerySet.as_manager()
    TIPOS = [('Individual', 'Individual'), ('Doble', 'Doble'), ('Suite', 'Suite'), ('Presidencial', 'Presidencial')]
    numero = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1)])
    tipo = models.CharField(max_length=20, choices=TIPOS)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    capacidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    disponible = models.BooleanField(default=True, help_text='Desmarca si está fuera de servicio.')
    imagen = models.ImageField(upload_to='habitaciones/', blank=True)

    class Meta:
        ordering = ['numero']
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return f'{self.numero} · {self.tipo}'

    def delete(self, *args, **kwargs):
        if self.reservaciones.filter(estado__in=['confirmada', 'hospedado']).exists():
            raise ValidationError('No se puede eliminar una habitación con reservaciones activas.')
        return super().delete(*args, **kwargs)
