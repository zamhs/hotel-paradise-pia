from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, F
from clientes.models import Cliente
from habitaciones.models import Habitacion

class Reservacion(models.Model):
    ESTADOS = [('confirmada', 'Confirmada'), ('hospedado', 'Hospedado'), ('completada', 'Completada'), ('cancelada', 'Cancelada')]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='reservaciones')
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='reservaciones')
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='confirmada')

    class Meta:
        ordering = ['-fecha_entrada', '-pk']
        verbose_name_plural = 'Reservaciones'
        constraints = [models.CheckConstraint(condition=Q(fecha_salida__gt=F('fecha_entrada')), name='salida_posterior_entrada')]

    def __str__(self):
        return f'Reservación #{self.pk} · {self.cliente}'

    def clean(self):
        super().clean()
        if not self.fecha_entrada or not self.fecha_salida:
            return
        if self.fecha_salida <= self.fecha_entrada:
            raise ValidationError({'fecha_salida': 'La fecha de salida debe ser posterior a la entrada.'})
        if not self.habitacion_id or self.estado == 'cancelada':
            return
        if not self.habitacion.disponible and self.estado in ['confirmada', 'hospedado']:
            raise ValidationError({'habitacion': 'Esta habitación está fuera de servicio.'})
        choque = Reservacion.objects.filter(habitacion_id=self.habitacion_id,
            fecha_entrada__lt=self.fecha_salida, fecha_salida__gt=self.fecha_entrada
        ).exclude(estado='cancelada').exclude(pk=self.pk)
        if choque.exists():
            raise ValidationError({'habitacion': 'No está disponible: ya existe una reservación en esas fechas.'})

    @property
    def noches(self):
        return (self.fecha_salida - self.fecha_entrada).days

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        self.total = self.noches * self.habitacion.precio_noche
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'total'}
        super().save(*args, **kwargs)
