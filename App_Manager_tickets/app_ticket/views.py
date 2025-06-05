from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required



from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import pytz
from django.utils import timezone


#profile
@login_required
def perfil(request):
    if hasattr(request.user, 'usuario'):
        contexto = {}
        return render(request, 'perfil.html', contexto)
    else:
        return redirect('completar_registro')
    
@login_required
def completar_registro(request):
    if request.method == 'POST':
        formulario = UsuarioForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save(commit=False)
            usuario.usuarios = request.user
            usuario.save()
            
            return redirect('lista_empresas')
    else:
        formulario = UsuarioForm()

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
        formulario = TicketForm(request.POST)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()

            return redirect('lista_tickets')
    else:
        formulario = TicketForm()

    contexto = {
        'formulario': formulario
    }
    return render(request, 'ticket_nuevo.html', contexto)

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

def lista_clientes(request):

    contexto = {
        'clientes': Cliente.objects.all(),
    }
    return render(request, 'cliente_lista.html', contexto)


def lista_categorias(request):

    contexto = {
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'categoria_lista.html', contexto)
def lista_sucursales(request):

    contexto = {
        'sucursales': Sucursal.objects.all(),
    }
    return render(request, 'sucursal_lista.html', contexto)
def lista_departamentos(request):

    contexto = {
        'departamentos': Departamento.objects.all(),
    }
    return render(request, 'departamento_lista.html', contexto)
def lista_tickets(request):

    contexto = {
        'tickets': Ticket.objects.all(),
    }
    return render(request, 'ticket_lista.html', contexto)


def lista_evaluaciones(request):
    evaluaciones = EvaluacionTecnico.objects.all()  # Obtiene todas las evaluaciones
    contexto = {
        'evaluaciones': evaluaciones
       
    }
    return render(request, 'evaluacion_tecnico_lista.html', contexto)

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
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        formulario = TicketForm(request.POST, instance=ticket)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_tickets')  # Replace with your actual ticket list URL name
    else:
        formulario = TicketForm(instance=ticket)

    contexto = {
        'formulario': formulario
       
    }
    return render(request, 'ticket_nuevo.html', contexto)





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
        empresa.delete()
        return redirect('lista_empresas')  # Redirige a la lista

    contexto = {
        'objeto': empresa,
        'url_cancelar': reverse('lista_empresas'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

#eliminar
def sucursal_eliminar(request, id):
    sucursal = get_object_or_404(Sucursal, id=id)

    if request.method == 'POST':
        sucursal.delete()
        return redirect('lista_sucursales')  # Redirige a la lista

    contexto = {
        'objeto': sucursal,
        'url_cancelar': reverse('lista_sucursales'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)
def departamento_eliminar(request, id):
    departamento = get_object_or_404(Departamento, id=id)

    if request.method == 'POST':
        departamento.delete()
        return redirect('lista_departamentos')  # Redirige a la lista

    contexto = {
        'objeto': departamento,
        'url_cancelar': reverse('lista_departamentos'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)
def categoria_eliminar(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')  # Redirige a la lista

    contexto = {
        'objeto': categoria,
        'url_cancelar': reverse('lista_categorias'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)
def cliente_eliminar(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')  # Redirige a la lista

    contexto = {
        'objeto': cliente,
        'url_cancelar': reverse('lista_clientes'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)
def ticket_eliminar(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    if request.method == 'POST':
        ticket.delete()
        return redirect('lista_tickets')  # Redirige a la lista

    contexto = {
        'objeto': ticket,
        'url_cancelar': reverse('lista_tickets'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

def evaluacion_eliminar(request, id):
    evaluacion = get_object_or_404(EvaluacionTecnico, id=id)

    if request.method == 'POST':
        evaluacion.delete()
        return redirect('lista_evaluaciones')  # Redirige a la lista

    contexto = {
        'objeto': evaluacion,
        'url_cancelar': reverse('lista_evaluaciones'),  # Usamos reverse() para obtener la URL
    }
    return render(request, 'ticket_eliminar.html', contexto)

#ver tickets del tenico
def ver_tickets_tecnico(request, ):
  
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

            # ACTUALIZAR ESTADO Y FECHA DE CIERRE DEL TICKET
            ticket.estado = 'cerrado'
            ticket.fecha_cierre = timezone.now()
            ticket.save()

            return redirect('lista_tickets')
    else:
        formulario = SolucionTicketForm()

    contexto = {
        'formulario': formulario,
        'ticket': ticket
    }
    return render(request, 'solucionticket_nuevo.html', contexto)


def reportes_view(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    tickets_filtrados = Ticket.objects.all()

    if fecha_inicio_str:
        # Usa pytz.utc aquí
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(tzinfo=pytz.utc)
        tickets_filtrados = tickets_filtrados.filter(fecha_creacion__gte=fecha_inicio)
    
    if fecha_fin_str:
        # Usa pytz.utc aquí
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=pytz.utc)
        tickets_filtrados = tickets_filtrados.filter(fecha_creacion__lte=fecha_fin)


    # KPI: Total Tickets Activos
    total_tickets_activos = tickets_filtrados.exclude(estado='cerrado').count()

    # KPI: Tiempo Promedio Resolución
    tickets_resueltos = tickets_filtrados.filter(estado='cerrado', fecha_cierre__isnull=False)
    tiempo_promedio_resolucion_horas = 0.0
    if tickets_resueltos.exists():
        total_duracion_segundos = 0
        for ticket in tickets_resueltos:
            if ticket.fecha_cierre and ticket.fecha_creacion:
                duracion = ticket.fecha_cierre - ticket.fecha_creacion
                total_duracion_segundos += duracion.total_seconds()
        
        if tickets_resueltos.count() > 0:
            tiempo_promedio_resolucion_horas = (total_duracion_segundos / tickets_resueltos.count()) / 3600 # Convertir a horas
    
    # KPI: Calificación Promedio
    calificacion_promedio = 0.0
    evaluaciones = EvaluacionTecnico.objects.filter(ticket__in=tickets_filtrados, calificacion__isnull=False)
    if evaluaciones.exists():
        calificacion_promedio = evaluaciones.aggregate(avg_cal=Avg('calificacion'))['avg_cal']

    # Tickets por Estado
    tickets_por_estado = tickets_filtrados.values('estado').annotate(count=Count('estado'))

    # Preparar datos para el gráfico de dona
    labels_estados = []
    data_estados = []
    for item in tickets_por_estado:
        labels_estados.append(item['estado'])
        data_estados.append(item['count'])

    # Tickets por Prioridad
    tickets_por_prioridad = tickets_filtrados.values('prioridad').annotate(count=Count('prioridad')).order_by('-count')

    # Preparar datos para el gráfico de barras por prioridad
    labels_prioridad = []
    data_prioridad = []
    for item in tickets_por_prioridad:
        labels_prioridad.append(item['prioridad'].capitalize()) # Capitalizar para una mejor presentación
        data_prioridad.append(item['count'])

    # Nuevo: Tickets por Categoría (Problemas más frecuentes)
    tickets_por_categoria = tickets_filtrados.values('categoria__nombre').annotate(count=Count('categoria__nombre')).order_by('-count')

    # Preparar datos para el gráfico de barras por categoría
    labels_categoria = []
    data_categoria = []
    for item in tickets_por_categoria:
        labels_categoria.append(item['categoria__nombre'])
        data_categoria.append(item['count'])

    # Nuevo: Tickets cerrados por Técnico (Técnicos más productivos)
    tickets_cerrados_por_tecnico = tickets_filtrados.filter(estado='cerrado').values('tecnico__nombre').annotate(count=Count('tecnico__nombre')).order_by('-count')

    # Preparar datos para el gráfico de barras por técnico
    labels_tecnicos = []
    data_tecnicos = []
    for item in tickets_cerrados_por_tecnico:
        labels_tecnicos.append(item['tecnico__nombre'])
        data_tecnicos.append(item['count'])

    # Nuevo: Departamentos con Más Incidencias
    # CORRECCIÓN AQUÍ: Accedemos al departamento a través del técnico
    tickets_por_departamento = tickets_filtrados.values('tecnico__departamento__nombre').annotate(count=Count('tecnico__departamento__nombre')).order_by('-count')

    # Preparar datos para el gráfico de barras por departamento
    labels_departamento = []
    data_departamento = []
    for item in tickets_por_departamento:
        # Asegurarse de que el nombre del departamento no sea None si algún técnico no tiene departamento asignado
        if item['tecnico__departamento__nombre']:
            labels_departamento.append(item['tecnico__departamento__nombre'])
            data_departamento.append(item['count'])


    context = {
        'total_tickets_activos': total_tickets_activos,
        'tiempo_promedio_resolucion': round(tiempo_promedio_resolucion_horas, 2),
        'calificacion_promedio': round(calificacion_promedio, 1) if calificacion_promedio else 0.0,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
        'labels_estados': labels_estados,
        'data_estados': data_estados,
        'labels_prioridad': labels_prioridad,
        'data_prioridad': data_prioridad,
        'labels_categoria': labels_categoria,
        'data_categoria': data_categoria,
        'labels_tecnicos': labels_tecnicos,
        'data_tecnicos': data_tecnicos,
        'labels_departamento': labels_departamento, 
        'data_departamento': data_departamento,     
    }

    return render(request, 'reportes.html', context)