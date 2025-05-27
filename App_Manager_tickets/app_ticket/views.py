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
    }
    return render(request, 'empresa_nuevo.html', contexto)

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
        'formulario': formulario,
    }
    return render(request, 'cliente_nuevo.html', contexto)


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
        'formulario': formulario,
    }
    return render(request, 'categoria_nuevo.html', contexto)


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
        'formulario': formulario,
    }
    return render(request, 'sucursal_nuevo.html', contexto)


    
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
        'formulario': formulario,
    }
    return render(request, 'departamento_nuevo.html', contexto)


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
        'formulario': formulario,
    }
    return render(request, 'ticket_nuevo.html', contexto)

#lista de empresas
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

