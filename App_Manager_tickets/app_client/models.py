from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombres = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.nombres