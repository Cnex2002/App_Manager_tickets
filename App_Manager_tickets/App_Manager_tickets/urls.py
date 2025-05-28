"""
URL configuration for App_Manager_tickets project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app_ticket import views


urlpatterns = [
    path('admin/', admin.site.urls),
    #nuevo
    path('empresa/nuevo/',views.empresa_nueva, name='empresa_nuevo'),
    path('categoria/nuevo/',views.categoria_nueva, name='categoria_nuevo'),
    path('cliente/nuevo/',views.cliente_nueva, name='cliente_nuevo'),
    path('sucursal/nuevo/', views.sucursal_nuevo, name='sucursal_nuevo'),
    path('departamento/nuevo/', views.departamento_nuevo, name='departamento_nuevo'),
    path('ticket/nuevo/', views.ticket_nuevo, name='ticket_nuevo'),
    path('rol/nuevo/', views.rol_nuevo, name='rol_nuevo'), 
    path('evaluacion/nuevo/', views.evaluacion_nueva, name='evaluacion_nueva'),  
    #lista
    path('empresa/', views.lista_empresas, name='lista_empresas'),
    path('categoria/', views.lista_categorias, name='lista_categorias'),
    path('cliente/', views.lista_clientes, name='lista_clientes'),
    path('sucursal/', views.lista_sucursales, name='lista_sucursales'),
    path('departamento/', views.lista_departamentos, name='lista_departamentos'),
    path('ticket/', views.lista_tickets, name='lista_tickets'),
    path('rol/', views.lista_roles, name='lista_roles'),
    path('evaluacion/', views.lista_evaluaciones, name='lista_evaluaciones'),
    path('soluciontickets/', views.lista_solucionticket, name='lista_soluciontickets'),
    #editar
    path('empresa/editar/<int:id>/', views.empresa_editar, name='empresa_editar'),
    path('sucursal/editar/<int:id>/', views.sucursal_editar, name='sucursal_editar'),
    path('departamento/editar/<int:id>/', views.departamento_editar, name='departamento_editar'),
    path('categoria/editar/<int:id>/', views.categoria_editar, name='categoria_editar'),
    path('cliente/editar/<int:id>/', views.cliente_editar, name='cliente_editar'),
    path('ticket/editar/<int:id>/', views.ticket_editar, name='ticket_editar'),
    path('rol/editar/<int:id>/', views.rol_editar, name='rol_editar'),
    path('evaluacion/editar/<int:id>/', views.evaluacion_editar, name='evaluacion_editar'),

]
