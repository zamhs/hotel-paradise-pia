from django.shortcuts import render

def formulario(request, form, titulo, regreso, descripcion='Completa los datos requeridos.'):
    for field in form:
        widget = field.field.widget
        if widget.__class__.__name__ == 'CheckboxInput':
            widget.attrs['class'] = 'form-check-input'
        elif widget.__class__.__name__ == 'Select':
            widget.attrs['class'] = 'form-select'
        else:
            widget.attrs['class'] = 'form-control'
    return render(request, 'formulario.html', {'form': form, 'titulo': titulo, 'regreso': regreso, 'descripcion': descripcion})
