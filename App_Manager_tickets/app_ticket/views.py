# Reconstructing the views.py content based on previous successful generation
# and then applying the new date filtering logic.

views_content_template = ""

from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
import fitz
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
import json



from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, Sum, Case, When, Value 
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta, date # 
import calendar
import pytz
from django.utils import timezone
from django.shortcuts import render
from django.http import FileResponse, Http404, JsonResponse
from .embeddings import TicketSolutionSearch
searcher = TicketSolutionSearch()
from django.core.files.base import ContentFile
import base64
import openpyxl
from django.http import HttpResponse
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Prefetch
from django.core.mail import send_mail
from django.db.models import Q
# ERORES PYTHON
from django.db.models import ProtectedError
from django.contrib import messages

# Importar Matplotlib
import matplotlib.pyplot as plt
import io
import urllib.parse
import matplotlib.dates as mdates
import base64
import urllib
import numpy as np
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDay  # Añade esta importación

#Importar funciones leer pdfs y descargar
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
from openpyxl import Workbook
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Image,SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

# Configurar el backend de Matplotlib para no usar una GUI
plt.switch_backend('Agg')


# Helper para verificar si el usuario es staff (tiene acceso al admin)
def is_staff_check(user):
    return user.is_staff



def is_admin_check(user):
    if hasattr(user, 'usuario'):
        return user.usuario.rol == 'admin'
    return False

def is_supervisor_check(user):
    if hasattr(user, 'usuario'):
        return user.usuario.rol == 'supervisor'
    return False

def is_atencion_check(user):
    if hasattr(user, 'usuario'):
        return user.usuario.rol == 'atencion'
    return False

def is_tecnico_check(user):
    if hasattr(user, 'usuario'):
        return user.usuario.rol == 'tecnico'
    return False





#profile
@login_required
def perfil(request):
    if hasattr(request.user, 'usuario'):
        usuario_personalizado = request.user.usuario # <--- Añade esta línea
        contexto = {
            'usuario_personalizado': usuario_personalizado # <--- Pasa la variable al contexto
        }
        return render(request, 'perfil.html', contexto)
    else:
        return redirect('completar_registro')
    
    
@login_required
def completar_registro(request):
    if request.method == 'POST':
        formulario = UsuarioForm2(request.POST)
        if formulario.is_valid():
            usuario = formulario.save(commit=False)
            usuario.usuarios = request.user
            usuario.save()
            
            return redirect('perfil')
    else:
        formulario = UsuarioForm2()

    contexto = {
        'formulario': formulario

    }
    return render(request, 'ticket_nuevo.html', contexto)


@login_required
def empresa_nueva(request):
    if request.method == 'POST':
        formulario = EmpresaForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_empresas')
    else:
        formulario = EmpresaForm()

    contexto = {
        'formulario': formulario,
        'titulo': 'Nueva Empresa',
    }
    return render(request, 'ticket_nuevo.html', contexto)



def cliente_nueva(request):
    if request.method == 'POST':
        formulario = clienteForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_clientes')
    else:
        formulario = clienteForm()

    contexto = {
        'formulario': formulario
       
    }
    return render(request, 'ticket_nuevo.html', contexto)

#nuevo usuario



def categoria_nueva(request):
    if request.method == 'POST':
        formulario = CategoriaForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_categorias')
    else:
        formulario = CategoriaForm()

    contexto = {
        'formulario': formulario
       
    }
    return render(request, 'ticket_nuevo.html', contexto)


def sucursal_nuevo(request):
    if request.method == 'POST':
        formulario = SucursalForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_sucursales')
    else:
        formulario = SucursalForm()

    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto)


def departamento_nuevo(request):
    if request.method == 'POST':
        formulario = DepartamentoForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_departamentos')
    else:
        formulario = DepartamentoForm()

    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto)



def ticket_nuevo(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.solicitante = request.user # Asegúrate de que 'solicitante' sea un campo válido en tu modelo Ticket o User
            ticket.save()
            form.save_m2m() # Guarda las relaciones ManyToMany, como la de técnicos (si el técnico fuera ManyToMany)

            # Enviar correo al cliente
            if ticket.cliente and ticket.cliente.correo:
                subject_cliente = f'Nuevo Ticket Creado: {ticket.titulo}'
                html_message_cliente = render_to_string('emails/ticket_creado_cliente.html', {'ticket': ticket})
                plain_message_cliente = strip_tags(html_message_cliente)
                send_mail(subject_cliente, plain_message_cliente, settings.DEFAULT_FROM_EMAIL, [ticket.cliente.correo], html_message=html_message_cliente)

            # Enviar correo al técnico asignado (si hay uno)
            # CORRECCIÓN AQUÍ: Cambiado 'tecnico_asignado' a 'tecnico'
            if ticket.tecnico and ticket.tecnico.usuarios and ticket.tecnico.usuarios.email:
                subject_tecnico = f'Nuevo Ticket Asignado: {ticket.titulo}'
                # Aquí también necesitas acceder al correo electrónico del objeto User asociado al Técnico
                html_message_tecnico = render_to_string('emails/ticket_asignado_tecnico.html', {'ticket': ticket})
                plain_message_tecnico = strip_tags(html_message_tecnico)
                send_mail(subject_tecnico, plain_message_tecnico, settings.DEFAULT_FROM_EMAIL, [ticket.tecnico.usuarios.email], html_message=html_message_tecnico)

            messages.success(request, 'Ticket creado exitosamente y correos enviados.')
            if ticket.solicitante.groups.filter(name='Cliente').exists():
                return redirect('ver_tickets_departamento')
            return redirect('lista_tickets')
    else:
        form = TicketForm()
    return render(request, 'ticket_nuevo1.html', {'formulario': form,'cliente_form': clienteForm(),
    'origen': "nuevo"})









def evaluacion_nueva(request):
    if request.method == 'POST':
        formulario = EvaluacionTecnicoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_evaluaciones')  
    else:
        formulario = EvaluacionTecnicoForm()
    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto)


#lista 
@login_required
def lista_empresas(request):
   
    contexto = {
        'empresas': Empresa.objects.all(),
    }
    return render(request, 'empresa_lista.html', contexto)


@login_required
def lista_clientes(request):
    query = request.GET.get('q')
    clientes_list = Cliente.objects.all().order_by('nombres')

    if query:
        clientes_list = clientes_list.filter(
            Q(nombres__icontains=query) |
            Q(ruc__icontains=query) |
            Q(empresa__icontains=query) # <-- ¡CAMBIO AQUÍ! Eliminado '__nombre'
        ).distinct()

    paginator = Paginator(clientes_list, 10)
    page = request.GET.get('page')

    try:
        clientes = paginator.page(page)
    except PageNotAnInteger:
        clientes = paginator.page(1)
    except EmptyPage:
        clientes = paginator.page(paginator.num_pages)

    context = {
        'clientes': clientes,
        'query': query,
    }
    return render(request, 'cliente_lista.html', context)




def lista_categorias(request):
    query = request.GET.get('q')
    if query:
        categorias_list = Categoria.objects.filter(
            Q(nombre__icontains=query)
        ).order_by('nombre')
    else:
        categorias_list = Categoria.objects.all().order_by('nombre')

    paginator = Paginator(categorias_list, 10)  # Muestra 10 categorías por página
    page = request.GET.get('page')

    try:
        categorias = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        categorias = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), entrega la última página de resultados.
        categorias = paginator.page(paginator.num_pages)

    context = {
        'categorias': categorias,
        'query': query,
    }
    return render(request, 'categoria_lista.html', context)



@login_required
def lista_sucursales(request):
    query = request.GET.get('q')
    sucursales_list = Sucursal.objects.all().order_by('nombre')

    if query:
        sucursales_list = sucursales_list.filter(
            Q(nombre__icontains=query) |
            Q(direccion__icontains=query) |
            Q(empresa__nombre__icontains=query)
        ).distinct()

    paginator = Paginator(sucursales_list, 10)  # 10 sucursales por página
    page = request.GET.get('page')
    try:
        sucursales = paginator.page(page)
    except PageNotAnInteger:
        sucursales = paginator.page(1)
    except EmptyPage:
        sucursales = paginator.page(paginator.num_pages)

    return render(request, 'sucursal_lista.html', {'sucursales': sucursales, 'query': query})


@login_required
def lista_departamentos(request):
    query = request.GET.get('q')
    if query:
        departamentos_list = Departamento.objects.filter(
            Q(nombre__icontains=query) |
            Q(sucursal__nombre__icontains=query) |
            Q(observaciones__icontains=query)
        ).order_by('nombre')
    else:
        departamentos_list = Departamento.objects.all().order_by('nombre')

    paginator = Paginator(departamentos_list, 10)  # Muestra 10 departamentos por página
    page = request.GET.get('page')

    try:
        departamentos = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        departamentos = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), entrega la última página de resultados.
        departamentos = paginator.page(paginator.num_pages)

    context = {
        'departamentos': departamentos,
        'query': query,
    }
    return render(request, 'departamento_lista.html', context)

@login_required
def lista_tickets(request):
    query = request.GET.get('q')
    user = request.user
    tickets = Ticket.objects.all()

    if user.is_superuser:  # Admin ve todos los tickets
        if query:
            tickets = tickets.filter(
                Q(titulo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(cliente__nombres__icontains=query) |
                Q(tecnico__nombre__icontains=query) |
                Q(estado__icontains=query) |
                Q(prioridad__icontains=query)
            )
    else:  # Supervisores y Atención solo ven tickets de su departamento
        try:
            usuario_perfil = Usuario.objects.get(usuarios=user)
            if usuario_perfil.departamento:
                # Filter tickets where the 'tecnico' (Usuario) belongs to the user's department
                tickets = tickets.filter(tecnico__departamento=usuario_perfil.departamento)
                
                if query:
                    tickets = tickets.filter(
                        Q(titulo__icontains=query) |
                        Q(descripcion__icontains=query) |
                        Q(cliente__nombres__icontains=query) |
                        Q(tecnico__nombre__icontains=query) |
                        Q(estado__icontains=query) |
                        Q(prioridad__icontains=query)
                    )
            else:
                messages.warning(request, "Tu usuario no está asociado a un departamento. No puedes ver tickets.")
                tickets = Ticket.objects.none() # No mostrar tickets si no hay departamento
        except Usuario.DoesNotExist:
            messages.error(request, "No se encontró el perfil de usuario. Contacta al administrador.")
            tickets = Ticket.objects.none() # No mostrar tickets si no hay perfil de usuario

    # Ordenar los tickets por fecha de creación descendente (los más recientes primero)
    tickets = tickets.order_by('-fecha_creacion')

    # Configuración de paginación
    paginator = Paginator(tickets, 10)  # Muestra 10 tickets por página
    page = request.GET.get('page')

    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        tickets = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), entrega la última página de resultados.
        tickets = paginator.page(paginator.num_pages)


    context = {
        'tickets': tickets,
        'query': query, # Pasamos el query para que se mantenga en los enlaces de paginación
    }
    return render(request, 'ticket_lista.html', context)



def lista_soluciontickets(request):
    soluciones = SolucionTicket.objects.select_related(
        'ticket__tecnico', 'ticket__cliente', 'ticket__categoria'
    ).prefetch_related(
        'imagenes',
        Prefetch('ticket__evaluacion', queryset=EvaluacionTecnico.objects.all(), to_attr='evaluacion_tecnico')
    ).order_by('-fecha_subida')

    query = request.GET.get('q')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if query:
        soluciones = soluciones.filter(
            Q(ticket__titulo__icontains=query) |
            Q(comentario__icontains=query)
        )

    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            soluciones = soluciones.filter(fecha_subida__gte=fecha_desde_dt)
        except ValueError:
            messages.error(request, "Formato de fecha 'Desde' inválido. Use AAAA-MM-DD.")
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE)) + timedelta(days=1, microseconds=-1)
            soluciones = soluciones.filter(fecha_subida__lte=fecha_hasta_dt)
        except ValueError:
            messages.error(request, "Formato de fecha 'Hasta' inválido. Use AAAA-MM-DD.")

    paginator = Paginator(soluciones, 5)
    page = request.GET.get('page')
    try:
        soluciones_paginadas = paginator.page(page)
    except PageNotAnInteger:
        soluciones_paginadas = paginator.page(1)
    except EmptyPage:
        soluciones_paginadas = paginator.page(paginator.num_pages)

    context = {
        'soluciones': soluciones_paginadas,
        'titulo': 'Lista de Soluciones de Tickets',
        'query': query,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estrellas': range(1, 6),  # Añadir esta línea
    }

    return render(request, 'solucionticket_lista.html', context)







@login_required
def solucionticket_detalle(request, pk):
    solucion = get_object_or_404(SolucionTicket, pk=pk)
    context = {
        'solucion': solucion,
        'titulo': f'Detalles de Solución para Ticket #{solucion.ticket.id}',
    }
    return render(request, 'solucionticket_detalle.html', context)

#ver tickets del departamento

@login_required
def ver_tickets_departamento(request):
    usuario_personalizado = request.user.usuario
    rol_usuario = usuario_personalizado.rol
    
    if rol_usuario in ['atencion', 'supervisor']:
        departamento_usuario = usuario_personalizado.departamento
        if departamento_usuario:
            # Filtra tickets donde el técnico asignado pertenezca al mismo departamento
            tickets = Ticket.objects.filter(tecnico__departamento=departamento_usuario)
        else:
            tickets = Ticket.objects.none() # No hay departamento asignado, no se muestran tickets
    else:
        # Si el rol no es "atencion" ni "supervisor", muestra todos los tickets
        tickets = Ticket.objects.all()
        
    contexto = {
        'tickets': tickets
    }
    return render(request, 'ticket_lista.html', contexto)





@login_required
def lista_evaluaciones(request):
    evaluaciones = EvaluacionTecnico.objects.all().order_by('-fecha_evaluacion')
    
    query = request.GET.get('q')
    if query:
        evaluaciones = evaluaciones.filter(
            Q(ticket__titulo__icontains=query) | # Busca por el título del ticket
            Q(comentario__icontains=query)       # Busca en el comentario de la evaluación
        )
    
    # Paginación
    paginator = Paginator(evaluaciones, 10)  # Muestra 10 evaluaciones por página
    page = request.GET.get('page')

    try:
        evaluaciones = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        evaluaciones = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), entrega la última página de resultados.
        evaluaciones = paginator.page(paginator.num_pages)
    
    context = {
        'evaluaciones': evaluaciones,
        'titulo': 'Lista de Evaluaciones',
        'query': query, # Añade query al contexto para mantener el filtro en la paginación
    }
    return render(request, 'evaluacion_tecnico_lista.html', context)







def empresa_editar(request, id):
    empresa = get_object_or_404(Empresa, id=id)  
    if request.method == 'POST':
        formulario = EmpresaForm(request.POST, instance=empresa)  
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_empresas')  
    else:
        formulario = EmpresaForm(instance=empresa) 
    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto) 

def sucursal_editar(request, id):
    sucursal = get_object_or_404(Sucursal, id=id)
    if request.method == 'POST':
        formulario = SucursalForm(request.POST, instance=sucursal)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_sucursales')
    else:
        formulario = SucursalForm(instance=sucursal)
    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto)  

def departamento_editar(request, id):
    departamento = get_object_or_404(Departamento, id=id)
    if request.method == 'POST':
        formulario = DepartamentoForm(request.POST, instance=departamento)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_departamentos')
    else:
        formulario = DepartamentoForm(instance=departamento)
    contexto = {
        'formulario': formulario
    
    }
    return render(request, 'ticket_nuevo.html', contexto) 

def categoria_editar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        formulario = CategoriaForm(request.POST, instance=categoria)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_categorias')
    else:
        formulario = CategoriaForm(instance=categoria)
    contexto = {
        'formulario': formulario,
        
    }
    return render(request, 'ticket_nuevo.html', contexto) 

def cliente_editar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        formulario = clienteForm(request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_clientes')
    else:
        formulario = clienteForm(instance=cliente)
    contexto = {
        'formulario': formulario
       
    }
    return render(request, 'ticket_nuevo.html', contexto)


def ticket_editar(request, id):
    origen = request.GET.get('origen') or request.POST.get('origen')
    ticket = get_object_or_404(Ticket, id=id)
    
    # Guardar el técnico original antes de procesar el formulario
    tecnico_original = ticket.tecnico 

    if request.method == 'POST':
        # Pasar el request al formulario
        formulario = TicketForm(request.POST, instance=ticket, request=request)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()

            # Enviar correo si el técnico ha cambiado o se ha asignado uno nuevo
            if objeto.tecnico and objeto.tecnico != tecnico_original:
                subject = f'Nuevo Ticket Asignado: {objeto.titulo}'
                # ¡CORRECCIÓN AQUÍ! Cambiado a 'emails/ticket_asignado_tecnico.html'
                message = render_to_string('emails/ticket_asignado_tecnico.html', {
                    'ticket': objeto,
                    'tecnico': objeto.tecnico, 
                })
                from_email = settings.EMAIL_HOST_USER
                
                # Verificación para asegurarse de que el usuario exista y tenga email
                if objeto.tecnico.usuarios and objeto.tecnico.usuarios.email:
                    recipient_list = [objeto.tecnico.usuarios.email]
                    
                    try:
                        send_mail(subject, message, from_email, recipient_list, html_message=message)
                        messages.success(request, f'Ticket actualizado y correo enviado a {objeto.tecnico.usuarios.email}')
                    except Exception as e:
                        messages.error(request, f'Ticket actualizado, pero falló el envío de correo: {e}')
                else:
                    messages.warning(request, f'Ticket actualizado, pero no se pudo enviar correo: el técnico asignado ({objeto.tecnico.nombre}) no tiene un usuario o email asociado.')


            # Redirigir según el origen
            if origen == 'departamento':
                return redirect('tecnico_tickets_asignados')
            else:
                return redirect('lista_tickets') 
    else:
        # Pasar el request al formulario
        formulario = TicketForm(instance=ticket, request=request)

    contexto = {
        'formulario': formulario,
        'origen': origen
    }
    return render(request, 'ticket_nuevo1.html', contexto)




def evaluacion_editar(request, id):
    evaluacion = get_object_or_404(EvaluacionTecnico, id=id) 
    if request.method == 'POST':
        formulario = EvaluacionTecnicoForm(request.POST, instance=evaluacion)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_evaluaciones')  #
    else:
        formulario = EvaluacionTecnicoForm(instance=evaluacion) 
    contexto = {
        'formulario': formulario,
        'titulo': 'Editar Evaluación de Técnico',
    }
    return render(request, 'ticket_nuevo.html', contexto)

#eliminar 
def empresa_eliminar(request, id):
    empresa = get_object_or_404(Empresa, id=id)

    if request.method == 'POST':
        try:
            empresa.delete()
            messages.success(request, 'Empresa eliminada correctamente.')
            return redirect('lista_empresas')  # Redirige a la lista
        except ProtectedError:
            # messages.error(request, 'No se puede eliminar porque hay datos relacionados con esta empresa.')
            messages.error(request, 'No se puede eliminar Empresa por que hay sucursales relacionadas')
            return redirect('lista_empresas')
           
            
    contexto = {
        'objeto': empresa,
        'url_cancelar': reverse('lista_empresas'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

#eliminar
def sucursal_eliminar(request, id):
    sucursal = get_object_or_404(Sucursal, id=id)

    if request.method == 'POST':
        try:
            sucursal.delete()
            messages.success(request, 'Sucursal eliminada correctamente.')
            return redirect('lista_sucursales')  # Redirige a la lista
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Sucursal ya que tiene departamentos')
            return redirect('lista_sucursales') 
        
    contexto = {
        'objeto': sucursal,
        'url_cancelar': reverse('lista_sucursales'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

def departamento_eliminar(request, id):
    departamento = get_object_or_404(Departamento, id=id)

    if request.method == 'POST':
        try:
            departamento.delete()
            messages.success(request, 'Departamento eliminada correctamente.')
            return redirect('lista_departamentos')  # Redirige a la lista
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Departamento ya que tiene usuarios y sucursales')
            return redirect('lista_departamentos') 
    contexto = {
        'objeto': departamento,
        'url_cancelar': reverse('lista_departamentos'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

def categoria_eliminar(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoria eliminada correctamente.')
            return redirect('lista_categorias')  # Redirige a la lista
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Categoria ya que tiene un ticket asignado ')
            return redirect('lista_categorias') 
        
    contexto = {
        'objeto': categoria,
        'url_cancelar': reverse('lista_categorias'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

def cliente_eliminar(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        try:    
            cliente.delete()
            messages.success(request, 'Cliente eliminada correctamente.')
            return redirect('lista_clientes')  # Redirige a la lista
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Cliente ya que tiene un ticket asignado ')
            return redirect('lista_clientes') 

    contexto = {
        'objeto': cliente,
        'url_cancelar': reverse('lista_clientes'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

def ticket_eliminar(request, id):
    origen = request.GET.get('origen') or request.POST.get('origen') 
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == 'POST':
        try:
            ticket.delete()
            messages.success(request, 'Ticket eliminada correctamente.')
            # Redirigir según el origen
            if origen == 'departamento':
                return redirect('ver_tickets_departamento')
            else:
                return redirect('lista_tickets')   
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Ticket ya que tiene un asignado al tecnico')
            return redirect('lista_tickets') 

    contexto = {
    'objeto': ticket,
    'url_cancelar': reverse('ver_tickets_departamento') if origen == 'departamento' else reverse('lista_tickets'),
    'origen': origen
}
    return render(request, 'ticket_eliminar.html', contexto)

def evaluacion_eliminar(request, id):
    evaluacion = get_object_or_404(EvaluacionTecnico, id=id)

    if request.method == 'POST':
        try:
            evaluacion.delete()
            messages.success(request, 'Evaluacion eliminada correctamente.')
            return redirect('lista_evaluaciones')  # Redirige a la lista
        except ProtectedError:
            messages.error(request, 'No se puede eliminar Evaluacion ya que tiene informacion relacionada')
            return redirect('lista_evaluaciones') 

    contexto = {
        'objeto': evaluacion,
        'url_cancelar': reverse('lista_evaluaciones'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

#ver tickets del tenico
def tickets_tecnico(request, ):
  
   return render(request, 'tecnico_ticket.html')

def solucionticket_nueva(request, id):  
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == 'POST':
        formulario = SolucionTicketForm(request.POST, request.FILES)
        if formulario.is_valid():
            solucion = formulario.save(commit=False)
            solucion.ticket = ticket
            solucion.fecha_subida = timezone.now()
            solucion.save()

            # Procesar imágenes subidas
            if 'imagenes' in request.FILES:
                for file in request.FILES.getlist('imagenes'):
                    if file.content_type.startswith('image/'):
                        ImagenSolucion.objects.create(
                            solucion=solucion,
                            imagen=file
                        )

            # Procesar imágenes pegadas (vendrán en request.POST como base64)
            for i in range(1, 5):
                image_data = request.POST.get(f'pasted_image_{i}', '')
                if image_data and image_data.startswith('data:image'):
                    format, imgstr = image_data.split(';base64,') 
                    ext = format.split('/')[-1]
                    file_name = f'pasted_{solucion.id}_{i}.{ext}'
                    
                    data = ContentFile(base64.b64decode(imgstr), name=file_name)
                    ImagenSolucion.objects.create(
                        solucion=solucion,
                        imagen=data
                    )

            # Actualizar estado del ticket
            ticket.estado = 'cerrado'
            ticket.fecha_cierre = timezone.now()
            ticket.save()
            
            messages.success(request, "La solución fue guardada exitosamente.")
            return redirect('lista_soluciontickets')
            
    else:
        formulario = SolucionTicketForm()

    contexto = {
        'formulario': formulario,
        'ticket': ticket
    }
    return render(request, 'solucionticket_nuevo.html', contexto)



# Instancia única para no cargar modelo en cada consulta


def chatbox_view(request):
    return render(request, 'chatbox.html')

# Vista que maneja las consultas enviadas desde el chatbox (POST)
@login_required
def chatbox_query(request):
    if request.method == 'POST':
        pregunta = request.POST.get('pregunta', '')
        if pregunta:
            # CAMBIA esta línea:
            # resultados = searcher.search_solution(pregunta)
            # A esta:
            resultados = searcher.query(pregunta)
            
            respuestas = []
            for r in resultados:
                # Asegurarse de que 'similitud' sea un float estándar de Python
                # Esto ya lo habías hecho y es correcto.
                if 'similitud' in r:
                    r['similitud'] = float(r['similitud']) 
                respuestas.append(r)

            return JsonResponse({'respuestas': respuestas})
        else:
            return JsonResponse({'error': 'No se proporcionó ninguna pregunta.'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)




@login_required
@user_passes_test(is_staff_check)
def usuario_lista(request):
    query = request.GET.get('q')
    
    usuarios_list = Usuario.objects.all().select_related('usuarios', 'departamento').order_by('nombre')

    if query:
        usuarios_list = usuarios_list.filter(
            Q(usuarios__username__icontains=query) |
            Q(nombre__icontains=query) |
            Q(usuarios__email__icontains=query) |
            Q(rol__icontains=query) |
            Q(departamento__nombre__icontains=query)
        ).distinct()

    paginator = Paginator(usuarios_list,10)  # Muestra 10 usuarios por página
    page = request.GET.get('page')

    try:
        usuarios_personalizados = paginator.page(page)
    except PageNotAnInteger:
        usuarios_personalizados = paginator.page(1)
    except EmptyPage:
        usuarios_personalizados = paginator.page(paginator.num_pages)

    contexto = {
        'usuarios': usuarios_personalizados,
        'query': query,
    }
    return render(request, 'usuario_lista.html', contexto)

@login_required
@user_passes_test(is_staff_check)
def usuario_nuevo(request):
    user_form = None # Inicializa para el caso GET

    if request.method == 'POST':
        user_form = UserEditForm(request.POST) # Usa UserEditForm para los campos de User
        usuario_form = UsuarioForm(request.POST) # Usa UsuarioForm para los campos de Usuario

        if user_form.is_valid() and usuario_form.is_valid():
            # Crear el User de Django
            new_user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data['email'],
                first_name=user_form.cleaned_data['first_name'],
                last_name=user_form.cleaned_data['last_name'],
                is_active=user_form.cleaned_data['is_active'],
                is_staff=user_form.cleaned_data['is_staff'],
                is_superuser=user_form.cleaned_data['is_superuser']
            )
            # Allauth generalmente maneja la contraseña, pero si se crea directamente:
            new_user.set_password(User.objects.make_random_password()) # Genera una contraseña aleatoria
            new_user.save()

            # Guardar el Usuario personalizado y vincularlo al User de Django
            usuario = usuario_form.save(commit=False)
            usuario.usuarios = new_user # Asegúrate de que este campo apunte al User de Django
            usuario.save()

            messages.success(request, 'Usuario creado exitosamente. Se ha generado una contraseña aleatoria.')
            return redirect('usuario_lista')
        else:
            messages.error(request, 'Hubo un error al crear el usuario. Por favor, revisa los campos.')
    else:
        user_form = UserEditForm()
        usuario_form = UsuarioForm()

    contexto = {
        'user_form': user_form,
        'usuario_form': usuario_form,
        'titulo': 'Crear Nuevo Usuario'
    }
    # No se usa ticket_nuevo.html directamente aquí porque esperamos dos formularios
    return render(request, 'usuario_form.html', contexto)


@login_required
@user_passes_test(is_staff_check)
def usuario_editar(request, id):
    usuario_personalizado = get_object_or_404(Usuario, id=id)
    user_django = usuario_personalizado.usuarios # Obtener el User de Django asociado

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_django)
        usuario_form = UsuarioForm(request.POST, instance=usuario_personalizado)

        if user_form.is_valid() and usuario_form.is_valid():
            user_form.save() # Guarda los cambios en el User de Django
            usuario_form.save() # Guarda los cambios en el Usuario personalizado
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuario_lista')
        else:
            messages.error(request, 'Hubo un error al actualizar el usuario. Por favor, revisa los campos.')
    else:
        user_form = UserEditForm(instance=user_django)
        usuario_form = UsuarioForm(instance=usuario_personalizado)

    contexto = {
        'user_form': user_form,
        'usuario_form': usuario_form,
        'titulo': f'Editar Usuario: {user_django.username}'
    }
    # Este template necesitará mostrar ambos formularios
    return render(request, 'usuario_form.html', contexto)


@login_required
@user_passes_test(is_staff_check)
def usuario_eliminar(request, id):
    usuario_personalizado = get_object_or_404(Usuario, id=id)
    # También eliminar el User de Django asociado para evitar orfandad
    user_django = usuario_personalizado.usuarios
    if user_django.is_superuser:
        messages.error(request, 'No se puede eliminar un superusuario.')
        return redirect('usuario_lista')
    try:         
        usuario_personalizado.delete()
        user_django.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar usuario por que tiene datos relacionados.')
    return redirect('usuario_lista')


@login_required
def perfil_editar(request):
    usuario_django = request.user
    usuario_personalizado = get_object_or_404(Usuario, usuarios=usuario_django)

    if request.method == 'POST':
        user_form = PerfilUserEditForm(request.POST, instance=usuario_django)
        # *** CAMBIO AQUÍ: Usar PerfilUsuarioEditForm ***
        usuario_form = PerfilUsuarioEditForm(request.POST, instance=usuario_personalizado)

        if user_form.is_valid() and usuario_form.is_valid():
            user_form.save()
            usuario_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Hubo un error al actualizar tu perfil. Por favor, revisa los campos.')
    else:
        user_form = PerfilUserEditForm(instance=usuario_django)
        # *** CAMBIO AQUÍ: Usar PerfilUsuarioEditForm ***
        usuario_form = PerfilUsuarioEditForm(instance=usuario_personalizado)

    contexto = {
        'user_form': user_form,
        'usuario_form': usuario_form,
        'titulo': 'Editar Mi Perfil'
    }
    return render(request, 'perfil_editar.html', contexto)


@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Importante para mantener al usuario logueado
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente!')
            return redirect('perfil')  # Redirige de nuevo a la página de perfil
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'cambiar_contrasena.html', {'form': form})



@login_required
@user_passes_test(is_tecnico_check, login_url='/accounts/login/') # Asegura que solo los técnicos accedan
def tecnico_tickets_asignados(request):
    # Obtener el objeto Usuario personalizado asociado al usuario de Django
    usuario_tecnico = get_object_or_404(Usuario, usuarios=request.user) 
    
    # Obtener todos los tickets asignados a este técnico
    tickets = Ticket.objects.filter(tecnico=usuario_tecnico).order_by('-fecha_creacion')
    
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(cliente_nombres_icontains=query) # Asume que Cliente tiene un campo 'nombres'
        ).distinct()

    context = {
        'tickets': tickets,
        'titulo': 'Mis Tickets Asignados',
        'query': query, # Pasa la consulta al template para mantenerla en el campo de búsqueda
    }
    return render(request, 'tecnico_ticket.html', context)




def buscar_cliente(request):
    query = request.GET.get('q', '')
    
    if query:
        clientes = Cliente.objects.filter(
            Q(nombres__icontains=query) |
            Q(ruc__icontains=query) |
            Q(telefono__icontains=query) |
            Q(correo__icontains=query) |
            Q(anydesk_empresa__icontains=query)
        )
    else:
        clientes = Cliente.objects.none()  # No devolvemos todos para evitar carga innecesaria

    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.id,
            'nombre': cliente.nombres,
            'ruc': cliente.ruc,
            'telefono': cliente.telefono,
            'correo': cliente.correo,
        })


    return JsonResponse({'results': results})





def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto_completo += pagina.get_text()
    return texto_completo



@login_required
def subir_manual(request):
    carpeta_manual = os.path.join(settings.BASE_DIR, 'app_ticket', 'manuales')
    os.makedirs(carpeta_manual, exist_ok=True)

    empresa_actual = request.user.usuario.departamento.sucursal.empresa  # Asumiendo jerarquía Usuario → Departamento → Sucursal → Empresa

    if request.method == 'POST' and request.FILES.getlist('manual'):
        archivos = request.FILES.getlist('manual')
        errores = []
        exitos = []

        for archivo in archivos:
            ext = archivo.name.split('.')[-1].lower()
            nombre_base = ".".join(archivo.name.split('.')[:-1])  # sin extensión

            if ext not in ['pdf', 'docx']:
                errores.append(f"{archivo.name} - formato no permitido")
                continue

            nombre_final = f"{nombre_base}.{ext}"
            ruta_destino = os.path.join(carpeta_manual, nombre_final)
            contador = 1

            while os.path.exists(ruta_destino):
                nombre_final = f"{nombre_base}_{contador}.{ext}"
                ruta_destino = os.path.join(carpeta_manual, nombre_final)
                contador += 1

            with open(ruta_destino, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)

            # Guardar en la BD
            ManualUsuario.objects.create(
                empresa=empresa_actual,
                nombre_archivo=nombre_final,
                ruta_archivo=ruta_destino
            )

            exitos.append(nombre_final)

        if exitos:
            messages.success(request, f"{len(exitos)} archivo(s) subido(s) correctamente.")
        if errores:
            messages.error(request, "Algunos archivos no se subieron: " + ", ".join(errores))

        return redirect('subir_manual')

    # Listar los manuales de la empresa actual
    manuales = ManualUsuario.objects.filter(empresa=empresa_actual)

    return render(request, 'subir_manual.html', {'archivos': manuales})



def descargar_manual(request, manual_id):
    try:
        manual = ManualUsuario.objects.get(id=manual_id)
        return FileResponse(open(manual.ruta_archivo, 'rb'), as_attachment=True, filename=manual.nombre_archivo)
    except (ManualUsuario.DoesNotExist, FileNotFoundError):
        raise Http404("Archivo no encontrado")



def eliminar_manual(request, manual_id):
        try:
            manual = ManualUsuario.objects.get(id=manual_id)
            if os.path.exists(manual.ruta_archivo):
                os.remove(manual.ruta_archivo)
            manual.delete()
            messages.success(request, f"Archivo '{manual.nombre_archivo}' eliminado correctamente.")
        except ManualUsuario.DoesNotExist:
            messages.error(request, "Archivo no encontrado.")
        return redirect('subir_manual')



def exportar_problemas_soluciones_pdf(request):
    soluciones = SolucionTicket.objects.select_related('ticket')

    template_path = 'pdf_problemas_soluciones.html'  # Lo crearemos en el siguiente paso
    context = {'soluciones': soluciones}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="problemas_y_soluciones.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

def tickets_por_tecnico(request):
    tecnico_id = request.GET.get('tecnico_id')
    
    if not tecnico_id:
        return JsonResponse([], safe=False)

    tickets = Ticket.objects.filter(tecnico_id=tecnico_id, estado='abierto')\
        .select_related('categoria', 'cliente')\
        .values(
            'id', 'titulo', 'descripcion', 'prioridad', 'estado', 'fecha_creacion',
            'categoria__nombre',
            'cliente__nombres', 'cliente__ruc', 'cliente__telefono', 'cliente__correo'
        )

    return JsonResponse(list(tickets), safe=False)


def tickets_por_tecnico(request):
    tecnico_id = request.GET.get('tecnico_id')
    
    if not tecnico_id:
        return JsonResponse([], safe=False)

    tickets = Ticket.objects.filter(tecnico_id=tecnico_id, estado='abierto')\
        .select_related('categoria', 'cliente')\
        .values(
            'id', 'titulo', 'descripcion', 'prioridad', 'estado', 'fecha_creacion',
            'categoria__nombre',
            'cliente__nombres', 'cliente__ruc', 'cliente__telefono', 'cliente__correo'
        )

    return JsonResponse(list(tickets), safe=False)


def get_plot_as_base64(plt):
    # Configurar tamaño consistente para todos los gráficos
    plt.figure(figsize=(10, 6))
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return image_base64

# Function to generate a blank image with a message
def get_blank_plot_with_message(message="No hay datos disponibles para generar el gráfico."):
    plt.figure(figsize=(10, 6))
    plt.text(0.5, 0.5, message, horizontalalignment='center', verticalalignment='center', fontsize=12, color='gray')
    plt.axis('off') # Hide axes
    plt.title("Gráfico no disponible")
    return get_plot_as_base64(plt)



def reportes_view(request):
    sucursales = Sucursal.objects.all()
    # Inicialmente, no filtramos por departamento aquí, ya que se carga dinámicamente
    departamentos = Departamento.objects.none()

    # Recuperar los filtros aplicados previamente para mantener la selección
    fecha_inicio_seleccionada = request.GET.get('fecha_inicio')
    fecha_fin_seleccionada = request.GET.get('fecha_fin')
    sucursal_seleccionada = request.GET.get('sucursal')
    departamento_seleccionado = request.GET.get('departamento')

    # Si hay una sucursal seleccionada, cargar los departamentos de esa sucursal
    if sucursal_seleccionada:
        departamentos = Departamento.objects.filter(sucursal__id=sucursal_seleccionada)

    context = {
        'sucursales': sucursales,
        'departamentos': departamentos, # Esto se usará para la carga inicial, luego JS lo actualiza
        'fecha_inicio_seleccionada': fecha_inicio_seleccionada,
        'fecha_fin_seleccionada': fecha_fin_seleccionada,
        'sucursal_seleccionada': sucursal_seleccionada,
        'departamento_seleccionado': departamento_seleccionado,
    }
    return render(request, 'reportes.html', context)






def grafico_evolucion_mensual_tickets(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')

    tickets = Ticket.objects.all()

    if fecha_inicio_str:
        fecha_inicio = parse_date(fecha_inicio_str)
        if fecha_inicio:
            tickets = tickets.filter(fecha_creacion__gte=fecha_inicio)

    if fecha_fin_str:
        fecha_fin = parse_date(fecha_fin_str)
        if fecha_fin:
            tickets = tickets.filter(fecha_creacion__lte=fecha_fin)

    if sucursal_id and sucursal_id != '':
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)

    if departamento_id and departamento_id != '':
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)

    # Agrupar por mes y contar tickets creados
    tickets_por_mes = tickets.annotate(month=TruncMonth('fecha_creacion')).values('month').annotate(count=Count('id')).order_by('month')

    meses = [item['month'].strftime('%Y-%m') for item in tickets_por_mes]
    cantidades = [item['count'] for item in tickets_por_mes]

    plt.figure(figsize=(10, 6))
    plt.plot(meses, cantidades, marker='o', linestyle='-', color='b')
    #plt.title('Evolución Mensual de Tickets Creados')
    plt.xlabel('Mes y Año')
    plt.ylabel('Cantidad de Tickets')
    plt.grid(True)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return JsonResponse({'grafico': grafico_base64})



@login_required
def buscar_departamentos(request):
    sucursal_id = request.GET.get('sucursal_id')
    departamentos_data = []
    if sucursal_id:
        # Asegúrate de que los departamentos sean activos
        departamentos = Departamento.objects.filter(sucursal_id=sucursal_id, estado=True).order_by('nombre')
        for depto in departamentos:
            departamentos_data.append({'id': depto.id, 'nombre': depto.nombre})
    return JsonResponse({'departamentos': departamentos_data})





def _generar_grafico_base64(plt_figure):
    """Función auxiliar para convertir un gráfico de Matplotlib a Base64."""
    buffer = io.BytesIO()
    plt_figure.savefig(buffer, format='png')
    plt.close(plt_figure) # Cierra la figura para liberar memoria
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def _aplicar_filtros_tickets(request, tickets_queryset):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')

    if fecha_inicio_str:
        parsed_date_inicio = parse_date(fecha_inicio_str)
        if parsed_date_inicio:
            # Convertir la fecha de inicio a un datetime consciente de la zona horaria al inicio del día
            start_of_day = timezone.make_aware(
                datetime.combine(parsed_date_inicio, datetime.min.time()),
                timezone.get_current_timezone() # Usa la zona horaria configurada en settings.py
            )
            tickets_queryset = tickets_queryset.filter(fecha_creacion__gte=start_of_day)

    if fecha_fin_str:
        parsed_date_fin = parse_date(fecha_fin_str)
        if parsed_date_fin:
            # Convertir la fecha de fin a un datetime consciente de la zona horaria al final del día
            end_of_day = timezone.make_aware(
                datetime.combine(parsed_date_fin, datetime.max.time()),
                timezone.get_current_timezone()
            )
            tickets_queryset = tickets_queryset.filter(fecha_creacion__lte=end_of_day)

    if sucursal_id and sucursal_id != '':
        tickets_queryset = tickets_queryset.filter(tecnico__departamento__sucursal__id=sucursal_id)

    if departamento_id and departamento_id != '':
        tickets_queryset = tickets_queryset.filter(tecnico__departamento__id=departamento_id)
        
    return tickets_queryset

def grafico_tickets_por_estado(request):
    tickets = Ticket.objects.all()
    tickets = _aplicar_filtros_tickets(request, tickets)

    estado_counts = tickets.values('estado').annotate(count=Count('id')).order_by('estado')

    estados = [item['estado'] for item in estado_counts]
    cantidades = [item['count'] for item in estado_counts]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(estados, cantidades, color=['skyblue', 'lightcoral', 'lightgreen', 'orange'])
    #ax.set_title('Tickets por Estado')
    ax.set_xlabel('Estado')
    ax.set_ylabel('Cantidad de Tickets')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})


def grafico_tickets_por_categoria(request):
    tickets = Ticket.objects.all()
    tickets = _aplicar_filtros_tickets(request, tickets)

    categoria_counts = tickets.values('categoria__nombre').annotate(count=Count('id')).order_by('categoria__nombre')

    categorias = [item['categoria__nombre'] for item in categoria_counts if item['categoria__nombre']]
    cantidades = [item['count'] for item in categoria_counts if item['categoria__nombre']]
    
    if not categorias: # Manejar caso sin datos
        return JsonResponse({'grafico': None, 'message': 'No hay datos para el gráfico de Tickets por Categoría con los filtros aplicados.'})

    # Función para formatear las etiquetas con porcentaje y conteo
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val:d})'
        return my_autopct

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(cantidades, 
           labels=categorias, 
           autopct=make_autopct(cantidades), 
           startangle=90, 
           colors=plt.cm.Paired.colors)
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    #ax.set_title('Tickets por Categoría')
    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})


def grafico_tickets_por_departamento(request):
    tickets = Ticket.objects.all()
    tickets = _aplicar_filtros_tickets(request, tickets)

    # Filtrar solo tickets que tienen un técnico asignado y un departamento asociado
    departamento_counts = tickets.filter(tecnico__departamento__isnull=False) \
                                 .values('tecnico__departamento__nombre') \
                                 .annotate(count=Count('id')) \
                                 .order_by('tecnico__departamento__nombre')

    departamentos = [item['tecnico__departamento__nombre'] for item in departamento_counts if item['tecnico__departamento__nombre']]
    cantidades = [item['count'] for item in departamento_counts if item['tecnico__departamento__nombre']]

    if not departamentos: # Manejar caso sin datos
        return JsonResponse({'grafico': None, 'message': 'No hay datos para el gráfico de Tickets por Departamento con los filtros aplicados.'})

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(departamentos, cantidades, color='teal')
    #ax.set_title('Tickets por Departamento')
    ax.set_xlabel('Departamento')
    ax.set_ylabel('Cantidad de Tickets')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})

def grafico_calificaciones_servicio(request):
    evaluaciones = EvaluacionTecnico.objects.all()

    # Aplicamos los filtros a los tickets asociados a las evaluaciones
    tickets_filtrados = Ticket.objects.all()
    tickets_filtrados = _aplicar_filtros_tickets(request, tickets_filtrados)
    ticket_ids_filtrados = tickets_filtrados.values_list('id', flat=True)

    # Filtramos las evaluaciones que corresponden a esos tickets
    evaluaciones = evaluaciones.filter(ticket__id__in=ticket_ids_filtrados)
    
    # Agrupamos por calificación para el gráfico de barras
    datos_calificaciones = evaluaciones.values('calificacion').annotate(
        total=Count('id')
    ).order_by('calificacion')

    if not datos_calificaciones:
        return JsonResponse({'grafico': None, 'message': 'No hay datos para el gráfico de Calificaciones de Servicio con los filtros aplicados.'})

    # Mapeo de valores numéricos a etiquetas de calificación
    calificacion_map = dict(CALIFICACION_CHOICES)
    
    # Preparar datos para el gráfico de barras horizontales
    calificaciones = []
    cantidades = []
    colores = []
    
    # Definir colores basados en la calificación (mejor calificación = verde, peor = rojo)
    color_map = {
        1: '#ff4d4d',  # Rojo para mala calificación
        2: '#ff9999',  # Rosa claro
        3: '#ffcc99',  # Naranja claro
        4: '#99ccff',  # Azul claro
        5: '#66cc99'   # Verde para buena calificación
    }
    
    for item in datos_calificaciones:
        calificacion = item['calificacion']
        calificaciones.append(calificacion_map.get(calificacion, f'Desconocido ({calificacion})'))
        cantidades.append(item['total'])
        colores.append(color_map.get(calificacion, '#999999'))  # Gris por defecto

    # Crear el gráfico de barras horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Crear las barras horizontales
    bars = ax.barh(
        calificaciones, 
        cantidades,
        color=colores,
        height=0.6  # Controla el grosor de las barras
    )
    
    # Añadir etiquetas con los valores
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.5,  # Posición x (un poco más allá del final de la barra)
            bar.get_y() + bar.get_height()/2,  # Posición y (centrada verticalmente)
            f'{int(width)}',  # Texto (valor)
            va='center',  # Alineación vertical
            ha='left',    # Alineación horizontal
            fontsize=10
        )

    # Formatear el gráfico
    #ax.set_title('Distribución de Calificaciones de Servicio')
    ax.set_xlabel('Cantidad de Evaluaciones')
    ax.set_ylabel('Calificación')
    ax.grid(True, linestyle='--', alpha=0.6, axis='x')  # Solo líneas de grid horizontales
    
    # Ajustar márgenes y layout
    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})

def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto_completo += pagina.get_text()
    return texto_completo

@login_required
def reportes_tecnico(request):
    tecnico_actual = request.user.usuario # Asumiendo que el User de Django tiene un OneToOneField a tu modelo Usuario

    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.filter(tecnico=tecnico_actual)

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_creacion__gte=fecha_inicio)
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido. Use YYYY-MM-DD.")
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_creacion__lte=fecha_fin)
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido. Use YYYY-MM-DD.")

    context = {
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str,
    }
    
    return render(request, 'reportes_tecnico.html', context)


@login_required
def grafico_tickets_por_estado_tecnico(request):
    tecnico_actual = request.user.usuario # Asumiendo que el User de Django tiene un OneToOneField a tu modelo Usuario
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.filter(tecnico=tecnico_actual)

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_creacion__gte=fecha_inicio)
        except ValueError:
            pass # Ya se manejó en reportes_tecnico, o se puede agregar un mensaje específico aquí si se desea
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_creacion__lte=fecha_fin)
        except ValueError:
            pass # Idem

    # Agrupar por estado y contar
    tickets_por_estado = tickets.values('estado').annotate(count=Count('id')).order_by('estado')

    estados = [item['estado'] for item in tickets_por_estado]
    cantidades = [item['count'] for item in tickets_por_estado]

    # Mapear estados a nombres más legibles si es necesario (ej. 'AB' -> 'Abierto')
    mapeo_estados = dict(Ticket.ESTADO_CHOICES) # Asumiendo que tienes ESTADO_CHOICES en tu modelo Ticket
    nombres_estados = [mapeo_estados.get(estado, estado) for estado in estados]

    # Generar gráfico de dona
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Colores para los estados
    colores = {
        'abierto': "#A07049",  # Light Peach
        'en proceso': '#AEC6CF', # Light Blue-Gray
        'cerrado': "#236B23",  # Pastel Green
        # Agrega más colores si tienes más estados
    }
    
    # Asignar colores basados en los estados presentes
    colores_grafico = [colores.get(estado, '#CCCCCC') for estado in estados] # Color por defecto si no está en el mapeo

    def func(pct, allvals):
        absolute = int(pct/100.*sum(allvals))
        return f"{pct:.1f}%\n({absolute})" # Formato: Porcentaje%\n(Cantidad)

    # Crear el gráfico de dona
    wedges, texts, autotexts = ax.pie(
        cantidades, 
        labels=nombres_estados, 
        autopct=lambda pct: func(pct, cantidades), # Usamos nuestra función personalizada
        startangle=90, 
        pctdistance=0.85, # Distancia de los porcentajes del centro
        colors=colores_grafico,
        wedgeprops=dict(width=0.3) # Para hacer la dona (donut)
    )

    # Ajustar el texto de los porcentajes
    for autotext in autotexts:
        autotext.set_color('white') 
        autotext.set_fontsize(10)
        autotext.set_weight('bold')

    # Ajustar el texto de las etiquetas (estados)
    for text in texts:
        text.set_fontsize(10)
        text.set_color('black') 
        text.set_weight('bold')

    #ax.set_title('Tickets por Estado', fontsize=14, fontweight='bold', pad=20)
    ax.axis('equal')  # Asegura que el gráfico sea un círculo.

    # Guardar el gráfico en un buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig) # Cierra la figura para liberar memoria

    return JsonResponse({'image': uri})


@login_required
def grafico_tickets_por_prioridad_tecnico(request):
    tecnico_actual = request.user.usuario
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.filter(tecnico=tecnico_actual)

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_creacion__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() + timedelta(days=1) - timedelta(seconds=1)
            tickets = tickets.filter(fecha_creacion__lte=fecha_fin)
        except ValueError:
            pass

    # Agrupar solo por prioridad y contar
    tickets_por_prioridad = tickets.values('prioridad').annotate(count=Count('id')).order_by('prioridad')

    # Definir el orden deseado de las prioridades para el gráfico
    orden_prioridad = ['baja', 'media', 'alta']
    
    # Inicializar las cantidades para todas las prioridades en el orden definido
    prioridades = []
    cantidades = []
    
    # Crear un diccionario temporal para un acceso rápido
    temp_data = {item['prioridad']: item['count'] for item in tickets_por_prioridad}

    for p in orden_prioridad:
        prioridades.append(p)
        cantidades.append(temp_data.get(p, 0)) # Usar .get para manejar prioridades sin tickets

    # Mapear prioridades a nombres más legibles
    mapeo_prioridades = dict(Ticket.PRIORIDAD_CHOICES)
    nombres_prioridades = [mapeo_prioridades.get(p, p.title()) for p in prioridades]

    # Generar gráfico de barras simple
    fig, ax = plt.subplots(figsize=(10, 7))

    bar_width = 0.6
    indices = range(len(prioridades))

    # Colores para las barras (puedes ajustar estos)
    colores_barras = {
        'baja': '#ADD8E6',  # Light Blue
        'media': '#FFD700', # Gold
        'alta': '#FF6347',  # Tomato
    }
    
    # Asignar colores a las barras según su prioridad
    colores_grafico = [colores_barras.get(p, '#CCCCCC') for p in prioridades]

    bars = ax.bar(indices, cantidades, bar_width, color=colores_grafico)

    # Añadir los números sobre las barras
    for bar in bars:
        height = bar.get_height()
        if height > 0: # Solo si la barra tiene un valor
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, color='gray') # Ajusta el +0.5 para el espacio

    ax.set_xlabel('Prioridad', fontsize=12)
    ax.set_ylabel('Cantidad de Tickets', fontsize=12)
    #ax.set_title('Tickets por Prioridad', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(indices)
    ax.set_xticklabels(nombres_prioridades, rotation=0, ha='center', fontsize=10)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7) # Cuadrícula en el eje Y

    plt.tight_layout()

    # Guardar el gráfico en un buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig) # Cierra la figura para liberar memoria

    return JsonResponse({'image': uri})


@login_required
def grafico_productividad_tecnico(request):
    tecnico_actual = request.user.usuario
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets_resueltos = Ticket.objects.filter(
        tecnico=tecnico_actual,
        estado='cerrado', # Solo tickets cerrados
        fecha_cierre__isnull=False # Asegurarse de que tengan una fecha de cierre
    )

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            tickets_resueltos = tickets_resueltos.filter(fecha_cierre__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() + timedelta(days=1) - timedelta(seconds=1)
            tickets_resueltos = tickets_resueltos.filter(fecha_cierre__lte=fecha_fin)
        except ValueError:
            pass
    
    # Determinar la granularidad del eje X: mensual o diaria
    # Si el rango es de 60 días o menos, se muestra por día, sino por mes
    if fecha_inicio_str and fecha_fin_str:
        start_date = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d').date() # Usamos la fecha original para el cálculo de días
        delta = end_date - start_date
        if delta.days <= 60: # Menos de dos meses, mostrar por día
            trunc_func = TruncDay('fecha_cierre')
            date_format = '%Y-%m-%d' # Formato para días
            xlabel = 'Fecha de Cierre (Día)'
        else: # Más de dos meses, mostrar por mes
            trunc_func = TruncMonth('fecha_cierre')
            date_format = '%Y-%m' # Formato para meses
            xlabel = 'Fecha de Cierre (Mes)'
    else: # Sin filtros de fecha, por defecto mostrar por mes
        trunc_func = TruncMonth('fecha_cierre')
        date_format = '%Y-%m'
        xlabel = 'Fecha de Cierre (Mes)'


    # Agrupar por el período truncado y contar
    productividad_por_periodo = tickets_resueltos.annotate(
        periodo=trunc_func
    ).values('periodo').annotate(
        count=Count('id')
    ).order_by('periodo')

    fechas = [item['periodo'] for item in productividad_por_periodo]
    cantidades = [item['count'] for item in productividad_por_periodo]

    # Convertir las fechas a formato Matplotlib (si son objetos datetime)
    fechas_mpl = mdates.date2num(fechas)

    fig, ax = plt.subplots(figsize=(12, 6)) # Un poco más ancho para la línea

    ax.plot(fechas_mpl, cantidades, marker='o', linestyle='-', color='#007bff', linewidth=2) # Línea azul

    # Formatear el eje X
    if trunc_func == TruncDay('fecha_cierre'):
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5)) # Mostrar cada 5 días
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right') # Rotar etiquetas para mejor lectura

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Tickets Resueltos', fontsize=12)
    #ax.set_title('Productividad: Tickets Resueltos por Período', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Asegurarse de que el eje Y empiece en 0 y sea un número entero
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))


    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)

    return JsonResponse({'image': uri})


@login_required
def grafico_calificaciones_recibidas_tecnico(request):
    tecnico_actual = request.user.usuario
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    evaluaciones = EvaluacionTecnico.objects.filter(
        ticket__tecnico=tecnico_actual,
        calificacion__isnull=False
    )

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            evaluaciones = evaluaciones.filter(fecha_evaluacion__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() + timedelta(days=1) - timedelta(seconds=1)
            evaluaciones = evaluaciones.filter(fecha_evaluacion__lte=fecha_fin)
        except ValueError:
            pass

    calificaciones_count = evaluaciones.values('calificacion').annotate(count=Count('id')).order_by('calificacion')

    calificaciones_posibles = [1, 2, 3, 4, 5]
    cantidades = [0] * len(calificaciones_posibles)
    
    for item in calificaciones_count:
        try:
            index = calificaciones_posibles.index(item['calificacion'])
            cantidades[index] = item['count']
        except ValueError:
            pass

    # --- MODIFICACIÓN AQUÍ: Ya no se usa EvaluacionTecnico.CALIFICACION_CHOICES ---
    mapeo_calificaciones = dict(CALIFICACION_CHOICES) # Usamos la constante CALIFICACION_CHOICES directamente
    # --- FIN DE MODIFICACIÓN ---

    nombres_calificaciones = [f"{cal} ({mapeo_calificaciones.get(cal, str(cal))})" for cal in calificaciones_posibles]

    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = range(len(calificaciones_posibles))

    colores_barras = {
        1: '#FF6347',
        2: '#FFD700',
        3: '#AEC6CF',
        4: '#90EE90',
        5: '#20B2AA',
    }
    
    colores_grafico = [colores_barras.get(cal, '#CCCCCC') for cal in calificaciones_posibles]

    bars = ax.barh(y_pos, cantidades, color=colores_grafico)

    for i, bar in enumerate(bars):
        width = bar.get_width()
        if width > 0:
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                    ha='left', va='center', fontsize=10, color='gray')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(nombres_calificaciones, fontsize=10)
    ax.set_xlabel('Cantidad de Evaluaciones', fontsize=12)
    ax.set_ylabel('Calificación', fontsize=12)
    #ax.set_title('Distribución de Calificaciones Recibidas', fontsize=14, fontweight='bold', pad=20)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    
    ax.set_xlim(left=0)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)

    return JsonResponse({'image': uri})

def grafico_calificacion_promedio_tecnico(request):
    tickets = Ticket.objects.all()
    tickets = _aplicar_filtros_tickets(request, tickets)

    # Obtener las evaluaciones de los tickets filtrados
    evaluaciones = EvaluacionTecnico.objects.filter(ticket__in=tickets)

    # Agrupar por técnico y calcular promedio de calificación
    calificaciones_por_tecnico = evaluaciones.values(
        'ticket__tecnico__nombre',
        'ticket__tecnico__id'
    ).annotate(
        promedio=Avg('calificacion'),
        cantidad=Count('id')
    ).order_by('-promedio')

    if not calificaciones_por_tecnico:
        return JsonResponse({'grafico': None, 'message': 'No hay datos para generar el gráfico de Calificación Promedio por Técnico con los filtros aplicados.'})

    tecnicos = [f"{item['ticket__tecnico__nombre']} ({item['cantidad']})" for item in calificaciones_por_tecnico]
    promedios = [float(item['promedio']) for item in calificaciones_por_tecnico]

    # Crear gráfico de barras horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Crear un gradiente de colores basado en el promedio
    colors = plt.cm.viridis([p/5 for p in promedios])  # Normalizado a 0-1 (ya que las calificaciones son 1-5)
    
    bars = ax.barh(tecnicos, promedios, color=colors)
    
    # Añadir etiquetas con los valores
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, 
                bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}', 
                ha='left', 
                va='center',
                fontsize=10)

    #ax.set_title('Calificación Promedio por Técnico')
    ax.set_xlabel('Calificación Promedio (1-5)')
    ax.set_ylabel('Técnico (N° evaluaciones)')
    ax.set_xlim(0, 5.5)  # El máximo es 5
    ax.grid(True, linestyle='--', alpha=0.6, axis='x')
    
    # Añadir barra de color para indicar la escala
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=1, vmax=5))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Escala de Calificación')

    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})

def grafico_ranking_tecnicos(request):
    tickets = Ticket.objects.filter(estado='cerrado')
    tickets = _aplicar_filtros_tickets(request, tickets)

    # Agrupar por técnico y contar tickets cerrados
    ranking_tecnicos = tickets.values(
        'tecnico__nombre',
        'tecnico__id'
    ).annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')[:10]  # Limitar a los 10 primeros

    if not ranking_tecnicos:
        return JsonResponse({'grafico': None, 'message': 'No hay datos para generar el Ranking de Técnicos con los filtros aplicados.'})

    tecnicos = [item['tecnico__nombre'] for item in ranking_tecnicos]
    cantidades = [item['cantidad'] for item in ranking_tecnicos]

    # Crear gráfico de barras horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colores para el ranking (degradado de verde)
    colors = plt.cm.Greens(np.linspace(0.4, 1, len(tecnicos)))
    
    bars = ax.barh(tecnicos, cantidades, color=colors)
    
    # Añadir etiquetas con los valores
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', 
                va='center',
                fontsize=10)

    #ax.set_title('Ranking de Técnicos (Tickets Cerrados)')
    ax.set_xlabel('Cantidad de Tickets Cerrados')
    ax.set_ylabel('Técnico')
    ax.grid(True, linestyle='--', alpha=0.6, axis='x')
    
    # Invertir el orden para que el primero quede arriba
    ax.invert_yaxis()

    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})

def grafico_tickets_por_cliente(request):
    tickets = Ticket.objects.all()
    tickets = _aplicar_filtros_tickets(request, tickets)

    # Agrupar por cliente y contar tickets, excluyendo tickets sin cliente
    tickets_por_cliente = tickets.exclude(cliente__isnull=True).values(
        'cliente__nombres',
        'cliente__empresa',
        'cliente__id'
    ).annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')[:10]  # Limitar a los 10 primeros

    if not tickets_por_cliente:
        return JsonResponse({'grafico': None, 'message': 'No hay datos para generar el gráfico de Tickets por Cliente con los filtros aplicados.'})

    # Crear etiquetas que incluyan nombre y empresa si está disponible
    clientes = []
    for item in tickets_por_cliente:
        nombre = item['cliente__nombres'] or 'Cliente sin nombre'
        empresa = item['cliente__empresa']
        if empresa:
            clientes.append(f"{nombre} ({empresa})")
        else:
            clientes.append(nombre)
    
    cantidades = [item['cantidad'] for item in tickets_por_cliente]

    # Crear gráfico de barras horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colores para el gráfico (escala de azules)
    colors = plt.cm.Blues(np.linspace(0.4, 1, len(clientes)))
    
    bars = ax.barh(clientes, cantidades, color=colors)
    
    # Añadir etiquetas con los valores
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', 
                va='center',
                fontsize=10)

    #ax.set_title('Clientes con más Tickets')
    ax.set_xlabel('Cantidad de Tickets')
    ax.set_ylabel('Cliente')
    ax.grid(True, linestyle='--', alpha=0.6, axis='x')
    
    # Invertir el orden para que el primero quede arriba
    ax.invert_yaxis()

    plt.tight_layout()

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({'grafico': grafico_base64})

def grafico_cumplimiento_sla(request):
    tickets = Ticket.objects.filter(estado='cerrado', fecha_cierre__isnull=False)
    tickets = _aplicar_filtros_tickets(request, tickets)

    # Definir los SLAs según prioridad (en horas)
    sla_horas = {
        'baja': 72,
        'media': 24,
        'alta': 4
    }

    # Calcular cumplimiento y tiempos promedio
    dentro_sla = 0
    fuera_sla = 0
    tiempos_por_prioridad = {
        'alta': {'dentro': [], 'fuera': []},
        'media': {'dentro': [], 'fuera': []},
        'baja': {'dentro': [], 'fuera': []}
    }

    for ticket in tickets:
        tiempo_resolucion = (ticket.fecha_cierre - ticket.fecha_creacion).total_seconds() / 3600  # en horas
        sla_esperado = sla_horas.get(ticket.prioridad, 72)  # default 72h si no encuentra prioridad
        
        if tiempo_resolucion <= sla_esperado:
            dentro_sla += 1
            tiempos_por_prioridad[ticket.prioridad]['dentro'].append(tiempo_resolucion)
        else:
            fuera_sla += 1
            tiempos_por_prioridad[ticket.prioridad]['fuera'].append(tiempo_resolucion)

    total_tickets = dentro_sla + fuera_sla

    if total_tickets == 0:
        return JsonResponse({'grafico': None, 'message': 'No hay tickets cerrados con los filtros aplicados.'})

    # Calcular tiempos promedio por prioridad para tickets dentro del SLA
    tiempos_promedio = {}
    for prioridad in ['alta', 'media', 'baja']:
        tiempos = tiempos_por_prioridad[prioridad]['dentro']
        if tiempos:
            avg_horas = sum(tiempos) / len(tiempos)
            horas = int(avg_horas)
            minutos = int((avg_horas - horas) * 60)
            tiempos_promedio[prioridad] = f"{horas}h {minutos}min"
        else:
            tiempos_promedio[prioridad] = "Sin datos"

    # Crear figura más grande para mejor visualización
    fig = plt.figure(figsize=(12, 12))  # Aumenté el tamaño de la figura
    ax = fig.add_subplot(111)
    
    # Preparar datos para el gráfico
    labels = ['Dentro del SLA', 'Fuera del SLA']
    sizes = [dentro_sla, fuera_sla]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)  # resaltar la primera porción

    # Función para formatear las etiquetas con porcentaje y conteo
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val:d})'
        return my_autopct

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct=make_autopct(sizes),
        shadow=True,
        startangle=90,
        textprops={'fontsize': 14}  # Aumenté el tamaño de fuente aquí
    )

    # Ajustar estilo de los textos
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.axis('equal')
    #ax.set_title('Cumplimiento de SLA por Prioridad', fontsize=16, pad=20)  # Aumenté el tamaño de fuente

    # Añadir leyenda con fuente más grande
    ax.legend(
        wedges,
        [f"{l} - {s} ({100*s/total_tickets:.1f}%)" for l, s in zip(labels, sizes)],
        title="Detalle",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=12  # Aumenté el tamaño de fuente de la leyenda
    )
    
    # Añadir texto con los tiempos promedio (con fuente más grande)
    texto_tiempos = (
        "Tiempo promedio de resolución dentro del SLA:\n"
        f"Alta: {tiempos_promedio['alta']}\n"
        f"Media: {tiempos_promedio['media']}\n"
        f"Baja: {tiempos_promedio['baja']}"
    )
    
    plt.figtext(
        0.5, 0.05, 
        texto_tiempos,
        ha='center',
        fontsize=14,  # Aumenté el tamaño de fuente aquí (era 12)
        bbox={
            'facecolor': 'white', 
            'alpha': 0.8, 
            'pad': 10,  # Aumenté el padding
            'boxstyle': 'round,pad=0.5'
        }
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Ajusté el espacio para el texto

    grafico_base64 = _generar_grafico_base64(fig)
    return JsonResponse({
        'grafico': grafico_base64,
        'texto_tiempos': texto_tiempos
    })

@login_required
def grafico_cumplimiento_sla_tecnico(request):
    tecnico_actual = request.user.usuario
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.filter(
        tecnico=tecnico_actual,
        estado='cerrado', 
        fecha_cierre__isnull=False
    )

    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_cierre__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() + timedelta(days=1) - timedelta(seconds=1)
            tickets = tickets.filter(fecha_cierre__lte=fecha_fin)
        except ValueError:
            pass

    # Definir los SLAs según prioridad (en horas)
    sla_horas = {
        'baja': 72,
        'media': 24,
        'alta': 4
    }

    # Calcular cumplimiento
    dentro_sla = 0
    fuera_sla = 0
    tiempos_por_prioridad = {
        'alta': {'dentro': [], 'fuera': []},
        'media': {'dentro': [], 'fuera': []},
        'baja': {'dentro': [], 'fuera': []}
    }

    for ticket in tickets:
        tiempo_resolucion = (ticket.fecha_cierre - ticket.fecha_creacion).total_seconds() / 3600  # en horas
        sla_esperado = sla_horas.get(ticket.prioridad, 72)  # default 72h si no encuentra prioridad
        
        if tiempo_resolucion <= sla_esperado:
            dentro_sla += 1
            tiempos_por_prioridad[ticket.prioridad]['dentro'].append(tiempo_resolucion)
        else:
            fuera_sla += 1
            tiempos_por_prioridad[ticket.prioridad]['fuera'].append(tiempo_resolucion)

    total_tickets = dentro_sla + fuera_sla

    if total_tickets == 0:
        return JsonResponse({'grafico': None, 'message': 'No hay tickets cerrados con los filtros aplicados.'})

    # Calcular tiempos promedio por prioridad para tickets dentro del SLA
    tiempos_promedio = {}
    for prioridad in ['alta', 'media', 'baja']:
        tiempos = tiempos_por_prioridad[prioridad]['dentro']
        if tiempos:
            avg_horas = sum(tiempos) / len(tiempos)
            horas = int(avg_horas)
            minutos = int((avg_horas - horas) * 60)
            tiempos_promedio[prioridad] = f"{horas}h {minutos}min"
        else:
            tiempos_promedio[prioridad] = "Sin datos"

    # Crear figura
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    # Preparar datos para el gráfico
    labels = ['Dentro del SLA', 'Fuera del SLA']
    sizes = [dentro_sla, fuera_sla]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)  # resaltar la primera porción

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val:d})'
        return my_autopct

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct=make_autopct(sizes),
        shadow=True,
        startangle=90
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.axis('equal')
    #ax.set_title('Cumplimiento de SLA por Prioridad', fontsize=14, pad=20)

    # Añadir texto con los tiempos promedio
    texto_tiempos = (
        "Tiempo promedio de resolución dentro del SLA:\n"
        f"Alta: {tiempos_promedio['alta']}\n"
        f"Media: {tiempos_promedio['media']}\n"
        f"Baja: {tiempos_promedio['baja']}"
    )
    
    plt.figtext(
        0.5, 0.05, 
        texto_tiempos,
        ha='center',
        fontsize=12,
        bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5}
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)

    return JsonResponse({'image': uri})






def exportar_tickets_por_categoria_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.all()

    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Generar el gráfico
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_tickets_por_categoria(req)
    
    # Obtener los datos del JsonResponse
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_tickets_por_categoria.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title = Paragraph("Reporte de Tickets por Categoría", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("Filtros aplicados: " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Tickets por Categoría</b>", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Preparar los datos para la tabla
    data = []
    # Encabezados de la tabla
    data.append([
        "ID Ticket", 
        "Título", 
        "Categoría", 
        "Prioridad", 
        "Fecha Creación", 
        "Fecha Cierre", 
        "Técnico Asignado"
    ])

    for ticket in tickets.order_by('id'):
        tecnico_asignado = ticket.tecnico.usuarios.username if ticket.tecnico and ticket.tecnico.usuarios else "N/A"
        fecha_cierre = ticket.fecha_cierre.strftime('%Y-%m-%d') if ticket.fecha_cierre else "N/A"
        data.append([
            str(ticket.id),
            ticket.titulo,
            ticket.categoria.nombre if ticket.categoria else "N/A",
            ticket.get_prioridad_display(),
            ticket.fecha_creacion.strftime('%Y-%m-%d'),
            fecha_cierre,
            tecnico_asignado
        ])

    # Crear la tabla
    table = Table(data, repeatRows=1)  # repeatRows=1 para repetir los encabezados en cada página

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),  # Azul corporativo
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),  # Fondo azul claro
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle de Tickets</b>", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets", 
        styles['Italic']
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def exportar_distribucion_estado_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.all().select_related('cliente', 'tecnico', 'categoria')

    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Generar el gráfico de distribución por estado
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_tickets_por_estado(req)
    
    # Obtener los datos del JsonResponse
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_distribucion_estado.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title = Paragraph("Distribución por Estado del Ticket", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("Filtros aplicados: " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Distribución de Tickets por Estado</b>", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Preparar los datos para la tabla con manejo de texto largo
    data = []
    # Encabezados de la tabla (textos más cortos)
    data.append([
        "ID",
        "Título del Ticket", 
        "Estado",
        "Prioridad", 
        "F. Creación", 
        "F. Cierre", 
        "Cliente",
        "Técnico"
    ])

    # Función para ajustar texto largo
    def ajustar_texto(texto, max_caracteres=20):
        if len(str(texto)) <= max_caracteres:
            return str(texto)
        palabras = str(texto).split()
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            if len(linea_actual + palabra) <= max_caracteres:
                linea_actual += palabra + " "
            else:
                lineas.append(linea_actual)
                linea_actual = palabra + " "
        lineas.append(linea_actual)
        return "\n".join(lineas)

    for ticket in tickets.order_by('estado', '-fecha_creacion'):
        tecnico_asignado = ticket.tecnico.nombre if ticket.tecnico else "Sin asignar"
        cliente_nombre = ticket.cliente.nombres if ticket.cliente else "Sin cliente"
        fecha_cierre = ticket.fecha_cierre.strftime('%Y-%m-%d') if ticket.fecha_cierre else "N/A"
        
        data.append([
            str(ticket.id),
            ajustar_texto(ticket.titulo, 25),  # 25 caracteres por línea para título
            ticket.get_estado_display(),
            ticket.get_prioridad_display(),
            ticket.fecha_creacion.strftime('%Y-%m-%d'),
            fecha_cierre,
            ajustar_texto(cliente_nombre, 15),  # 15 caracteres para cliente
            ajustar_texto(tecnico_asignado, 15) # 15 caracteres para técnico
        ])

    # Definir anchos de columna optimizados
    col_widths = [
        0.5*inch,   # ID
        1.6*inch,   # Título (ligeramente reducido)
        0.7*inch,   # Estado
        0.7*inch,   # Prioridad
        0.8*inch,   # F. Creación
        0.8*inch,   # F. Cierre
        1.0*inch,   # Cliente
        1.0*inch    # Técnico
    ]

    # Crear la tabla con manejo de texto multilínea
    table = Table(data, repeatRows=1, colWidths=col_widths)

    # Estilo optimizado para texto largo
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEADING', (0, 0), (-1, -1), 10),  # Espacio entre líneas
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Título alineado a la izquierda
        ('TEXTCOLOR', (2, 1), (2, -1), 
            lambda r, c, v: 
                colors.red if data[r][2] == 'Abierto' else 
                colors.blue if data[r][2] == 'En Proceso' else 
                colors.green),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#D9E1F2'), colors.white]),
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle de Tickets por Estado</b>", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(table)

    # Estadísticas resumidas
    total_tickets = tickets.count()
    tickets_abiertos = tickets.filter(estado='abierto').count()
    tickets_proceso = tickets.filter(estado='en proceso').count()
    tickets_cerrados = tickets.filter(estado='cerrado').count()


    # Pie de página
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets", 
        styles['Italic']
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def exportar_tendencia_mensual_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query
    tickets = Ticket.objects.all().select_related('tecnico', 'cliente')

    # Aplicar filtros
    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Generar el gráfico de tendencia mensual
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_evolucion_mensual_tickets(req)
    
    # Obtener los datos del JsonResponse
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_tendencia_mensual.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title_style = styles['Title']
    title_style.fontSize = 16
    title_style.spaceAfter = 12
    title = Paragraph("Tendencia Mensual de Creación de Tickets", title_style)
    story.append(title)

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"<b>Desde:</b> {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"<b>Hasta:</b> {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"<b>Sucursal:</b> {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("<b>Sucursal:</b> No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"<b>Departamento:</b> {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("<b>Departamento:</b> No encontrado")

    if filtros_texto:
        filtros_text = " | ".join(filtros_texto)
        filtros_paragraph = Paragraph(filtros_text, styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 15))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Tendencia Mensual</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 15))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 15))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 15))

    # Obtener datos mensuales (sin tasa de cierre)
    datos_mensuales = tickets.annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total=Count('id'),
        cerrados=Count('id', filter=Q(estado='cerrado')),
        alta=Count('id', filter=Q(prioridad='alta')),
        media=Count('id', filter=Q(prioridad='media')),
        baja=Count('id', filter=Q(prioridad='baja'))
    ).order_by('mes')

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla (sin tasa de cierre)
    headers = [
        Paragraph("<b>Mes/Año</b>", styles['Heading3']),
        Paragraph("<b>Total Creados</b>", styles['Heading3']),
        Paragraph("<b>Cerrados</b>", styles['Heading3']),
        Paragraph("<b>Prioridad Alta</b>", styles['Heading3']),
        Paragraph("<b>Prioridad Media</b>", styles['Heading3']),
        Paragraph("<b>Prioridad Baja</b>", styles['Heading3'])
    ]
    data.append(headers)

    # Llenar datos (sin tasa de cierre)
    for mes_data in datos_mensuales:
        mes = mes_data['mes'].strftime('%b/%Y')
        
        data.append([
            Paragraph(mes, styles['Normal']),
            Paragraph(str(mes_data['total']), styles['Normal']),
            Paragraph(str(mes_data['cerrados']), styles['Normal']),
            Paragraph(str(mes_data['alta']), styles['Normal']),
            Paragraph(str(mes_data['media']), styles['Normal']),
            Paragraph(str(mes_data['baja']), styles['Normal'])
        ])

    # Definir anchos de columna optimizados
    col_widths = [
        1.2*inch,   # Mes/Año
        1.0*inch,   # Total
        1.0*inch,   # Cerrados
        1.0*inch,   # Alta
        1.0*inch,   # Media
        1.0*inch    # Baja
    ]

    # Crear la tabla con estilo mejorado
    table = Table(data, repeatRows=1, colWidths=col_widths)
    
    # Estilo optimizado
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Colorear por prioridad
        ('TEXTCOLOR', (3, 1), (3, -1), colors.red),    # Alta
        ('TEXTCOLOR', (4, 1), (4, -1), colors.orange), # Media
        ('TEXTCOLOR', (5, 1), (5, -1), colors.green),  # Baja
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Estadísticas Mensuales</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"<i>Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets</i>", 
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def exportar_desempeno_departamento_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query
    tickets = Ticket.objects.all().select_related('tecnico')

    # Aplicar filtros
    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Obtener datos por departamento
    datos_departamentos = tickets.filter(tecnico__departamento__isnull=False)\
        .values('tecnico__departamento__nombre')\
        .annotate(
            total=Count('id'),
            cerrados=Count('id', filter=Q(estado='cerrado'))
        )\
        .order_by('tecnico__departamento__nombre')

    # Generar el gráfico de desempeño por departamento
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_tickets_por_departamento(req)
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_desempeno_departamento.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title_style = styles['Title']
    title_style.fontSize = 16
    title_style.spaceAfter = 12
    title = Paragraph("Desempeño por Departamento", title_style)
    story.append(title)

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"<b>Desde:</b> {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"<b>Hasta:</b> {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"<b>Sucursal:</b> {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("<b>Sucursal:</b> No encontrada")

    if filtros_texto:
        filtros_text = " | ".join(filtros_texto)
        filtros_paragraph = Paragraph(filtros_text, styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 15))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Tickets por Departamento</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 15))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 15))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 15))

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla
    headers = [
        Paragraph("<b>Departamento</b>", styles['Heading3']),
        Paragraph("<b>Tickets Creados</b>", styles['Heading3']),
        Paragraph("<b>Tickets Cerrados</b>", styles['Heading3']),
        Paragraph("<b>% Cumplimiento</b>", styles['Heading3'])
    ]
    data.append(headers)

    # Llenar datos
    for depto_data in datos_departamentos:
        porcentaje = (depto_data['cerrados'] / depto_data['total']) * 100 if depto_data['total'] > 0 else 0
        data.append([
            Paragraph(depto_data['tecnico__departamento__nombre'], styles['Normal']),
            Paragraph(str(depto_data['total']), styles['Normal']),
            Paragraph(str(depto_data['cerrados']), styles['Normal']),
            Paragraph(f"{porcentaje:.1f}%", styles['Normal'])
        ])

    # Definir anchos de columna
    col_widths = [
        2.5*inch,   # Departamento
        1.5*inch,   # Tickets Creados
        1.5*inch,   # Tickets Cerrados
        1.5*inch    # % Cumplimiento
    ]

    # Crear la tabla
    table = Table(data, repeatRows=1, colWidths=col_widths)
    
    # Estilo optimizado
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Resaltar departamentos con buen desempeño (más del 50% cerrados)
        ('TEXTCOLOR', (0, 1), (0, -1), 
            lambda r, c, v: colors.green if float(data[r][3][:-1]) > 50 else colors.black),
        # Resaltar porcentajes altos en verde
        ('TEXTCOLOR', (3, 1), (3, -1), 
            lambda r, c, v: colors.green if float(data[r][3][:-1]) > 50 else colors.red),
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Estadísticas por Departamento</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"<i>Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets</i>", 
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response


def exportar_cumplimiento_sla_general_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_cumplimiento_sla_general.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Título del reporte
    story.append(Paragraph("<b>Reporte de Indicador de Cumplimiento de SLA</b>", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # Filtros
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets = Ticket.objects.select_related('cliente', 'tecnico__departamento__sucursal').all()

    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)
    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        tickets = tickets.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE)) + timedelta(days=1) - timedelta(seconds=1)
        tickets = tickets.filter(fecha_creacion__lte=fecha_fin)

    # Contadores para el gráfico
    cumplieron_sla_count = 0
    no_cumplieron_sla_count = 0
    # en_proceso_sla_count = 0 # No es necesario para el gráfico "Cumplió/No Cumplió"

    # Preparar datos para la tabla y contadores para el gráfico
    data = []
    data.append([
        "ID Ticket", "Título Ticket", "Prioridad", "SLA Definido",
        "Tiempo Resolución", "¿Cumplió SLA?", "Técnico Asignado"
    ])

    for ticket in tickets:
        sla_definido = ""
        if ticket.prioridad == 'baja':
            sla_definido = "72h"
        elif ticket.prioridad == 'media':
            sla_definido = "24h"
        elif ticket.prioridad == 'alta':
            sla_definido = "4h"

        tiempo_resolucion = "N/A"
        cumplio_sla = "N/A"

        if ticket.fecha_cierre and ticket.fecha_creacion:
            duracion_ticket = ticket.fecha_cierre - ticket.fecha_creacion
            total_horas = duracion_ticket.total_seconds() / 3600
            tiempo_resolucion = f"{total_horas:.2f}h"

            if (ticket.prioridad == 'baja' and total_horas <= 72) or \
               (ticket.prioridad == 'media' and total_horas <= 24) or \
               (ticket.prioridad == 'alta' and total_horas <= 4):
                cumplio_sla = "Sí"
                cumplieron_sla_count += 1
            else:
                cumplio_sla = "No"
                no_cumplieron_sla_count += 1
        elif ticket.estado == 'cerrado' and not ticket.fecha_cierre:
             cumplio_sla = "No registrado"
             tiempo_resolucion = "No registrado"
             # No se cuenta para el gráfico de SLA si no hay fecha de cierre válida
        elif ticket.estado != 'cerrado':
            cumplio_sla = "En Proceso"
            tiempo_resolucion = "N/A"
            # en_proceso_sla_count += 1 # No se incluye en el gráfico de cumplimiento de SLA

        tecnico_asignado = ticket.tecnico.nombre if ticket.tecnico else "No asignado"

        data.append([
            str(ticket.id),
            ticket.titulo,
            ticket.get_prioridad_display(),
            sla_definido,
            tiempo_resolucion,
            cumplio_sla,
            tecnico_asignado
        ])

    # --- Generación del Gráfico de Pastel con Matplotlib ---
    total_tickets_evaluados = cumplieron_sla_count + no_cumplieron_sla_count

    if total_tickets_evaluados > 0:
        labels = ['Cumplieron SLA', 'No Cumplieron SLA']
        sizes = [cumplieron_sla_count, no_cumplieron_sla_count]
        colors_chart = ['#4CAF50', '#F44336'] # Verde y Rojo

        fig1, ax1 = plt.subplots(figsize=(6, 3)) # Tamaño del gráfico para el PDF
        
        # Ocultar el porcentaje en el label para controlarlo con autopct
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_chart, startangle=90)
        
        # Ajustar el color y tamaño del texto de los porcentajes
        for autotext in autotexts:
            autotext.set_color('white') # Color blanco para los porcentajes
            autotext.set_fontsize(8) # Tamaño de fuente más pequeño para porcentajes
        
        ax1.axis('equal')  # Asegura que el pastel sea un círculo.

        
        
        # Guardar gráfico en buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight') # bbox_inches='tight' para eliminar márgenes extra
        plt.close(fig1) # Cerrar la figura para liberar memoria

        # Añadir gráfico al PDF
        story.append(Spacer(1, 0.3 * inch))
        img = Image(buf)
        img.drawWidth = 6 * inch  # Ajusta el ancho del gráfico en el PDF
        img.drawHeight = 3 * inch # Ajusta el alto del gráfico en el PDF
        story.append(img)
        story.append(Spacer(1, 0.2 * inch)) # Espacio entre el gráfico y la tabla
    else:
        story.append(Paragraph("<i>No hay tickets cerrados para evaluar el cumplimiento de SLA.</i>", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

    # --- Fin de la Generación del Gráfico ---

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E3F2FD')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(table)

    # Pie de página
    fecha_generacion = timezone.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"<i>Reporte generado el: {fecha_generacion}</i>", styles['Normal']))

    doc.build(story)
    return response


def exportar_ranking_tecnicos_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query
    tickets = Ticket.objects.all().select_related('tecnico', 'evaluacion')
    tecnicos = Usuario.objects.filter(rol='tecnico')

    # Aplicar filtros
    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
        tecnicos = tecnicos.filter(departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)
        tecnicos = tecnicos.filter(departamento__id=departamento_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Definir SLAs
    sla_horas = {
        'baja': 72,
        'media': 24,
        'alta': 4
    }

    # Preparar datos para el ranking
    ranking_data = []
    for tecnico in tecnicos:
        # Tickets del técnico
        tickets_tecnico = tickets.filter(tecnico=tecnico)
        total_tickets = tickets_tecnico.count()
        tickets_cerrados = tickets_tecnico.filter(estado='cerrado', fecha_cierre__isnull=False)
        tickets_abiertos = tickets_tecnico.filter(estado='abierto')

        # Calcular cumplimiento SLA
        dentro_sla = 0
        for ticket in tickets_cerrados:
            tiempo_resolucion = (ticket.fecha_cierre - ticket.fecha_creacion).total_seconds() / 3600
            sla_esperado = sla_horas.get(ticket.prioridad, 72)
            if tiempo_resolucion <= sla_esperado:
                dentro_sla += 1

        porcentaje_sla = (dentro_sla / tickets_cerrados.count()) * 100 if tickets_cerrados.count() > 0 else 0


        ranking_data.append({
            'tecnico': tecnico.nombre,
            'total_tickets': total_tickets,
            'tickets_cerrados': tickets_cerrados.count(),
            'tickets_abiertos': tickets_abiertos.count(),
            'porcentaje_sla': round(porcentaje_sla, 2)
        })

    # Ordenar por el número de tickets cerrados (de mayor a menor)
    ranking_data.sort(key=lambda x: (-x['tickets_cerrados'], -x['porcentaje_sla'])) # Mantenemos el % SLA como segundo criterio

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ranking_tecnicos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title = Paragraph("Reporte de Ranking de Eficiencia Técnica", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("Filtros aplicados: " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Generar el gráfico de ranking
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    # Asume que grafico_ranking_tecnicos es una función que existe y devuelve un JsonResponse
    # con el gráfico en base64. Si no existe, deberás crearla o adaptar esta parte.
    grafico_response = grafico_ranking_tecnicos(req) # Asegúrate que esta función esté definida
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Ranking de Técnicos</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla
    headers = [
        "Técnico",
        "Total Tickets",
        "Cerrados",
        "Abiertos",
        "% Cumplimiento SLA"
    ]
    data.append(headers)

    for item in ranking_data:
        data.append([
            item['tecnico'],
            str(item['total_tickets']),
            str(item['tickets_cerrados']),
            str(item['tickets_abiertos']),
            f"{item['porcentaje_sla']:.2f}%"
        ])

    # Crear la tabla
    table = Table(data, repeatRows=1)

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Resaltar los mejores porcentajes de SLA
        ('TEXTCOLOR', (4, 1), (4, -1),
            lambda r, c, v: colors.green if float(data[r][4][:-1]) >= 80 else
                            colors.orange if float(data[r][4][:-1]) >= 50 else
                            colors.red)
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle del Ranking</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets",
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def exportar_desempeno_tecnico_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query para técnicos
    tecnicos = Usuario.objects.filter(rol='tecnico').select_related('departamento')

    # Aplicar filtros
    if sucursal_id:
        tecnicos = tecnicos.filter(departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tecnicos = tecnicos.filter(departamento__id=departamento_id)

    # Obtener tickets con los mismos filtros
    tickets = Ticket.objects.all()
    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)
    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Preparar datos para el reporte
    desempeno_data = []
    for tecnico in tecnicos:
        # Tickets asignados al técnico
        tickets_tecnico = tickets.filter(tecnico=tecnico)
        total_tickets = tickets_tecnico.count()
        
        # Evaluaciones del técnico
        evaluaciones = EvaluacionTecnico.objects.filter(ticket__in=tickets_tecnico)
        total_evaluaciones = evaluaciones.count()
        
        # Calcular calificación promedio
        promedio = evaluaciones.aggregate(Avg('calificacion'))['calificacion__avg'] or 0

        desempeno_data.append({
            'tecnico': tecnico.nombre,
            'departamento': tecnico.departamento.nombre if tecnico.departamento else 'Sin departamento',
            'tickets_asignados': total_tickets,
            'total_evaluaciones': total_evaluaciones,
            'calificacion_promedio': round(promedio, 2)
        })

    # Ordenar por calificación promedio descendente
    desempeno_data.sort(key=lambda x: -x['calificacion_promedio'])

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_desempeno_tecnico.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title = Paragraph("Reporte de Desempeño Promedio por Técnico", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("Filtros aplicados: " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Generar el gráfico de desempeño
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_calificacion_promedio_tecnico(req)
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Calificación Promedio por Técnico</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla
    headers = [
        "Técnico",
        "Departamento",
        "Tickets Asignados",
        "Total Evaluaciones", 
        "Calificación Promedio"
    ]
    data.append(headers)

    for item in desempeno_data:
        data.append([
            item['tecnico'],
            item['departamento'],
            str(item['tickets_asignados']),
            str(item['total_evaluaciones']),
            f"{item['calificacion_promedio']:.2f}"
        ])

    # Crear la tabla
    table = Table(data, repeatRows=1)

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Resaltar las mejores calificaciones
        ('TEXTCOLOR', (4, 1), (4, -1),
            lambda r, c, v: colors.green if float(data[r][4]) >= 4 else
                            colors.orange if float(data[r][4]) >= 3 else
                            colors.red)
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle del Desempeño por Técnico</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets",
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def exportar_tickets_por_cliente_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query
    tickets = Ticket.objects.all().select_related('cliente', 'tecnico', 'categoria')

    # Aplicar filtros
    if sucursal_id:
        tickets = tickets.filter(tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        tickets = tickets.filter(tecnico__departamento__id=departamento_id)

    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_fin)

    # Generar el gráfico de tickets por cliente
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_tickets_por_cliente(req)
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_tickets_por_cliente.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título del documento
    title = Paragraph("Reporte de Volumen de Tickets por Cliente", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("Filtros aplicados: " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Gráfico de Tickets por Cliente</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Obtener datos de clientes con más tickets
    clientes_data = tickets.exclude(cliente__isnull=True)\
        .values('cliente__nombres', 'cliente__empresa', 'cliente__id')\
        .annotate(
            total_tickets=Count('id'),
            tickets_abiertos=Count('id', filter=Q(estado='abierto')),
            tickets_cerrados=Count('id', filter=Q(estado='cerrado')),
            categoria_mas_frecuente=models.Subquery(
                tickets.filter(cliente_id=models.OuterRef('cliente__id'))
                .values('cliente_id')
                .annotate(categoria_frecuente=models.Max('categoria__nombre'))
                .values('categoria_frecuente')[:1]
            )
        )\
        .order_by('-total_tickets')[:10]  # Limitar a los 10 primeros

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla
    headers = [
        "Cliente",
        "Empresa",
        "Categoría Más Frecuente",
        "Tickets Totales",
        "Tickets Abiertos",
        "Tickets Cerrados"
    ]
    data.append(headers)

    for cliente in clientes_data:
        data.append([
            cliente['cliente__nombres'],
            cliente['cliente__empresa'] or "N/A",
            cliente['categoria_mas_frecuente'] or "N/A",
            str(cliente['total_tickets']),
            str(cliente['tickets_abiertos']),
            str(cliente['tickets_cerrados'])
        ])

    # Crear la tabla
    table = Table(data, repeatRows=1)

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Resaltar clientes con muchos tickets abiertos
        ('TEXTCOLOR', (4, 1), (4, -1),
            lambda r, c, v: colors.red if int(data[r][4]) > 3 else colors.black)
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle de Tickets por Cliente</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets",
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response



def exportar_evaluacion_calidad_pdf(request):
    # Obtener los filtros de la solicitud
    sucursal_id = request.GET.get('sucursal')
    departamento_id = request.GET.get('departamento')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base query
    evaluaciones = EvaluacionTecnico.objects.select_related(
        'ticket__tecnico__departamento__sucursal',
        'ticket__categoria',
        'ticket__cliente'
    ).filter(
        calificacion__isnull=False
    ).order_by('-fecha_evaluacion')

    # Aplicar filtros
    if sucursal_id:
        evaluaciones = evaluaciones.filter(ticket__tecnico__departamento__sucursal__id=sucursal_id)
    if departamento_id:
        evaluaciones = evaluaciones.filter(ticket__tecnico__departamento__id=departamento_id)
    if fecha_inicio_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        evaluaciones = evaluaciones.filter(fecha_evaluacion__date__gte=fecha_inicio)
    if fecha_fin_str:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        evaluaciones = evaluaciones.filter(fecha_evaluacion__date__lte=fecha_fin)

    # Generar el gráfico de calificaciones
    from django.http import HttpRequest
    req = HttpRequest()
    req.GET = request.GET.copy()
    grafico_response = grafico_calificaciones_servicio(req)
    grafico_data = json.loads(grafico_response.content.decode('utf-8'))

    # Preparar la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_evaluacion_calidad_servicio.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    # Estilo personalizado para títulos largos
    styles.add(ParagraphStyle(name='WrappedTitle',
                               parent=styles['Title'],
                               fontSize=18,
                               leading=22,
                               alignment=1, # TA_CENTER
                               spaceAfter=12))
    
    # Estilo para encabezados de sección
    styles.add(ParagraphStyle(name='Heading2Centered',
                               parent=styles['Heading2'],
                               alignment=1, # TA_CENTER
                               spaceAfter=6))
    
    story = []

    # Título del documento
    title = Paragraph("Reporte de Evaluación de la Calidad del Servicio", styles['WrappedTitle'])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Añadir texto descriptivo con los filtros aplicados
    filtros_texto = []
    if fecha_inicio_str:
        filtros_texto.append(f"Desde: {fecha_inicio_str}")
    if fecha_fin_str:
        filtros_texto.append(f"Hasta: {fecha_fin_str}")
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.get(id=sucursal_id)
            filtros_texto.append(f"Sucursal: {sucursal.nombre}")
        except Sucursal.DoesNotExist:
            filtros_texto.append("Sucursal: No encontrada")
    if departamento_id:
        try:
            departamento = Departamento.objects.get(id=departamento_id)
            filtros_texto.append(f"Departamento: {departamento.nombre}")
        except Departamento.DoesNotExist:
            filtros_texto.append("Departamento: No encontrado")

    if filtros_texto:
        filtros_paragraph = Paragraph("<b>Filtros aplicados:</b> " + ", ".join(filtros_texto), styles['Normal'])
        story.append(filtros_paragraph)
        story.append(Spacer(1, 0.2 * inch))

    # Añadir el gráfico si está disponible
    if grafico_data.get('grafico'):
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(grafico_data['grafico'])
            img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
            story.append(Paragraph("<b>Distribución de Calificaciones</b>", styles['Heading2Centered']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            error_msg = Paragraph(f"<font color='red'>Error al incluir gráfico: {str(e)}</font>", styles['Normal'])
            story.append(error_msg)
            story.append(Spacer(1, 0.2 * inch))
    elif grafico_data.get('message'):
        no_data_msg = Paragraph(f"<i>{grafico_data['message']}</i>", styles['Italic'])
        story.append(no_data_msg)
        story.append(Spacer(1, 0.2 * inch))

    # Estadísticas resumidas
    total_evaluaciones = evaluaciones.count()
    promedio_calificacion = evaluaciones.aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    calificacion_1 = evaluaciones.filter(calificacion=1).count()
    calificacion_2 = evaluaciones.filter(calificacion=2).count()
    calificacion_3 = evaluaciones.filter(calificacion=3).count()
    calificacion_4 = evaluaciones.filter(calificacion=4).count()
    calificacion_5 = evaluaciones.filter(calificacion=5).count()

    

    # Preparar datos para la tabla
    data = []
    # Encabezados de la tabla
    headers = [
        "ID Ticket",
        "Título",
        "Categoría",
        "Calificación",
        "Comentario",
        "Fecha Evaluación",
        "Técnico"
    ]
    data.append(headers)

    for evaluacion in evaluaciones:
        data.append([
            str(evaluacion.ticket.id),
            evaluacion.ticket.titulo,
            evaluacion.ticket.categoria.nombre if evaluacion.ticket.categoria else "N/A",
            evaluacion.get_calificacion_display(),
            evaluacion.comentario or "Sin comentario",
            evaluacion.fecha_evaluacion.strftime('%Y-%m-%d %H:%M') if evaluacion.fecha_evaluacion else "N/A",
            evaluacion.ticket.tecnico.nombre if evaluacion.ticket.tecnico else "No asignado"
        ])

    page_width = letter[0] - 2 * inch # Ancho de la página menos los márgenes predeterminados de ReportLab
    
    col_widths = [
        0.7 * inch,  # ID Ticket
        1.2 * inch,  # Título (se ajustará con Paragraph en la celda)
        1.0 * inch,  # Categoría
        0.9 * inch,  # Calificación
        1.7 * inch,  # Comentario (se ajustará con Paragraph en la celda)
        1.1 * inch,  # Fecha Evaluación
        1.4 * inch   # Técnico
    ]
    
    # Formatear datos para que los campos con texto largo se envuelvan
    # usando Paragraph dentro de las celdas
    formatted_data = []
    # Encabezados con estilo
    header_style = styles['Normal']
    header_style.fontName = 'Helvetica-Bold'
    header_style.fontSize = 9
    formatted_data.append([Paragraph(h, header_style) for h in headers])

    # Datos con estilo (sin colores condicionales)
    for row in data[1:]: # Ignorar los encabezados que ya añadimos
        formatted_row = []
        for i, cell_value in enumerate(row):
            cell_style = styles['Normal']
            cell_style.fontSize = 8
            # Removido el coloreado condicional para la columna de Calificación (índice 3)
            if i == 4: # Columna de Comentario (alinear a la izquierda)
                comment_style = styles['Normal']
                comment_style.fontSize = 8
                comment_style.alignment = 0 # TA_LEFT
                formatted_row.append(Paragraph(cell_value, comment_style))
            else: # Todas las demás columnas (incluida Calificación)
                formatted_row.append(Paragraph(cell_value, cell_style))
        formatted_data.append(formatted_row)

    # Crear la tabla
    table = Table(formatted_data, colWidths=col_widths, repeatRows=1)

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7F7F7F')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        # Las condiciones de TEXTCOLOR para la columna de calificación han sido removidas
    ]))

    # Añadir título para la tabla
    story.append(Paragraph("<b>Detalle de Evaluaciones</b>", styles['Heading2Centered']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(table)

    # Pie de página con información de generación
    fecha_generacion = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    pie_pagina = Paragraph(
        f"Reporte generado el {fecha_generacion} | Sistema de Gestión de Tickets",
        styles['Italic']
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(pie_pagina)

    # Construir el PDF
    doc.build(story)

    return response

def crear_cliente_ajax(request):
    if request.method == 'POST':
        form = clienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'id': cliente.id,
                'nombre': cliente.nombres
            })
        else:
            errores = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errores': errores})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})