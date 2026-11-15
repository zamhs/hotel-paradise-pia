from django import forms
from .models import Reservacion

class ReservacionForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = ['cliente', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado']
        labels = {'habitacion': 'Habitación', 'fecha_entrada': 'Fecha de entrada', 'fecha_salida': 'Fecha de salida'}
        widgets = {
            'fecha_entrada': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_salida': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
