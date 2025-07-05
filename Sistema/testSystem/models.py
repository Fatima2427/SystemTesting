from django.db import models
from django.contrib.auth.models import User


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    caracteristicas = models.TextField()

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.get_full_name()


class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()
    estado = models.CharField(max_length=50)
    usuarios = models.ManyToManyField(
        Usuario, through='UsuarioProyecto', related_name='proyectos_asignados')

    def __str__(self):
        return self.nombre


class UsuarioProyecto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.proyecto}"


class ModuloProyecto(models.Model):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='modulos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()

    def __str__(self):
        return f"{self.nombre} ({self.proyecto.nombre})"


class Prueba(models.Model):
    tipo_prueba = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='pruebas/')
    fecha = models.DateField(auto_now_add=True)
    modulo = models.ForeignKey(
        ModuloProyecto, on_delete=models.CASCADE, related_name='pruebas')

    def __str__(self):
        return self.tipo_prueba


class Resultado(models.Model):
    prueba = models.ForeignKey(
        'Prueba', related_name='detalles', on_delete=models.CASCADE)

    nombre_test = models.CharField(max_length=200)

    clasificacion_ml = models.CharField(max_length=100, blank=True, null=True)
    score_probabilidad_flaky = models.FloatField(default=0.0)
    detalle_probabilidades = models.JSONField(
        blank=True, null=True)  # 👈 Nuevo campo
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_test} - {self.clasificacion_ml}"


class Reporte(models.Model):
    tipo = models.CharField(max_length=100)  # por módulo o por proyecto
    fecha_generado = models.DateField(auto_now_add=True)
    archivo_pdf = models.FileField(
        upload_to='reportes/', blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes')
    modulo = models.ForeignKey(ModuloProyecto, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='reportes')
    resultados = models.ManyToManyField(Resultado, related_name='reportes')

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo}"
