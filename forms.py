from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellidos', 'correo', 'telefono']
        labels = {'telefono': 'Teléfono'}

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        if Cliente.objects.filter(correo__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo
