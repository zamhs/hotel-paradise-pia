from django.urls import path
from . import views
app_name = 'habitaciones'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.editar, name='crear'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]
