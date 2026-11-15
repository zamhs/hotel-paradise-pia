from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .models import Habitacion

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero','tipo','precio_noche','capacidad','disponible')
    list_filter = ('tipo','disponible')
    search_fields = ('numero','tipo')

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def delete_view(self, request, object_id, extra_context=None):
        try:
            return super().delete_view(request, object_id, extra_context)
        except ValidationError as e:
            self.message_user(request, e.messages[0], messages.ERROR)
            return redirect('admin:habitaciones_habitacion_changelist')
