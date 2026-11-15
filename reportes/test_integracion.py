from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from tempfile import TemporaryDirectory
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from clientes.models import Cliente
from habitaciones.models import Habitacion
from reservaciones.models import Reservacion

class DemoAccessTests(TestCase):
    def test_credenciales_visibles_y_login(self):
        call_command('datos_demo')
        response = self.client.get(reverse('seguridad:login'))
        self.assertContains(response, 'Usuario: <code>admin</code>', html=True)
        self.assertContains(response, 'Contraseña: <code>admin</code>', html=True)
        response = self.client.post(reverse('seguridad:login'), {'username':'admin', 'password':'admin'})
        self.assertRedirects(response, reverse('reportes:dashboard'))
        self.assertTrue(get_user_model().objects.get(username='admin').is_superuser)

    def test_actualiza_password_demo_anterior_sin_restaurar_uno_personalizado(self):
        user = get_user_model().objects.create_superuser(username='admin', password='ParadiseDemo2026!')
        call_command('datos_demo')
        user.refresh_from_db()
        self.assertTrue(user.check_password('admin'))
        user.set_password('MiPasswordPersonalizado!')
        user.save()
        call_command('datos_demo')
        user.refresh_from_db()
        self.assertTrue(user.check_password('MiPasswordPersonalizado!'))

class HotelTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username='prueba', password='Prueba123456!')
        self.client.force_login(self.usuario)
        self.habitacion = Habitacion.objects.create(numero=101,tipo='Doble',precio_noche=Decimal('1250.00'),capacidad=2)
        self.cliente = Cliente.objects.create(nombre='Ana',apellidos='López',correo='ana@example.com',telefono='8110000000')
        self.entrada = timezone.localdate()
        self.salida = self.entrada + timedelta(days=3)

    def reserva(self, entrada=None, salida=None, estado='confirmada'):
        return Reservacion.objects.create(cliente=self.cliente,habitacion=self.habitacion,fecha_entrada=entrada or self.entrada,fecha_salida=salida or self.salida,estado=estado)

    def payload(self, entrada=None, salida=None):
        return {'cliente':self.cliente.pk,'habitacion':self.habitacion.pk,'fecha_entrada':entrada or self.entrada,'fecha_salida':salida or self.salida,'estado':'confirmada'}

    def test_acceso_y_logout(self):
        self.client.logout()
        self.assertRedirects(self.client.get(reverse('reportes:dashboard')), '/cuenta/login/?next=/')
        r=self.client.post(reverse('seguridad:login'),{'username':'prueba','password':'Prueba123456!'})
        self.assertRedirects(r, reverse('reportes:dashboard'))
        self.assertRedirects(self.client.post(reverse('seguridad:logout')),reverse('seguridad:login'))

    def test_paginas(self):
        for url in ['reportes:dashboard','habitaciones:lista','clientes:lista','reservaciones:lista','reservaciones:disponibilidad','reportes:reportes','habitaciones:crear','clientes:crear','reservaciones:crear']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(reverse(url)).status_code, 200)
        self.assertNotEqual(self.client.get('/admin/').status_code, 200)

    def test_habitacion_crud_foto_y_numero_unico(self):
        with TemporaryDirectory() as carpeta, override_settings(MEDIA_ROOT=carpeta):
            b=BytesIO()
            Image.new('RGB',(16,16),'white').save(b,format='PNG')
            foto=SimpleUploadedFile('cuarto.png', b.getvalue(), content_type='image/png')
            datos={'numero':202,'tipo':'Suite','precio_noche':'2000.00','capacidad':4,'disponible':'on','imagen':foto}
            self.assertEqual(self.client.post(reverse('habitaciones:crear'),datos).status_code,302)
            h=Habitacion.objects.get(numero=202)
            self.assertTrue(h.imagen.name)
            self.assertTrue(h.imagen.storage.exists(h.imagen.name))
            self.assertContains(self.client.get(reverse('habitaciones:lista')+'?tipo=Suite'), 'Habitación 202')
            datos.pop('imagen')
            datos['precio_noche']='2100.00'
            self.assertEqual(self.client.post(reverse('habitaciones:editar',args=[h.pk]),datos).status_code,302)
            h.refresh_from_db()
            self.assertEqual(h.precio_noche,Decimal('2100.00'))
            self.assertEqual(self.client.post(reverse('habitaciones:crear'),datos).status_code,200)
            self.assertEqual(Habitacion.objects.filter(numero=202).count(),1)
            self.client.post(reverse('habitaciones:eliminar',args=[h.pk]))
            self.assertFalse(Habitacion.objects.filter(pk=h.pk).exists())

    def test_cliente_crud_correo_unico(self):
        datos={'nombre':'Luis','apellidos':'Pérez','correo':'luis@example.com','telefono':'8120000000'}
        self.assertEqual(self.client.post(reverse('clientes:crear'),datos).status_code,302)
        c=Cliente.objects.get(correo=datos['correo'])
        datos['correo']='ANA@EXAMPLE.COM'
        self.assertContains(self.client.post(reverse('clientes:crear'),datos), 'Este correo ya está registrado.')
        datos['correo']='luis@example.com'
        datos['telefono']='8120000001'
        self.assertEqual(self.client.post(reverse('clientes:editar',args=[c.pk]),datos).status_code,302)
        self.assertContains(self.client.get(reverse('clientes:lista')+'?q=Luis'), 'Luis')
        self.client.post(reverse('clientes:eliminar',args=[c.pk]))
        self.assertFalse(Cliente.objects.filter(pk=c.pk).exists())

    def test_fechas_y_total(self):
        self.assertContains(self.client.post(reverse('reservaciones:crear'),self.payload(salida=self.entrada)), 'La fecha de salida debe ser posterior')
        self.assertEqual(self.client.post(reverse('reservaciones:crear'),self.payload()).status_code,302)
        r=Reservacion.objects.get()
        self.assertEqual(r.total,Decimal('3750.00'))
        self.assertEqual(r.noches,3)

    def test_solapamiento_y_salida_mismo_dia(self):
        self.reserva()
        for inicio,fin in [(self.entrada,self.salida),(self.entrada-timedelta(days=1),self.salida+timedelta(days=1)),(self.entrada+timedelta(days=1),self.salida+timedelta(days=1))]:
            with self.subTest(inicio=inicio,fin=fin):
                self.assertContains(self.client.post(reverse('reservaciones:crear'),self.payload(inicio,fin)), 'No está disponible')
        self.assertEqual(self.client.post(reverse('reservaciones:crear'),self.payload(self.salida,self.salida+timedelta(days=1))).status_code,302)

    def test_editar_y_cancelar_libera(self):
        r=self.reserva()
        self.assertEqual(self.client.post(reverse('reservaciones:editar',args=[r.pk]),self.payload(salida=self.salida+timedelta(days=1))).status_code,302)
        r.refresh_from_db()
        self.assertEqual(r.total,Decimal('5000.00'))
        self.client.post(reverse('reservaciones:cancelar',args=[r.pk]))
        r.refresh_from_db()
        self.assertEqual(r.estado,'cancelada')
        self.assertEqual(self.client.post(reverse('reservaciones:crear'),self.payload()).status_code,302)

    def test_habitacion_activa_no_se_elimina(self):
        self.reserva()
        with self.assertRaises(ValidationError):
            self.habitacion.delete()
        self.assertContains(self.client.post(reverse('habitaciones:eliminar',args=[self.habitacion.pk]),follow=True),'reservaciones activas')
        self.assertTrue(Habitacion.objects.filter(pk=self.habitacion.pk).exists())
        with self.assertRaises(ProtectedError):
            self.cliente.delete()

    def test_disponibilidad_y_reportes(self):
        self.reserva()
        libre=Habitacion.objects.create(numero=301,tipo='Suite',precio_noche=2000,capacidad=4)
        r=self.client.get(reverse('reservaciones:disponibilidad'),{'entrada':self.entrada,'salida':self.salida})
        self.assertContains(r,'Habitación 301')
        self.assertNotContains(r,'Habitación 101')
        self.assertContains(self.client.get(reverse('reportes:dashboard')),'3750.00')
        r=self.client.get(reverse('reportes:reportes'),{'inicio':self.entrada,'fin':self.salida})
        self.assertEqual(r.context['cantidad'],1)
        self.assertEqual(r.context['ingresos'],Decimal('3750.00'))

    def test_fuera_de_servicio(self):
        self.habitacion.disponible=False
        self.habitacion.save()
        self.assertContains(self.client.post(reverse('reservaciones:crear'),self.payload()),'fuera de servicio')
