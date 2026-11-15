from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import OperationalError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import timedelta
from config.helpers import formulario
from habitaciones.models import Habitacion
from .models import Reservacion
from .forms import ReservacionForm

@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    reservas = Reservacion.objects.select_related('cliente', 'habitacion')
    if q:
        for palabra in q.split():
            reservas = reservas.filter(Q(cliente__nombre__icontains=palabra)|Q(cliente__apellidos__icontains=palabra)|Q(habitacion__numero__icontains=palabra)|Q(habitacion__tipo__icontains=palabra))
    if estado:
        reservas = reservas.filter(estado=estado)
    return render(request, 'reservaciones/lista.html', {'reservas':reservas,'q':q,'estado':estado,'estados':Reservacion.ESTADOS})

@login_required
def editar(request, pk=None):
    obj = get_object_or_404(Reservacion, pk=pk) if pk else None
    if obj and obj.estado == 'cancelada':
        messages.error(request, 'Una reserva cancelada no se puede modificar.')
        return redirect('reservaciones:lista')
    initial = {}
    if not obj:
        initial = {'habitacion':request.GET.get('habitacion'), 'fecha_entrada':request.GET.get('entrada', timezone.localdate()), 'fecha_salida':request.GET.get('salida', timezone.localdate()+timedelta(days=1))}
    form = ReservacionForm(request.POST or None, instance=obj, initial=initial)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            messages.success(request, 'Reservación guardada correctamente.')
            return redirect('reservaciones:lista')
        except ValidationError as e:
            form.add_error(None, e)
        except OperationalError:
            form.add_error(None, 'No se pudo guardar por una operación simultánea. Intenta de nuevo.')
    return formulario(request, form, 'Editar reservación' if obj else 'Nueva reservación', reverse('reservaciones:lista'), 'El total se calcula automáticamente de acuerdo con las noches y la tarifa de la habitación.')

@login_required
def cancelar(request, pk):
    obj = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'POST':
        if obj.estado not in ['cancelada', 'completada']:
            obj.estado = 'cancelada'
            obj.save()
            messages.success(request, 'Reservación cancelada.')
        return redirect('reservaciones:lista')
    return render(request, 'confirmar.html', {'titulo':'Cancelar reservación','objeto':obj,'regreso':reverse('reservaciones:lista'),'accion':'Cancelar reservación','detalle':'La habitación volverá a estar disponible para esas fechas.'})

@login_required
def disponibilidad(request):
    entrada = request.GET.get('entrada', str(timezone.localdate()))
    salida = request.GET.get('salida', str(timezone.localdate()+timedelta(days=1)))
    tipo = request.GET.get('tipo', '')
    error = ''
    rooms = Habitacion.objects.none()
    try:
        a, b = parse_date(entrada), parse_date(salida)
        if not a or not b or b <= a:
            raise ValueError()
        ocupadas = Reservacion.objects.filter(fecha_entrada__lt=b, fecha_salida__gt=a).exclude(estado='cancelada').values('habitacion_id')
        rooms = Habitacion.objects.filter(disponible=True).exclude(pk__in=ocupadas)
        if tipo:
            rooms = rooms.filter(tipo=tipo)
    except (ValueError, TypeError):
        error = 'Ingresa fechas válidas. La salida debe ser posterior a la entrada.'
    return render(request, 'reservaciones/disponibilidad.html', {'habitaciones':rooms,'entrada':entrada,'salida':salida,'tipo':tipo,'tipos':Habitacion.TIPOS,'error':error})
