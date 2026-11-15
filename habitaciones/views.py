from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from config.helpers import formulario
from .models import Habitacion
from .forms import HabitacionForm

@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    habitaciones = Habitacion.objects.all()
    if q:
        habitaciones = habitaciones.filter(Q(numero__icontains=q) | Q(tipo__icontains=q))
    if tipo:
        habitaciones = habitaciones.filter(tipo=tipo)
    hoy = timezone.localdate()
    ocupadas = set(habitaciones.filter(reservaciones__fecha_entrada__lte=hoy,
        reservaciones__fecha_salida__gt=hoy, reservaciones__estado__in=['confirmada','hospedado']).values_list('pk', flat=True))
    return render(request, 'habitaciones/lista.html', {'habitaciones': habitaciones, 'ocupadas': ocupadas, 'q': q, 'tipo': tipo, 'tipos': Habitacion.TIPOS})

@login_required
def editar(request, pk=None):
    obj = get_object_or_404(Habitacion, pk=pk) if pk else None
    form = HabitacionForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Habitación guardada correctamente.')
        return redirect('habitaciones:lista')
    return formulario(request, form, 'Editar habitación' if obj else 'Nueva habitación', reverse('habitaciones:lista'))

@login_required
def eliminar(request, pk):
    obj = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                obj.delete()
            messages.success(request, 'Habitación eliminada.')
        except ValidationError as e:
            messages.error(request, e.messages[0])
        return redirect('habitaciones:lista')
    return render(request, 'confirmar.html', {'titulo':'Eliminar habitación','objeto':obj,'regreso':reverse('habitaciones:lista'),'accion':'Eliminar','detalle':'Se eliminará la habitación y sus reservaciones históricas. No se puede eliminar si tiene reservas activas.'})
