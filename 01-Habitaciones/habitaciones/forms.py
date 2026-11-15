from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'precio_noche', 'capacidad', 'disponible', 'imagen']
        labels = {'numero': 'Número', 'precio_noche': 'Precio por noche (MXN)', 'imagen': 'Fotografía'}
