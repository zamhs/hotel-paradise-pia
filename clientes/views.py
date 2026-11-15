from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from config.helpers import formulario
from .models import Cliente
from .forms import ClienteForm

@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()
    if q:
        for palabra in q.split():
            clientes = clientes.filter(Q(nombre__icontains=palabra)|Q(apellidos__icontains=palabra)|Q(correo__icontains=palabra)|Q(telefono__icontains=palabra))
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'q': q})

@login_required
def editar(request, pk=None):
    obj = get_object_or_404(Cliente, pk=pk) if pk else None
    form = ClienteForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente guardado correctamente.')
        return redirect('clientes:lista')
    return formulario(request, form, 'Editar cliente' if obj else 'Nuevo cliente', reverse('clientes:lista'))

@login_required
def eliminar(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Cliente eliminado.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar un cliente con historial de reservaciones.')
        return redirect('clientes:lista')
    return render(request, 'confirmar.html', {'titulo':'Eliminar cliente','objeto':obj,'regreso':reverse('clientes:lista'),'accion':'Eliminar','detalle':'Esta acción no se puede deshacer.'})
