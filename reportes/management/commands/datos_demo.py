from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from habitaciones.models import Habitacion
from clientes.models import Cliente
from reservaciones.models import Reservacion

class Command(BaseCommand):
    help = 'Carga usuarios y registros ficticios de demostración de forma repetible.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        for username, staff, first_name in [('admin', True, 'Administrador'), ('recepcion', False, 'Recepción')]:
            user, created = User.objects.get_or_create(username=username, defaults={'first_name':first_name,'is_staff':staff,'is_superuser':staff})
            if created or (username == 'admin' and user.check_password('ParadiseDemo2026!')):
                user.set_password('admin' if username == 'admin' else 'ParadiseDemo2026!')
                user.save()
        rooms = {}
        for n, tipo, precio, capacidad, disponible in [(101,'Individual',850,1,True),(102,'Individual',850,1,True),(201,'Doble',1400,2,True),(202,'Doble',1400,2,True),(301,'Suite',2350,4,True),(302,'Suite',2350,4,True),(401,'Presidencial',4500,6,True),(402,'Presidencial',4500,6,False)]:
            rooms[n], _ = Habitacion.objects.get_or_create(numero=n, defaults={'tipo':tipo,'precio_noche':precio,'capacidad':capacidad,'disponible':disponible})
        clients = []
        for nombre, apellidos, correo, telefono in [('Ana','García López','ana@example.com','8110000101'),('Diego','Martínez Ruiz','diego@example.com','8110000102'),('Valeria','Hernández Soto','valeria@example.com','8110000103'),('Luis','Mendoza Flores','luis@example.com','8110000104'),('Sofía','Ramírez Torres','sofia@example.com','8110000105')]:
            c, _ = Cliente.objects.get_or_create(correo=correo, defaults={'nombre':nombre,'apellidos':apellidos,'telefono':telefono})
            clients.append(c)
        hoy = timezone.localdate()
        if not Reservacion.objects.exists():
            for idx, n, entrada, salida, estado in [(0,101,-1,2,'hospedado'),(1,201,0,3,'confirmada'),(2,301,4,7,'confirmada'),(3,102,-10,-7,'completada'),(4,401,8,10,'confirmada'),(0,202,-7,-5,'cancelada')]:
                Reservacion.objects.create(cliente=clients[idx], habitacion=rooms[n],fecha_entrada=hoy+timedelta(days=entrada),fecha_salida=hoy+timedelta(days=salida),estado=estado)
        self.stdout.write(self.style.SUCCESS('Datos de demostración listos. Acceso inicial de administrador: admin / admin.'))
