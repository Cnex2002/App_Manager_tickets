from django import forms
from .models import *
from django.contrib.auth.models import User

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'ruc', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }
class clienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['ruc', 'nombres', 'telefono', 'direccion', 'correo', 'anydesk_empresa', 'empresa']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.TextInput(attrs={'class': 'form-control'}),
            'anydesk_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class SucursalForm(forms.ModelForm):
    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'empresa','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

#DepartamentoForm 
class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'sucursal','observaciones','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }




class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'estado', 'prioridad', 'categoria', 'cliente', 'tecnico']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tecnico': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Extraer 'request' de los kwargs antes de llamar al super().__init__
        request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)

        # Si hay un request y el usuario está autenticado
        if request and request.user.is_authenticated:
            try:
                # Intentar obtener el objeto Usuario personalizado
                usuario_personalizado = request.user.usuario
                rol_usuario = usuario_personalizado.rol

                # Aplicar lógica de filtrado si el rol es 'atencion' o 'supervisor'
                if rol_usuario in ['atencion', 'supervisor']:
                    departamento_usuario = usuario_personalizado.departamento
                    if departamento_usuario:
                        # Filtrar técnicos: rol 'tecnico' Y del mismo departamento
                        self.fields['tecnico'].queryset = Usuario.objects.filter(
                            rol='tecnico',
                            departamento=departamento_usuario
                        )
                    else:
                        # Si el usuario (atención/supervisor) no tiene departamento, no se muestran técnicos
                        self.fields['tecnico'].queryset = Usuario.objects.none()
                else:
                    # Si el rol NO es 'atencion' o 'supervisor', mostrar todos los técnicos
                    self.fields['tecnico'].queryset = Usuario.objects.filter(rol='tecnico')
            except Usuario.DoesNotExist:
                # Manejar el caso en que request.user.usuario no exista (aunque debería, si el sistema es consistente)
                # Por seguridad o fallback, mostrar todos los técnicos con rol 'tecnico'
                self.fields['tecnico'].queryset = Usuario.objects.filter(rol='tecnico')
        else:
            # Si no hay usuario autenticado (ej. formulario en una vista pública, lo cual no es el caso aquí
            # porque la vista es @login_required, pero es buena práctica), mostrar todos los técnicos.
            self.fields['tecnico'].queryset = Usuario.objects.filter(rol='tecnico')



class EvaluacionTecnicoForm(forms.ModelForm):
    class Meta:
        model = EvaluacionTecnico
        fields = ['ticket', 'calificacion', 'comentario', 'fecha_evaluacion']
        widgets = {
            'ticket': forms.Select(attrs={'class': 'form-control'}),
            'calificacion': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_evaluacion': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # <-- Agrega esta línea
            ),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs['multiple'] = 'multiple'
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            result = []
            for file in data:
                result.append(super().clean(file, initial))
            return result
        return super().clean(data, initial)

class SolucionTicketForm(forms.ModelForm):
    imagenes = MultipleFileField(
        required=False,
        label='Subir imágenes',
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'file-input'
        })
    )
    
    class Meta:
        model = SolucionTicket
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe la solución...'
            }),
        }





class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'rol', 'departamento']
        widgets = {
            #'usuarios': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }


class UsuarioForm2(forms.ModelForm):
    rol = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['nombre', 'rol', 'departamento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra las opciones de rol para excluir 'administrador'
        ROLES_CHOICES_FILTRADOS = [
            (value, label) for value, label in self.instance._meta.get_field('rol').choices
            if value != 'admin'
        ]
        self.fields['rol'].choices = ROLES_CHOICES_FILTRADOS


# Nuevo formulario para editar el User de Django
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ESTA ES LA ÚNICA DEFINICIÓN CORRECTA DE UserEditForm
class PerfilUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        # Eliminé 'is_staff' y 'is_superuser' para que el usuario no los edite.
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            # Username de solo lectura.
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            
        }

# Nuevo formulario para editar el perfil del usuario (sin permitir cambiar el rol)
class PerfilUsuarioEditForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'departamento'] # Excluye 'rol'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }