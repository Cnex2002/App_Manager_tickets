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
from django.conf import settings
from django.contrib import admin
from django.urls import path,  include
from app_ticket import views
from unittest.mock import patch
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('app_ticket/', include('app_ticket.urls')),

    #nuevo
    path('empresa/nuevo/',views.empresa_nueva, name='empresa_nuevo'),
    path('categoria/nuevo/',views.categoria_nueva, name='categoria_nuevo'),
    path('cliente/nuevo/',views.cliente_nueva, name='cliente_nuevo'),
    path('sucursal/nuevo/', views.sucursal_nuevo, name='sucursal_nuevo'),
    path('departamento/nuevo/', views.departamento_nuevo, name='departamento_nuevo'),
    path('ticket/nuevo/', views.ticket_nuevo, name='ticket_nuevo'),
   
    path('evaluacion/nuevo/', views.evaluacion_nueva, name='evaluacion_nueva'),  
    path('soluciontickets/nuevo/<int:id>/', views.solucionticket_nueva, name='solucionticket_nueva'),
    #lista
    path('empresa/', views.lista_empresas, name='lista_empresas'),
    path('categoria/', views.lista_categorias, name='lista_categorias'),
    path('cliente/', views.lista_clientes, name='lista_clientes'),
    path('sucursal/', views.lista_sucursales, name='lista_sucursales'),
    path('departamento/', views.lista_departamentos, name='lista_departamentos'),
    path('ticket/', views.lista_tickets, name='lista_tickets'),
    path('soluciontickets/lista/', views.lista_soluciontickets, name='lista_soluciontickets'),

    path('evaluacion/', views.lista_evaluaciones, name='lista_evaluaciones'),
    #editar
    path('empresa/editar/<int:id>/', views.empresa_editar, name='empresa_editar'),
    path('sucursal/editar/<int:id>/', views.sucursal_editar, name='sucursal_editar'),
    path('departamento/editar/<int:id>/', views.departamento_editar, name='departamento_editar'),
    path('categoria/editar/<int:id>/', views.categoria_editar, name='categoria_editar'),
    path('cliente/editar/<int:id>/', views.cliente_editar, name='cliente_editar'),
    path('ticket/editar/<int:id>/', views.ticket_editar, name='ticket_editar'),
 
    path('evaluacion/editar/<int:id>/', views.evaluacion_editar, name='evaluacion_editar'),
    #eliminar
    path('empresa/eliminar/<int:id>/', views.empresa_eliminar, name='empresa_eliminar'),
    path('sucursal/eliminar/<int:id>/', views.sucursal_eliminar, name='sucursal_eliminar'),
    path('departamento/eliminar/<int:id>/', views.departamento_eliminar, name='departamento_eliminar'),
    path('categoria/eliminar/<int:id>/', views.categoria_eliminar, name='categoria_eliminar'),
    path('cliente/eliminar/<int:id>/', views.cliente_eliminar, name='cliente_eliminar'),
    path('ticket/eliminar/<int:id>/', views.ticket_eliminar, name='ticket_eliminar'),
  
    path('evaluacion/eliminar/<int:id>/', views.evaluacion_eliminar, name='evaluacion_eliminar'),
    #ver
    
    path('soluciontickets/nuevo/<int:id>/', views.solucionticket_nueva, name='solucionticket_nueva'),
  


    path('accounts/', include('allauth.urls')),
    #perfil
    path('accounts/profile/', views.perfil, name='perfil'),
    path('perfil/', views.perfil, name='perfil'),
    #completar registro
    path('usuario/completar_registro/', views.completar_registro, name='completar_registro'),
    path('dashboard/', views.ticket_editar, name='dashboard'),
    #si la url esta vacia que me lleve al login 
    path('', views.perfil, name='perfil'),
     path('reportes/', views.reportes_view, name='reportes'),
     path('generar_reporte_rendimiento_tecnicos_excel/', views.generar_reporte_rendimiento_tecnicos_excel, name='generar_reporte_rendimiento_tecnicos_excel'),
    path('generar_reporte_satisfaccion_cliente_excel/', views.generar_reporte_satisfaccion_cliente_excel, name='generar_reporte_satisfaccion_cliente_excel'),
    path('generar_reporte_clientes_mas_tickets_excel/', views.generar_reporte_clientes_mas_tickets_excel, name='generar_reporte_clientes_mas_tickets_excel'),

   



   # Rutas para la administración de usuarios
    path('usuarios/lista/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/editar/<int:id>/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/eliminar/<int:id>/', views.usuario_eliminar, name='usuario_eliminar'),
     path('usuario/nuevo/', views.usuario_nuevo, name='usuario_nuevo'),
   
    path('perfil/editar/', views.perfil_editar, name='perfil_editar'), # Nueva URL para editar el perfil
     path('perfil/cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('tickets/departamento/', views.ver_tickets_departamento, name='ver_tickets_departamento'),
    path('tecnico/tickets/', views.tecnico_tickets_asignados, name='tecnico_tickets_asignados'),

    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('subir_manual/', views.subir_manual, name='subir_manual'),
    path('manuales/descargar/<int:manual_id>/', views.descargar_manual, name='descargar_manual'),
    path('manuales/eliminar/<int:manual_id>/', views.eliminar_manual, name='eliminar_manual'),

     path('reporte/problemas-soluciones/', views.exportar_problemas_soluciones_pdf, name='reporte_problemas_soluciones'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    
