from django.db import models

# Create your models here.
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