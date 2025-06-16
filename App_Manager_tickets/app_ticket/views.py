from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test



from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
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
            except Exception as e:
                messages.error(request, f'Ticket creado pero no se pudo enviar el correo de notificación: {e}')

            return redirect('lista_tickets')  # Redirige a la lista de tickets
    else:
        # Pasar el request al formulario
        formulario = TicketForm(request=request)
    return render(request, 'ticket_nuevo.html', {'formulario': formulario, 'titulo': 'Crear Nuevo Ticket'})









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



def lista_soluciontickets(request):
    soluciones = SolucionTicket.objects.all().select_related('ticket').prefetch_related('imagenes')
    contexto = {
        'soluciones': soluciones,
    }
    return render(request, 'solucionticket_lista.html', contexto)


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
        # Pasar el request al formulario
        formulario = TicketForm(request.POST, instance=ticket, request=request)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.save()
            return redirect('lista_tickets')  
    else:
        # Pasar el request al formulario
        formulario = TicketForm(instance=ticket, request=request)

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

            return redirect('lista_tickets')
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
def chatbox_query(request):
    # Verifica que la solicitud sea de tipo POST
    if request.method == 'POST':
        # Obtiene la pregunta enviada desde el formulario o petición AJAX
        pregunta = request.POST.get('pregunta', '')

        # Verifica que la pregunta no esté vacía
        if pregunta.strip() == '':
            return JsonResponse({'error': 'No se recibió ninguna pregunta'})

        # Llama al sistema inteligente (motor de búsqueda semántica) para obtener respuestas similares
        resultados = searcher.query(pregunta, top_k=3)

        # Construye la lista de respuestas que se enviará al frontend
        respuestas = []
        for r in resultados:
            respuestas.append({
                'ticket_id': r['ticket_id'],     # ID del ticket relacionado
                'problema': r['problema'],       # Problema registrado en el sistema
                'solucion': r['solucion'],       # Solución asociada al ticket
                'similitud': r['similitud']      # Grado de similitud con la pregunta del usuario
            })

        # Devuelve las respuestas como un JSON al cliente (chatbox)
        return JsonResponse({'respuestas': respuestas})

    # Si no se utiliza el método POST, retorna error 405 (Método no permitido)
    return JsonResponse({'error': 'Método no permitido'}, status=405)



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

@login_required
def generar_reporte_excel(request):
    reporte_tipo = request.GET.get('reporte_tipo')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Verificar si las fechas están presentes
    if not fecha_inicio_str or not fecha_fin_str:
        messages.error(request, "Por favor, seleccione una fecha de inicio y una fecha de fin para generar el reporte.")
        return redirect('reportes') # Redirige de vuelta a la página de reportes

    tickets_base_query = Ticket.objects.all()

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(tzinfo=pytz.utc)
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=pytz.utc)
    except ValueError:
        messages.error(request, "Por favor, seleccione un rango de fechas válido." , extra_tags='danger')
        return redirect('reportes')

    # Aplicar filtros de fecha a la consulta base
    tickets_base_query = tickets_base_query.filter(
        fecha_creacion__gte=fecha_inicio,
        fecha_creacion__lte=fecha_fin
    )

    if reporte_tipo == 'tickets_estado_prioridad':
        # ... (código existente para reporte_tipo 'tickets_estado_prioridad') ...
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_tickets_estado_prioridad.xlsx"'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Tickets por Estado y Prioridad"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid") # Azul oscuro
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Encabezados
        # Quitamos 'Sucursal' y 'Departamento' porque ya no existen en Cliente
        headers = [
            "Título", "Descripción", "Estado", "Prioridad", 
            "Categoría", "Cliente", "Técnico Asignado", "Fecha Creación", "Fecha Cierre"
        ]
        sheet.append(headers)

        # Aplicar estilos a los encabezados
        for col_num, cell in enumerate(sheet[1], 1):
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 20 # Ancho por defecto

        # Datos
        # select_related sigue siendo 'cliente', 'tecnico', 'categoria'
        # La consulta base `tickets_base_query` ya tiene los filtros de fecha aplicados
        tickets = tickets_base_query.select_related(
            'cliente', 'tecnico', 'categoria'
        ).order_by('fecha_creacion')

        for ticket in tickets:
            cliente_nombre = ticket.cliente.nombres if ticket.cliente else 'N/A'
            
            # Acceso a empresa: Ahora es un CharField directo
            empresa_nombre = 'N/A'
            if ticket.cliente and ticket.cliente.empresa:
                empresa_nombre = ticket.cliente.empresa # Acceso directo, no .nombre

            categoria_nombre = ticket.categoria.nombre if ticket.categoria else 'N/A'
            
            cliente_info = ''
            if cliente_nombre != 'N/A' and empresa_nombre != 'N/A':
                cliente_info = f"{cliente_nombre} ({empresa_nombre})"
            elif cliente_nombre != 'N/A':
                cliente_info = cliente_nombre
            elif empresa_nombre != 'N/A':
                cliente_info = f"({empresa_nombre})"


            tecnico_asignado = 'No Asignado'
            if ticket.tecnico and ticket.tecnico.usuarios:
                tecnico_asignado = ticket.tecnico.usuarios.username
            elif ticket.tecnico: # Si tiene objeto Tecnico pero no usuario asignado (quizás caso borde)
                tecnico_asignado = f"Técnico sin usuario ({ticket.tecnico.pk})"


            fecha_creacion_str = ''
            if ticket.fecha_creacion:
                fecha_creacion_str = ticket.fecha_creacion.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')

            fecha_cierre_str = 'N/A'
            if ticket.fecha_cierre:
                fecha_cierre_str = ticket.fecha_cierre.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')


            sheet.append([
                ticket.titulo,
                ticket.descripcion,
                ticket.get_estado_display(), # Usa get_estado_display() para el valor legible
                ticket.get_prioridad_display(), # Usa get_prioridad_display() para el valor legible
                categoria_nombre,
                cliente_info,
                tecnico_asignado,
                fecha_creacion_str,
                fecha_cierre_str,
            ])
        
        # Ajustar ancho de columnas automáticamente
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter # Get the column name
            for cell in col:
                try: # Necessary to avoid error on empty cells
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width

        workbook.save(response)
        return response
    
    elif reporte_tipo == 'rendimiento_tickets_categoria':
        # ... (código existente para reporte_tipo 'rendimiento_tickets_categoria') ...
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_rendimiento_tickets_categoria.xlsx"'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Rendimiento por Categoría"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid") # Azul oscuro
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Encabezados
        headers = [
            "Categoría", "Número Total de Tickets", "Tickets Abiertos", 
            "Tickets En Proceso", "Tickets Cerrados", "Tiempo Promedio de Cierre (Horas)"
        ]
        sheet.append(headers)

        # Aplicar estilos a los encabezados
        for col_num, cell in enumerate(sheet[1], 1):
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25 # Ancho por defecto

        # Datos para el reporte de rendimiento por categoría
        categorias = Categoria.objects.all()

        for categoria in categorias:
            # Aplicar el filtro de fecha a las consultas de tickets por categoría
            # La consulta base `tickets_base_query` ya tiene los filtros de fecha aplicados
            total_tickets = tickets_base_query.filter(categoria=categoria).count()
            tickets_abiertos = tickets_base_query.filter(categoria=categoria, estado='abierto').count()
            tickets_en_proceso = tickets_base_query.filter(categoria=categoria, estado='en proceso').count()
            tickets_cerrados = tickets_base_query.filter(categoria=categoria, estado='cerrado').count()

            # Calcular tiempo promedio de cierre
            tiempo_cierre_tickets = tickets_base_query.filter(
                categoria=categoria, 
                estado='cerrado', 
                fecha_cierre__isnull=False
            ).annotate(
                tiempo_diff=ExpressionWrapper(
                    F('fecha_cierre') - F('fecha_creacion'),
                    output_field=DurationField()
                )
            ).aggregate(avg_tiempo_cierre=Avg('tiempo_diff'))

            tiempo_promedio_cierre_horas = 'N/A'
            if tiempo_cierre_tickets['avg_tiempo_cierre']:
                total_seconds = tiempo_cierre_tickets['avg_tiempo_cierre'].total_seconds()
                tiempo_promedio_cierre_horas = round(total_seconds / 3600, 2)

            sheet.append([
                categoria.nombre,
                total_tickets,
                tickets_abiertos,
                tickets_en_proceso,
                tickets_cerrados,
                tiempo_promedio_cierre_horas,
            ])
        
        # Ajustar ancho de columnas automáticamente
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

        workbook.save(response)
        return response

    elif reporte_tipo == 'rendimiento_tecnicos_individuales':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_rendimiento_tecnicos.xlsx"'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Rendimiento de Técnicos"

        # Estilos (reutilizar los ya definidos o definir nuevos si es necesario)
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid") # Azul oscuro
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Encabezados del reporte
        headers = [
            "Técnico",
            "Número Total de Tickets Asignados",
            "Tickets Cerrados",
            "Tickets Abiertos/En Proceso",
            "Tiempo Promedio de Resolución (Horas)",
            "Calificación Promedio Recibida"
        ]
        sheet.append(headers)

        # Aplicar estilos a los encabezados
        for col_num, cell in enumerate(sheet[1], 1):
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 30 # Ancho por defecto

        # Datos para el reporte de rendimiento por técnico
        # Obtenemos todos los técnicos que tienen tickets asignados en el rango de fechas
        tecnicos = Usuario.objects.filter(tickets_asignados__in=tickets_base_query).distinct()

        for tecnico in tecnicos:
            tecnico_nombre = tecnico.nombre 
            
            # Filtramos los tickets para este técnico dentro del rango de fechas
            tickets_tecnico = tickets_base_query.filter(tecnico=tecnico)

            total_tickets_asignados = tickets_tecnico.count()
            tickets_cerrados = tickets_tecnico.filter(estado='cerrado').count()
            tickets_abiertos_en_proceso = tickets_tecnico.filter(estado__in=['abierto', 'en proceso']).count()

            # Calcular tiempo promedio de resolución para este técnico
            tickets_resueltos_tecnico = tickets_tecnico.filter(estado='cerrado', fecha_cierre__isnull=False)
            tiempo_promedio_resolucion_horas = 'N/A'
            if tickets_resueltos_tecnico.exists():
                total_duracion_segundos = 0
                for ticket in tickets_resueltos_tecnico:
                    if ticket.fecha_cierre and ticket.fecha_creacion:
                        duracion = ticket.fecha_cierre - ticket.fecha_creacion
                        total_duracion_segundos += duracion.total_seconds()
                
                if tickets_resueltos_tecnico.count() > 0:
                    tiempo_promedio_resolucion_horas = round((total_duracion_segundos / tickets_resueltos_tecnico.count()) / 3600, 2) # Convertir a horas
            
            # Calcular calificación promedio
            calificaciones_tecnico = EvaluacionTecnico.objects.filter(ticket__in=tickets_resueltos_tecnico, calificacion__isnull=False)
            calificacion_promedio = 'N/A'
            if calificaciones_tecnico.exists():
                calificacion_promedio = round(calificaciones_tecnico.aggregate(avg_cal=Avg('calificacion'))['avg_cal'], 1)

            sheet.append([
                tecnico_nombre,
                total_tickets_asignados,
                tickets_cerrados,
                tickets_abiertos_en_proceso,
                tiempo_promedio_resolucion_horas,
                calificacion_promedio,
            ])
        
        # Ajustar ancho de columnas automáticamente
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

        workbook.save(response)
        return response

    elif reporte_tipo == 'evaluaciones_clientes':  # Nuevo tipo de reporte
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_evaluaciones_clientes.xlsx"'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Evaluaciones de Clientes"

        # Estilos (reutilizar los ya definidos)
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Encabezados del reporte
        headers = [
            "ID del Ticket", 
            "Título del Ticket", 
            "Calificación", 
            "Comentario de Evaluación", 
            "Fecha de Evaluación", 
            "Cliente", 
            "Técnico Asignado"
        ]
        sheet.append(headers)

        # Aplicar estilos a los encabezados
        for col_num, cell in enumerate(sheet[1], 1):
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25 # Ancho por defecto

        # Obtener evaluaciones dentro del rango de fechas
        # Filtramos las evaluaciones que están asociadas a tickets dentro del rango de fechas
        evaluaciones = EvaluacionTecnico.objects.filter(
            ticket__fecha_creacion__gte=fecha_inicio,
            ticket__fecha_creacion__lte=fecha_fin
        ).select_related('ticket', 'ticket__cliente', 'ticket__tecnico', 'ticket__tecnico__usuarios').order_by('fecha_evaluacion')

        for eval_obj in evaluaciones:
            ticket_id = eval_obj.ticket.id
            ticket_titulo = eval_obj.ticket.titulo
            calificacion = eval_obj.calificacion if eval_obj.calificacion is not None else 'N/A'
            comentario = eval_obj.comentario if eval_obj.comentario else 'Sin comentario'
            
            fecha_evaluacion_str = ''
            if eval_obj.fecha_evaluacion:
                fecha_evaluacion_str = eval_obj.fecha_evaluacion.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
            
            cliente_nombre = eval_obj.ticket.cliente.nombres if eval_obj.ticket.cliente else 'N/A'
            
            tecnico_asignado = 'No Asignado'
            if eval_obj.ticket.tecnico and eval_obj.ticket.tecnico.usuarios:
                tecnico_asignado = eval_obj.ticket.tecnico.usuarios.username
            elif eval_obj.ticket.tecnico:
                tecnico_asignado = f"Técnico sin usuario ({eval_obj.ticket.tecnico.pk})"

            sheet.append([
                ticket_id,
                ticket_titulo,
                calificacion,
                comentario,
                fecha_evaluacion_str,
                cliente_nombre,
                tecnico_asignado,
            ])
        
        # Ajustar ancho de columnas automáticamente
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

        workbook.save(response)
        return response

    elif reporte_tipo == 'rendimiento_departamentos': # Nuevo reporte por departamento
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_rendimiento_departamentos.xlsx"'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Rendimiento por Departamento"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        # Encabezados
        headers = [
            "Departamento", 
            "Categoría Más Usada", 
            "Tickets Cerrados", 
            "Tickets Abiertos", 
            "Calificación Promedio"
        ]
        sheet.append(headers)

        # Aplicar estilos a los encabezados
        for col_num, cell in enumerate(sheet[1], 1):
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25

        # Datos para el reporte de rendimiento por departamento
        departamentos = Departamento.objects.all()

        for departamento in departamentos:
            departamento_nombre = departamento.nombre
            
            # Filtrar tickets asociados a este departamento (a través de los técnicos)
            tickets_departamento = tickets_base_query.filter(tecnico__departamento=departamento)

            # Categoría más usada
            categoria_mas_usada = 'N/A'
            top_categoria = tickets_departamento.values('categoria__nombre').annotate(
                count=Count('categoria__nombre')
            ).order_by('-count').first()
            if top_categoria and top_categoria['categoria__nombre']:
                categoria_mas_usada = top_categoria['categoria__nombre']

            # Tickets cerrados y abiertos
            tickets_cerrados = tickets_departamento.filter(estado='cerrado').count()
            tickets_abiertos = tickets_departamento.filter(estado='abierto').count()

            # Calificación promedio
            calificacion_promedio_departamento = 'N/A'
            evaluaciones_departamento = EvaluacionTecnico.objects.filter(
                ticket__in=tickets_departamento, 
                calificacion__isnull=False
            )
            if evaluaciones_departamento.exists():
                calificacion_promedio_departamento = round(
                    evaluaciones_departamento.aggregate(avg_cal=Avg('calificacion'))['avg_cal'], 1
                )

            sheet.append([
                departamento_nombre,
                categoria_mas_usada,
                tickets_cerrados,
                tickets_abiertos,
                calificacion_promedio_departamento,
            ])
        
        # Ajustar ancho de columnas automáticamente
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

        workbook.save(response)
        return response

    return HttpResponse("Tipo de reporte no válido", status=400)


# Vistas para Usuarios


@login_required
@user_passes_test(is_staff_check)
def usuario_lista(request):
    usuarios_personalizados = Usuario.objects.all().select_related('usuarios', 'departamento')
    contexto = {
        'usuarios': usuarios_personalizados,
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
    usuario_personalizado.delete()
    user_django.delete()
    messages.success(request, 'Usuario eliminado correctamente.')
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
    usuario_tecnico = get_object_or_404(Usuario, usuarios=request.user) # Corrected field name here
    
    # Obtener todos los tickets asignados a este técnico
    tickets = Ticket.objects.filter(tecnico=usuario_tecnico).order_by('-fecha_creacion')
    
    context = {
        'tickets': tickets,
        'titulo': 'Mis Tickets Asignados'
    }
    return render(request, 'tecnico_ticket.html', context)
