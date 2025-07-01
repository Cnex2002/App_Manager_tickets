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


from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta, date # <-- Added date here
import pytz
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
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
from django.core.mail import send_mail
from django.db.models import Q
# ERORES PYTHON
from django.db.models import ProtectedError
from django.contrib import messages

# Importar Matplotlib
import matplotlib.pyplot as plt
import io
import urllib
import numpy as np
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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



@login_required
def ticket_nuevo(request):
    origen = request.GET.get('origen') or request.POST.get('origen')  # Captura de GET o POST
    if request.method == 'POST':
        # Pasar el request al formulario
        formulario = TicketForm(request.POST, request=request) 
        if formulario.is_valid():
            ticket = formulario.save(commit=False)
            ticket.estado = 'abierto'  # Asigna el estado inicial
            ticket.save()

            # Enviar correo electrónico al cliente
            asunto = f'Creación de Ticket #{ticket.id}'
            mensaje = (
                f'Estimado/a {ticket.cliente.nombres},\n\n'
                f'Se ha creado un nuevo ticket con los siguientes detalles:\n\n'
                f'Título: {ticket.titulo}\n'
                f'Descripción: {ticket.descripcion}\n'
                f'Estado: {ticket.estado}\n'
                f'Prioridad: {ticket.prioridad}\n'
                f'Categoría: {ticket.categoria.nombre}\n'
                f'Fecha de Creación: {ticket.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                f'Nos pondremos en contacto contigo a la brevedad posible.\n\n'
                f'Saludos,\n'
                f'Equipo de Soporte'
            )
            email_cliente = ticket.cliente.correo # Obtén el correo del cliente

            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,  # Desde el correo configurado en settings
                    [email_cliente],  # Lista de destinatarios
                    fail_silently=False,
                )
                messages.success(request, 'Ticket creado exitosamente y notificación por correo enviada al cliente.')
                 # Redirigir según el origen
                if origen == 'departamento':
                    return redirect('ver_tickets_departamento')
                else:
                    return redirect('lista_tickets')
            except Exception as e:
                messages.error(request, f'Ticket creado pero no se pudo enviar el correo de notificación: {e}')

            
    else:
        # Pasar el request al formulario
        formulario = TicketForm(request=request)
    return render(request, 'ticket_nuevo1.html', {'formulario': formulario, 'titulo': 'Crear Nuevo Ticket'})









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
    soluciones = SolucionTicket.objects.all().order_by('-fecha_subida')

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
            # Asegurarse de que la fecha sea interpretada correctamente
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            soluciones = soluciones.filter(fecha_subida__gte=fecha_desde_dt)
        except ValueError:
            messages.error(request, "Formato de fecha 'Desde' inválido. Use AAAA-MM-DD.")
    
    if fecha_hasta:
        try:
            # Sumar un día y restar un segundo para incluir todo el día de 'fecha_hasta'
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(tzinfo=pytz.timezone(settings.TIME_ZONE)) + timedelta(days=1, microseconds=-1)
            soluciones = soluciones.filter(fecha_subida__lte=fecha_hasta_dt)
        except ValueError:
            messages.error(request, "Formato de fecha 'Hasta' inválido. Use AAAA-MM-DD.")

    # Paginación
    paginator = Paginator(soluciones, 5)  # Mostrar 5 soluciones por página
    page = request.GET.get('page')
    try:
        soluciones_paginadas = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entregar la primera página.
        soluciones_paginadas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), entregar la última página de resultados.
        soluciones_paginadas = paginator.page(paginator.num_pages)

    context = {
        'soluciones': soluciones_paginadas,  # Usar las soluciones paginadas
        'titulo': 'Lista de Soluciones de Tickets',
        'query': query,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
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
    if request.method == 'POST':
        # Pasar el request al formulario
        formulario = TicketForm(request.POST, instance=ticket, request=request)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
             # Redirigir según el origen
            if origen == 'departamento':
                return redirect('ver_tickets_departamento')
            else:
                return redirect('lista_tickets') 
    else:
        # Pasar el request al formulario
        formulario = TicketForm(instance=ticket, request=request)

    contexto = {
        'formulario': formulario
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







# Helper function to generate and encode plots
def get_plot_as_base64(plt):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close() # Close the plot to free up memory
    return image_base64

# Function to generate a blank image with a message
def get_blank_plot_with_message(message="No hay datos disponibles para generar el gráfico."):
    plt.figure(figsize=(10, 6))
    plt.text(0.5, 0.5, message, horizontalalignment='center', verticalalignment='center', fontsize=12, color='gray')
    plt.axis('off') # Hide axes
    plt.title("Gráfico no disponible")
    return get_plot_as_base64(plt)


# 1. Tickets por Estado (Circular / Anillo)
def tickets_por_estado_report(start_date=None, end_date=None):
    queryset = Ticket.objects.all()
    if start_date:
        queryset = queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        queryset = queryset.filter(fecha_creacion__lte=end_date)
    
    estados = queryset.values('estado').annotate(count=Count('id'))
    labels = [e['estado'].capitalize() for e in estados]
    sizes = [e['count'] for e in estados]
    colors = ['#FF9999', '#66B2FF', '#99FF99'] # Light colors for better readability

    if not sizes: # Handle case where no tickets are found
        return get_blank_plot_with_message("No hay tickets en el rango de fechas seleccionado.")

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'edgecolor': 'black'})
    ax1.axis('equal')   # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title('Tickets por Estado')
    return get_plot_as_base64(plt)

# 2. Departamentos con Más Incidencias (Barras Verticales)
def departamentos_incidencias_report(start_date=None, end_date=None):
    queryset = Ticket.objects.all()
    if start_date:
        queryset = queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        queryset = queryset.filter(fecha_creacion__lte=end_date)

    # Use F() expression to access fields across relationships
    departamentos = queryset.values(
        departamento_nombre=F('tecnico__departamento__nombre')
    ).annotate(count=Count('id')).order_by('-count')

    labels = [d['departamento_nombre'] if d['departamento_nombre'] else 'Sin Departamento' for d in departamentos]
    counts = [d['count'] for d in departamentos]

    if not counts: # Handle case where no data is found
        return get_blank_plot_with_message("No hay datos de incidencias por departamento en el rango de fechas seleccionado.")

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color='skyblue')
    plt.xlabel('Departamentos')
    plt.ylabel('Número de Incidencias')
    plt.title('Departamentos con Más Incidencias')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return get_plot_as_base64(plt)

# 3. Tendencia de Tickets por Mes (Gráfico de serie Temporal)
def tendencia_tickets_por_mes_report(start_date=None, end_date=None):
    queryset = Ticket.objects.all()
    if start_date:
        queryset = queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        queryset = queryset.filter(fecha_creacion__lte=end_date)

    # Annotate with month and year for grouping
    tickets_por_mes = queryset.annotate(
        month=TruncMonth('fecha_creacion')
    ).values('month').annotate(count=Count('id')).order_by('month')

    months = [t['month'].strftime('%Y-%m') for t in tickets_por_mes]
    counts = [t['count'] for t in tickets_por_mes]

    if not months: # Handle case where no data is found
        return get_blank_plot_with_message("No hay datos de tendencia de tickets por mes en el rango de fechas seleccionado.")

    plt.figure(figsize=(12, 6))
    plt.plot(months, counts, marker='o', linestyle='-')
    plt.xlabel('Mes y Año')
    plt.ylabel('Número de Tickets')
    plt.title('Tendencia de Tickets por Mes')
    plt.grid(True)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return get_plot_as_base64(plt)

# 4. Categorías con mas incidencias (Barras Verticales)
def categorias_incidencias_report(start_date=None, end_date=None):
    queryset = Ticket.objects.all()
    if start_date:
        queryset = queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        queryset = queryset.filter(fecha_creacion__lte=end_date)

    categorias = queryset.values('categoria__nombre').annotate(count=Count('id')).order_by('-count')
    labels = [c['categoria__nombre'] if c['categoria__nombre'] else 'Sin Categoría' for c in categorias]
    counts = [c['count'] for c in categorias]

    if not counts: # Handle case where no data is found
        return get_blank_plot_with_message("No hay datos de incidencias por categoría en el rango de fechas seleccionado.")

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color='lightcoral')
    plt.xlabel('Categorías')
    plt.ylabel('Número de Incidencias')
    plt.title('Categorías con Más Incidencias')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return get_plot_as_base64(plt)

# 5. Calificación de tickets (histograma)
def calificacion_tickets_report(start_date=None, end_date=None):
    queryset = EvaluacionTecnico.objects.all()
    if start_date:
        queryset = queryset.filter(ticket__fecha_creacion__gte=start_date)
    if end_date:
        queryset = queryset.filter(ticket__fecha_creacion__lte=end_date)

    calificaciones = queryset.values_list('calificacion', flat=True).exclude(calificacion__isnull=True)
    
    if not calificaciones:
        return get_blank_plot_with_message("No hay datos de calificaciones en el rango de fechas seleccionado.")

    # Map numerical ratings to their string representations
    calificacion_map = dict(CALIFICACION_CHOICES)
    display_calificaciones = [calificacion_map.get(c, 'Desconocido') for c in calificaciones]

    # Count occurrences of each rating
    from collections import Counter
    rating_counts = Counter(display_calificaciones)
    
    # Order the labels according to CALIFICACION_CHOICES
    # Only include labels for ratings that actually exist in the data
    existing_ratings = sorted(list(set(c for c in calificaciones if c is not None)))
    ordered_labels = [calificacion_map[i] for i in existing_ratings]
    ordered_counts = [rating_counts[calificacion_map[label_key]] for label_key in existing_ratings]

    plt.figure(figsize=(8, 5))
    plt.bar(ordered_labels, ordered_counts, color='lightgreen')
    plt.xlabel('Calificación')
    plt.ylabel('Número de Evaluaciones')
    plt.title('Distribución de Calificaciones de Tickets')
    plt.tight_layout()
    return get_plot_as_base64(plt)

def tiempo_promedio_resolucion_report(start_date=None, end_date=None):
    # Calcular el tiempo de resolución para cada ticket cerrado
    tickets_cerrados = Ticket.objects.filter(estado='cerrado', fecha_cierre__isnull=False)

    if start_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__gte=start_date)
    if end_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__lte=end_date + timedelta(days=1))

    ticket_durations = tickets_cerrados.annotate(
        duration=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    ).filter(tecnico__isnull=False)

    # Agrupar por técnico y calcular el promedio de resolución individual
    tecnico_avg_durations = ticket_durations.values('tecnico__nombre').annotate(
        avg_duration=Avg('duration')
    ).order_by('tecnico__nombre')

    # Convertir timedelta a horas/días para fácil comparación y filtrar outliers
    tecnicos_resolucion = []
    for item in tecnico_avg_durations:
        if item['avg_duration']:
            # Convertir a horas para la detección de outliers (o el valor que consideres alto)
            duration_in_hours = item['avg_duration'].total_seconds() / 3600
            tecnicos_resolucion.append({
                'nombre': item['tecnico__nombre'],
                'avg_duration_seconds': item['avg_duration'].total_seconds(),
                'avg_duration_hours': duration_in_hours
            })

    # Calcular la mediana de los tiempos promedio de los técnicos para identificar outliers
    # Usaremos el IQR para una detección robusta de outliers
    avg_resolution_time_formatted = "No hay tickets cerrados para calcular el MTTR."
    if tecnicos_resolucion:
        all_avg_hours = [t['avg_duration_hours'] for t in tecnicos_resolucion]
        Q1 = np.percentile(all_avg_hours, 25)
        Q3 = np.percentile(all_avg_hours, 75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR

        # Filtrar técnicos con alto promedio de resolución (outliers)
        filtered_tecnicos_resolucion = [
            t for t in tecnicos_resolucion if t['avg_duration_hours'] <= upper_bound
        ]

        if filtered_tecnicos_resolucion:
            # Calcular el promedio de resolución general sin los outliers
            total_avg_seconds_filtered = sum(t['avg_duration_seconds'] for t in filtered_tecnicos_resolucion) / len(filtered_tecnicos_resolucion)
            
            # Convertir a formato legible (días, horas, minutos)
            def format_duration(seconds):
                days = int(seconds // (24 * 3600))
                hours = int((seconds % (24 * 3600)) // 3600)
                minutes = int((seconds % 3600) // 60)
                return f"{days}d {hours}h {minutes}m"

            avg_resolution_time_formatted = format_duration(total_avg_seconds_filtered)
        else:
            avg_resolution_time_formatted = "No hay datos suficientes para calcular el MTTR sin outliers."
    

    # Recalculamos el MTTR por mes, ya que el MTTR general ya ha sido limpiado de outliers.
    # Esta parte se enfoca en la tendencia, no en la eliminación de outliers individuales por técnico.
    
    # Calcular el tiempo de resolución por mes (sin filtrar técnicos específicos aquí)
    mttr_por_mes = tickets_cerrados.annotate(
        month=TruncMonth('fecha_cierre'),
        duration=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    ).values('month').annotate(
        avg_duration_per_month=Avg('duration')
    ).order_by('month')

    fechas_mttr = []
    durations_mttr = []

    for item in mttr_por_mes:
        if item['avg_duration_per_month']:
            fechas_mttr.append(item['month'].strftime('%Y-%m'))
            durations_mttr.append(item['avg_duration_per_month'].total_seconds() / 3600) # Convert to hours

    if not durations_mttr: # Added check for empty data
        mttr_img = get_blank_plot_with_message("No hay datos de MTTR por mes en el rango de fechas seleccionado.")
    else:
        plt.figure(figsize=(10, 6))
        plt.plot(fechas_mttr, durations_mttr, marker='o', linestyle='-', color='orange')
        plt.xlabel('Mes')
        plt.ylabel('Tiempo Promedio de Resolución (Horas)')
        plt.title('Tendencia del Tiempo Promedio de Resolución (MTTR) por Mes')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True)
        plt.tight_layout()
        mttr_img = get_plot_as_base64(plt)

    return mttr_img, avg_resolution_time_formatted


def tickets_fuera_de_sla_report(start_date=None, end_date=None):
    # Aquí se asume un SLA de ejemplo, por ejemplo, 48 horas (2 días) para tickets.
    # DEBES DEFINIR TUS PROPIOS TIEMPOS DE SLA SEGÚN LA PRIORIDAD, CATEGORÍA, ETC.
    SLA_THRESHOLD_HOURS = 48 # Ejemplo: 48 horas de SLA.

    tickets_cerrados = Ticket.objects.filter(estado='cerrado', fecha_cierre__isnull=False)

    if start_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__gte=start_date)
    if end_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__lte=end_date + timedelta(days=1))

    ticket_durations = tickets_cerrados.annotate(
        duration=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    ).filter(tecnico__isnull=False)

    # Identificar técnicos con alto promedio de resolución para excluir del cálculo global de MTTR
    # y para el gráfico de "Tickets Fuera de SLA"
    tecnico_avg_durations_for_sla = ticket_durations.values('tecnico__nombre').annotate(
        avg_duration=Avg('duration')
    ).order_by('tecnico__nombre')

    tecnicos_resolucion_sla = []
    for item in tecnico_avg_durations_for_sla:
        if item['avg_duration']:
            tecnicos_resolucion_sla.append({
                'nombre': item['tecnico__nombre'],
                'avg_duration_hours': item['avg_duration'].total_seconds() / 3600
            })
    
    outlier_tecnicos = []
    outlier_avg_resolution_time_formatted = "No hay datos de resolución de tickets."
    if tecnicos_resolucion_sla:
        all_avg_hours_sla = [t['avg_duration_hours'] for t in tecnicos_resolucion_sla]
        Q1_sla = np.percentile(all_avg_hours_sla, 25)
        Q3_sla = np.percentile(all_avg_hours_sla, 75)
        IQR_sla = Q3_sla - Q1_sla
        upper_bound_sla = Q3_sla + 1.5 * IQR_sla

        outlier_tecnicos_names = [t['nombre'] for t in tecnicos_resolucion_sla if t['avg_duration_hours'] > upper_bound_sla]
        
        # Calcular el promedio de resolución solo para los técnicos outliers
        outlier_tickets = ticket_durations.filter(tecnico__nombre__in=outlier_tecnicos_names)
        
        if outlier_tickets.exists():
            avg_outlier_duration_seconds = outlier_tickets.aggregate(avg_dur=Avg('duration'))['avg_dur'].total_seconds()
            
            def format_duration(seconds):
                days = int(seconds // (24 * 3600))
                hours = int((seconds % (24 * 3600)) // 3600)
                minutes = int((seconds % 3600) // 60)
                return f"{days}d {hours}h {minutes}m"
            
            outlier_avg_resolution_time_formatted = format_duration(avg_outlier_duration_seconds)
        else:
            outlier_avg_resolution_time_formatted = "No hay tickets de técnicos con alto promedio de resolución en el período."
    


    # Ahora, para el gráfico de tickets fuera de SLA, necesitamos el total de tickets cerrados
    # y los que exceden el SLA.
    total_tickets_cerrados = tickets_cerrados.count()
    tickets_fuera_sla = tickets_cerrados.annotate(
        duration_seconds=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    ).filter(
        duration_seconds__gt=timedelta(hours=SLA_THRESHOLD_HOURS)
    ).count()

    tickets_en_sla = total_tickets_cerrados - tickets_fuera_sla

    labels = ['Tickets Dentro de SLA', 'Tickets Fuera de SLA']
    sizes = [tickets_en_sla, tickets_fuera_sla]
    colors = ['lightgreen', 'lightcoral']
    explode = (0, 0.1)  # explode 1st slice

    if total_tickets_cerrados == 0: # Added check for no closed tickets
        sla_img = get_blank_plot_with_message("No hay tickets cerrados para evaluar el cumplimiento de SLA en el rango de fechas seleccionado.")
    else:
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')   # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f'Cumplimiento de SLA (Umbral: {SLA_THRESHOLD_HOURS} Horas)')
        plt.tight_layout()
        sla_img = get_plot_as_base64(plt)

    return sla_img, outlier_avg_resolution_time_formatted


# NEW: Tiempo Promedio de Resolución de Técnicos con Alto Tiempo de Resolución (Outliers de SLA)
def tiempo_promedio_resolucion_outliers_report(start_date=None, end_date=None):
    SLA_THRESHOLD_HOURS = 48  # Reutilizar el mismo umbral SLA

    tickets_cerrados = Ticket.objects.filter(estado='cerrado', fecha_cierre__isnull=False)

    if start_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__gte=start_date)
    if end_date:
        tickets_cerrados = tickets_cerrados.filter(fecha_creacion__lte=end_date + timedelta(days=1))

    ticket_durations = tickets_cerrados.annotate(
        duration=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    ).filter(tecnico__isnull=False)

    tecnico_avg_durations = ticket_durations.values('tecnico__nombre').annotate(
        avg_duration=Avg('duration')
    ).order_by('tecnico__nombre')

    tecnicos_resolucion = []
    for item in tecnico_avg_durations:
        if item['avg_duration']:
            tecnicos_resolucion.append({
                'nombre': item['tecnico__nombre'],
                'avg_duration_hours': item['avg_duration'].total_seconds() / 3600
            })

    outlier_tecnicos_names = []
    if tecnicos_resolucion:
        all_avg_hours = [t['avg_duration_hours'] for t in tecnicos_resolucion]
        # Check if all_avg_hours is not empty before calculating percentiles
        if all_avg_hours:
            Q1 = np.percentile(all_avg_hours, 25)
            Q3 = np.percentile(all_avg_hours, 75)
            IQR = Q3 - Q1
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_tecnicos_names = [t['nombre'] for t in tecnicos_resolucion if t['avg_duration_hours'] > upper_bound]

    # Filtrar tickets solo para los técnicos identificados como outliers
    outlier_tickets_filtered = tickets_cerrados.filter(
        tecnico__nombre__in=outlier_tecnicos_names
    ).annotate(
        month=TruncMonth('fecha_cierre'),
        duration=ExpressionWrapper(F('fecha_cierre') - F('fecha_creacion'), output_field=DurationField())
    )

    # Calcular el MTTR por mes solo para los tickets de los técnicos outliers
    mttr_outliers_por_mes = outlier_tickets_filtered.values('month').annotate(
        avg_duration_per_month=Avg('duration')
    ).order_by('month')

    fechas_mttr_outliers = []
    durations_mttr_outliers = []

    for item in mttr_outliers_por_mes:
        if item['avg_duration_per_month']:
            fechas_mttr_outliers.append(item['month'].strftime('%Y-%m'))
            durations_mttr_outliers.append(item['avg_duration_per_month'].total_seconds() / 3600) # Convert to hours

    mttr_outliers_img = None
    info_outliers = "No hay datos de tickets cerrados para técnicos con alto promedio de resolución en el período."

    if not durations_mttr_outliers: # Added check for empty data
        mttr_outliers_img = get_blank_plot_with_message("No hay datos de MTTR para técnicos con alto tiempo de resolución en el rango de fechas seleccionado.")
    else:
        plt.figure(figsize=(10, 6))
        plt.plot(fechas_mttr_outliers, durations_mttr_outliers, marker='o', linestyle='-', color='red')
        plt.xlabel('Mes')
        plt.ylabel('Tiempo Promedio de Resolución (Horas)')
        plt.title('Tendencia del MTTR para Técnicos con Alto Tiempo de Resolución')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True)
        plt.tight_layout()
        mttr_outliers_img = get_plot_as_base64(plt)

        # Información adicional para el reporte
        avg_overall_outlier_mttr_seconds = sum(durations_mttr_outliers) / len(durations_mttr_outliers) * 3600
        
        def format_duration(seconds):
            days = int(seconds // (24 * 3600))
            hours = int((seconds % (24 * 3600)) // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        
        info_outliers = f"MTTR promedio general para técnicos outliers: {format_duration(avg_overall_outlier_mttr_seconds)}. Técnicos considerados outliers: {', '.join(outlier_tecnicos_names) if outlier_tecnicos_names else 'Ninguno'}"

    return mttr_outliers_img, info_outliers

@login_required
def generar_reporte_rendimiento_tecnicos_excel(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido. Use AAAA-MM-DD.")
            return redirect('reportes') # Redirige de vuelta a la página de reportes

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido. Use AAAA-MM-DD.")
            return redirect('reportes') # Redirige de vuelta a la página de reportes

    # Filtrar tickets por rango de fechas si se proporcionan
    tickets_queryset = Ticket.objects.all()
    if start_date:
        tickets_queryset = tickets_queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        tickets_queryset = tickets_queryset.filter(fecha_creacion__lte=end_date + timedelta(days=1)) # Incluir el día final completo

    # Rendimiento de Técnicos (Detallado)
    tecnicos_data = Usuario.objects.filter(rol='tecnico').annotate(
        tickets_cerrados=Count('tickets_asignados', filter=Q(tickets_asignados__estado='cerrado', tickets_asignados__in=tickets_queryset)),
        tickets_abiertos=Count('tickets_asignados', filter=Q(tickets_asignados__estado='abierto', tickets_asignados__in=tickets_queryset)),
        tickets_en_proceso=Count('tickets_asignados', filter=Q(tickets_asignados__estado='en proceso', tickets_asignados__in=tickets_queryset)),
        total_tickets_asignados=Count('tickets_asignados', filter=Q(tickets_asignados__in=tickets_queryset)),
        tiempo_resolucion_avg=Avg(
            ExpressionWrapper(
                F('tickets_asignados__fecha_cierre') - F('tickets_asignados__fecha_creacion'),
                output_field=DurationField()
            ),
            filter=Q(tickets_asignados__estado='cerrado', tickets_asignados__in=tickets_queryset)
        ),
        calificacion_promedio=Avg('tickets_asignados__evaluacion__calificacion', filter=Q(tickets_asignados__in=tickets_queryset))
    ).order_by('tiempo_resolucion_avg') # Ordenar por menor tiempo de resolución

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Rendimiento Técnicos"

    # Encabezados
    headers = [
        "Nombre del Técnico", "Tickets Cerrados", "Tickets Abiertos",
        "Tickets En Proceso", "Total Tickets Asignados",
        "Tiempo Promedio de Resolución (MTTR)", "Calificación Promedio"
    ]
    sheet.append(headers)

    # Estilos para encabezados
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="007bff", end_color="007bff", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    header_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    for col_num, header_text in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = header_border
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25

    # Datos
    for tecnico in tecnicos_data:
        mttr = "N/A"
        if tecnico.tiempo_resolucion_avg:
            total_seconds = tecnico.tiempo_resolucion_avg.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            mttr = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

        calificacion = f"{tecnico.calificacion_promedio:.2f}" if tecnico.calificacion_promedio is not None else "N/A"

        row_data = [
            tecnico.nombre,
            tecnico.tickets_cerrados,
            tecnico.tickets_abiertos,
            tecnico.tickets_en_proceso,
            tecnico.total_tickets_asignados,
            mttr,
            calificacion
        ]
        sheet.append(row_data)

    # Ajustar el ancho de las columnas automáticamente (opcional, si los datos son muy variables)
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width


    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"rendimiento_tecnicos_reporte_{start_date_str or 'todos'}_a_{end_date_str or 'todos'}.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def generar_reporte_satisfaccion_cliente_excel(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido. Use AAAA-MM-DD.")
            return redirect('reportes')

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido. Use AAAA-MM-DD.")
            return redirect('reportes')

    evaluaciones_queryset = EvaluacionTecnico.objects.filter(
        calificacion__isnull=False,
        comentario__isnull=False
    ).select_related('ticket__cliente', 'ticket__tecnico') # Pre-fetch related objects

    if start_date:
        evaluaciones_queryset = evaluaciones_queryset.filter(fecha_evaluacion__gte=start_date)
    if end_date:
        evaluaciones_queryset = evaluaciones_queryset.filter(fecha_evaluacion__lte=end_date + timedelta(days=1))

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Satisfacción Cliente"

    headers = [
        "Título del Ticket", "Nombre Cliente", "Calificación",
        "Comentario", "Nombre del Técnico"
    ]
    sheet.append(headers)

    # Estilos para encabezados
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="007bff", end_color="007bff", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    header_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    for col_num, header_text in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = header_border
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25

    for eval_tec in evaluaciones_queryset:
        cliente_nombre = f"{eval_tec.ticket.cliente.nombres}" if eval_tec.ticket.cliente else "N/A"
        tecnico_nombre = f"{eval_tec.ticket.tecnico.nombre}" if eval_tec.ticket.tecnico else "N/A"
        row_data = [
            eval_tec.ticket.titulo,
            cliente_nombre,
            eval_tec.get_calificacion_display(),
            eval_tec.comentario,
            tecnico_nombre
        ]
        sheet.append(row_data)

    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width

    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"satisfaccion_cliente_reporte_{start_date_str or 'todos'}_a_{end_date_str or 'todos'}.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def generar_reporte_clientes_mas_tickets_excel(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido. Use AAAA-MM-DD.")
            return redirect('reportes')

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido. Use AAAA-MM-DD.")
            return redirect('reportes')

    tickets_queryset = Ticket.objects.all()
    if start_date:
        tickets_queryset = tickets_queryset.filter(fecha_creacion__gte=start_date)
    if end_date:
        tickets_queryset = tickets_queryset.filter(fecha_creacion__lte=end_date + timedelta(days=1))

    clientes_tickets = Cliente.objects.annotate(
        num_tickets=Count('tickets', filter=Q(tickets__in=tickets_queryset))
    ).order_by('-num_tickets')

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Clientes con Más Tickets"

    headers = [
        "RUC Cliente", "Nombre Cliente", "Teléfono", "Dirección",
        "Correo", "Anydesk Empresa", "Empresa Asociada", "Número de Tickets"
    ]
    sheet.append(headers)

    # Estilos para encabezados
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="007bff", end_color="007bff", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    header_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    for col_num, header_text in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = header_border
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25


    for cliente in clientes_tickets:
        row_data = [
            cliente.ruc,
            cliente.nombres,
            cliente.telefono,
            cliente.direccion,
            cliente.correo,
            cliente.anydesk_empresa,
            cliente.empresa,
            cliente.num_tickets
        ]
        sheet.append(row_data)

    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width

    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"clientes_mas_tickets_reporte_{start_date_str or 'todos'}_a_{end_date_str or 'todos'}.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Asegúrate de que tu función reportes_view pueda manejar la selección del tipo de reporte.
@login_required
def reportes_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido. Use AAAA-MM-DD.")
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido. Use AAAA-MM-DD.")

    # Call the new report functions
    mttr_img, mttr_info = tiempo_promedio_resolucion_report(start_date, end_date)
    sla_img, outlier_sla_info = tickets_fuera_de_sla_report(start_date, end_date)
    
    # NEW: Call the report for MTTR of outlier technicians
    mttr_outliers_img, mttr_outliers_info = tiempo_promedio_resolucion_outliers_report(start_date, end_date)


    context = {
        'tickets_por_estado_img': tickets_por_estado_report(start_date, end_date),
        'departamentos_incidencias_img': departamentos_incidencias_report(start_date, end_date),
        'tendencia_tickets_por_mes_img': tendencia_tickets_por_mes_report(start_date, end_date),
        'categorias_incidencias_img': categorias_incidencias_report(start_date, end_date),
        'calificacion_tickets_img': calificacion_tickets_report(start_date, end_date),
        'mttr_img': mttr_img,
        'mttr_info': mttr_info,
        'sla_img': sla_img,
        'outlier_sla_info': outlier_sla_info,
        'mttr_outliers_img': mttr_outliers_img,
        'mttr_outliers_info': mttr_outliers_info,
        'start_date_str': start_date_str, # Pasar las fechas para que los filtros persistan
        'end_date_str': end_date_str,
    }

    return render(request, 'reportes.html', context)
