"""
URL configuration for Sistema project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from . import views
from .views import inicio
urlpatterns = [

    path('', inicio.as_view(), name='inicio'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/modificar/<int:pk>/',
         views.modificar_usuario, name='modificar_usuario'),
    path('usuarios/eliminar/<int:pk>/',
         views.eliminar_usuario, name='eliminar_usuario'),
    path('proyectos/nuevo', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/modificar/<int:pk>/',
         views.modificar_proyecto, name='modificar_proyecto'),
    path('proyectos/eliminar/<int:pk>/',
         views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyectos/<int:pk>/',
         views.ver_proyecto, name='ver_proyecto'),
    path('pruebas/crear/', views.crear_prueba, name='crear_prueba'),
    path('pruebas/', views.listar_pruebas, name='listar_pruebas'),
    path('pruebas/<int:pk>/', views.ver_prueba, name='ver_prueba'),
    # path('pruebas/subir_csv/', views.subir_csv, name='subir_csv'),


]
