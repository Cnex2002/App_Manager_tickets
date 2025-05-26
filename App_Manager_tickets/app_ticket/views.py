from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
from .forms import *

def empresa_nueva(request):
    if request.method == 'POST':
        formulario = EmpresaForm(request.POST)
    else:
        formulario = EmpresaForm()
        
    if formulario.is_valid():
        objeto=formulario.save(commit=False)
        objeto.save()
    contexto={
        'formulario':EmpresaForm()
    }
    return render(request,'empresa_nuevo.html',contexto)

def cliente_nueva(request):
    if request.method == 'POST':
        formulario = clienteForm(request.POST)
    else:
        formulario = clienteForm()
        
    if formulario.is_valid():
        objeto=formulario.save(commit=False)
        objeto.save()
    contexto={
        'formulario':clienteForm()
    }
    return render(request,'cliente_nuevo.html',contexto)

def categoria_nueva(request):
    if request.method == 'POST':
        formulario = CategoriaForm(request.POST)
    else:
        formulario = CategoriaForm()
        
    if formulario.is_valid():
        objeto=formulario.save(commit=False)
        objeto.save()
    contexto={
        'formulario':CategoriaForm()
    }
    return render(request,'categoria_nuevo.html',contexto)