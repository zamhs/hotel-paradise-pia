from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.dateparse import parse_date
from habitaciones.models import Habitacion
from clientes.models import Cliente
from reservaciones.models import Reservacion

@login_required
def dashboard(request):
    hoy = timezone.localdate()
    activas = Reservacion.objects.filter(estado__in=['confirmada','hospedado'], fecha_entrada__lte=hoy, fecha_salida__gt=hoy)
    ocupadas = activas.values('habitacion_id')
    disponibles = Habitacion.objects.filter(disponible=True).exclude(pk__in=ocupadas).count()
    recientes = Reservacion.objects.select_related('habitacion','cliente').order_by('-pk')[:6]
    return render(request, 'reportes/dashboard.html', {
        'clientes_total':Cliente.objects.count(), 'habitaciones_total':Habitacion.objects.count(),
        'reservas_total':Reservacion.objects.count(), 'disponibles':disponibles,
        'ingresos':Reservacion.objects.exclude(estado='cancelada').aggregate(total=Sum('total'))['total'] or 0,
        'recientes':recientes, 'hoy':hoy, 'ocupadas':activas.values('habitacion_id').distinct().count(),
    })

@login_required
def reportes(request):
    inicio = request.GET.get('inicio','')
    fin = request.GET.get('fin','')
    estado = request.GET.get('estado','')
    reservas = Reservacion.objects.select_related('cliente','habitacion')
    error = ''
    try:
        if inicio:
            fecha = parse_date(inicio)
            if not fecha: raise ValueError()
            reservas = reservas.filter(fecha_entrada__gte=fecha)
        if fin:
            fecha = parse_date(fin)
            if not fecha: raise ValueError()
            reservas = reservas.filter(fecha_entrada__lte=fecha)
        if inicio and fin and inicio > fin:
            raise ValueError()
    except (ValueError, TypeError):
        error = 'Selecciona un rango válido.'
        reservas = Reservacion.objects.none()
    if estado:
        reservas = reservas.filter(estado=estado)
    grupos = reservas.values('estado').annotate(cantidad=Count('id')).order_by('estado')
    ingresos = reservas.exclude(estado='cancelada').aggregate(total=Sum('total'))['total'] or 0
    return render(request, 'reportes/reportes.html', {'reservas':reservas,'ingresos':ingresos,'grupos':grupos,'inicio':inicio,'fin':fin,'estado':estado,'estados':Reservacion.ESTADOS,'error':error,'cantidad':reservas.count()})
