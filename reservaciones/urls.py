from django.urls import path
from . import views
app_name = 'reservaciones'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.editar, name='crear'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
]
