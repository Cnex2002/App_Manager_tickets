from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from .models import *
from .forms import *

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

def lista_roles(request):
    roles = Rol.objects.all()  
    contexto = {
        'roles': roles
         
    }
    return render(request, 'rol_lista.html', contexto) 

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

def rol_nuevo(request):
    if request.method == 'POST':
        formulario = RolForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_roles')  # Redirige a la lista de roles después de crear el nuevo rol
    else:
        formulario = RolForm()
    contexto = {
        'formulario': formulario
        
    }
    return render(request, 'ticket_nuevo.html', contexto)

def rol_editar(request, id):
    rol = get_object_or_404(Rol, id=id)
    if request.method == 'POST':
        formulario = RolForm(request.POST, instance=rol)
        if formulario.is_valid():
            formulario.save()
            return redirect('lista_roles')
    else:
        formulario = RolForm(instance=rol)
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




def lista_solucionticket(request):
   
    contexto = {
        'solucionticket': SolucionTicket.objects.all(),
    }
    return render(request, 'solucionticket_lista.html', contexto)


from django.utils import timezone

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

