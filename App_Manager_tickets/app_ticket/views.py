from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.shortcuts import render
from django.http import JsonResponse
from .embeddings import TicketSolutionSearch
searcher = TicketSolutionSearch()

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




# Instancia única para no cargar modelo en cada consulta


def chatbox_view(request):
    return render(request, 'chatbox.html')

def chatbox_query(request):
    if request.method == 'POST':
        pregunta = request.POST.get('pregunta', '')
        if pregunta.strip() == '':
            return JsonResponse({'error': 'No se recibió ninguna pregunta'})

        resultados = searcher.query(pregunta, top_k=3)
        respuestas = []
        for r in resultados:
            respuestas.append({
                'ticket_id': r['ticket_id'],
                'problema': r['problema'],
                'solucion': r['solucion'],
                'similitud': r['similitud']
            })

        return JsonResponse({'respuestas': respuestas})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

