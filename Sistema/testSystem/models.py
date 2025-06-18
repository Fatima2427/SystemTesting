from django.db import models
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    caracteristicas = models.TextField()

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)  # hashed
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50)
    # Relación con usuarios (si es ManyToMany, ajusta esto)
    id_participante = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class ParticipantesProyecto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.proyecto} ({self.rol})"


class ModuloProyecto(models.Model):
    descripcion = models.TextField()
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="modulos")
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Módulo de {self.proyecto.nombre}"


class Prueba(models.Model):
    tipo_prueba = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='pruebas/')
    fecha = models.DateField()
    modulo = models.ForeignKey(
        ModuloProyecto, on_delete=models.CASCADE, related_name='pruebas')

    def __str__(self):
        return self.tipo_prueba


class Resultado(models.Model):
    prueba = models.ForeignKey(
        Prueba, related_name='detalles', on_delete=models.CASCADE)
    nombre_test = models.CharField(max_length=200)
    tipo_prueba = models.CharField(max_length=50, choices=(
        ('unit', 'Unit'),
        ('integration', 'Integration'),
        ('e2e', 'End to End'),
    ))
    clasificacion_ml = models.CharField(max_length=100, blank=True, null=True)
    score_probabilidad_flaky = models.FloatField(default=0.0)
    estado = models.BooleanField(default=True)  # True: activa, False: inactiva

    def __str__(self):
        return self.nombre_test


class Reporte(models.Model):
    tipo = models.CharField(max_length=100)
    prueba = models.ForeignKey(
        Prueba, on_delete=models.SET_NULL, null=True, blank=True, related_name="reportes")
    parametros = models.TextField(blank=True, null=True)
    fecha_generado = models.DateField(auto_now_add=True)
    modulo = models.ForeignKey(
        ModuloProyecto, on_delete=models.CASCADE, related_name="reportes")

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo}"


class Recomendacion(models.Model):
    prueba = models.ForeignKey(
        Prueba, on_delete=models.CASCADE, related_name="recomendaciones")
    modulo = models.ForeignKey(
        ModuloProyecto, on_delete=models.CASCADE, related_name="recomendaciones")
    contenido = models.TextField()

    def __str__(self):
        return f"Recomendación para {self.prueba.nombre}"
