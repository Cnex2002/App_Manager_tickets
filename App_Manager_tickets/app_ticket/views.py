from django.shortcuts import render
from .models import *
from .forms import *

def Empresa_nueva(request):
    contexto={
        'formulario':EmpresaForm()
    }
    return render(request,'Empresa_nuevo.html',contexto)