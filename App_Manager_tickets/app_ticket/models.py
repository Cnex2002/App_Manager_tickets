from django.db import models


class Empresa(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    ruc = models.CharField(max_length=20, unique=True, blank=False, null=False)
    direccion = models.TextField(blank=False, null=False, default='Dirección no especificada' )
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    direccion = models.TextField(blank=False, null=False,  default='Dirección no especificada')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"
    
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='departamentos')
    observaciones = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.sucursal.nombre}"
    
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombres = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    correo = models.EmailField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.nombres
    
class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, related_name='tickets')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, related_name='tickets')
    tecnico = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, related_name='tickets_asignados')

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
    


class SolucionTicket(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='imagenes')
    ruta_imagen = models.TextField()
    comentario = models.TextField(null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solucion ID {self.ticket.id}"
    
CALIFICACION_CHOICES = [
    (1, '1 - Muy Malo'),
    (2, '2 - Malo'),
    (3, '3 - Regular'),
    (4, '4 - Bueno'),
    (5, '5 - Excelente'),
]

class EvaluacionTecnico(models.Model):
    ticket = models.OneToOneField('Ticket', on_delete=models.CASCADE, related_name='evaluacion')
    calificacion = models.IntegerField(choices=CALIFICACION_CHOICES, null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Evaluación del Ticket #{self.ticket.id} - {self.get_calificacion_display(),}"