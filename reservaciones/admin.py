from django.contrib import admin
from .models import Reservacion

@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('cliente','habitacion','fecha_entrada','fecha_salida','estado','total')
    list_filter = ('estado','fecha_entrada')
    search_fields = ('cliente__nombre','cliente__apellidos','habitacion__numero')
    readonly_fields = ('total',)
    def has_delete_permission(self, request, obj=None):
        return False
