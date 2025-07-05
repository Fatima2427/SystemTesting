# pruebas/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Prueba, ModuloProyecto, Proyecto, Usuario, Rol

from django.core.files.uploadedfile import SimpleUploadedFile


class UsuarioModeloTest(TestCase):
    def test_crear_usuario_y_rol(self):
        rol = Rol.objects.create(
            nombre='Administrador', caracteristicas='Permisos completos')
        user = User.objects.create_user(username='admin', password='admin123')
        usuario = Usuario.objects.create(user=user, rol=rol)
        self.assertEqual(usuario.user.username, 'admin')
        self.assertEqual(usuario.rol.nombre, 'Administrador')


class VistaLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario1', password='pass123')
        Rol.objects.create(nombre="tester", caracteristicas="Rol de prueba")
        Usuario.objects.create(
            user=self.user, rol=Rol.objects.get(nombre="tester"))

    def test_acceso_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_correcto_redirecciona(self):
        response = self.client.post(reverse('login'), {
            'username': 'usuario1',
            'password': 'pass123'
        })
        self.assertRedirects(response, reverse('inicio'))

    def test_login_incorrecto(self):
        response = self.client.post(reverse('login'), {
            'username': 'usuario1',
            'password': 'incorrecta'
        })
        self.assertContains(
            response, 'Credenciales inválidas', status_code=200)


class SubidaCSVTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        rol = Rol.objects.create(nombre="Tester", caracteristicas="Sube CSVs")
        self.usuario = Usuario.objects.create(user=self.user, rol=rol)
        self.proyecto = Proyecto.objects.create(
            nombre="Proyecto 1", descripcion="desc", fecha="2024-06-01", estado="activo")
        self.modulo = ModuloProyecto.objects.create(
            nombre="Modulo 1", descripcion="desc", fecha="2024-06-02", proyecto=self.proyecto)
        self.client.login(username='testuser', password='testpass')

    def test_subida_csv_valida(self):
        # Crear un CSV temporal de prueba
        contenido = b"Test Name,Status\nprueba_1,PASS\nprueba_1,FAIL\n"
        archivo_csv = SimpleUploadedFile(
            "test.csv", contenido, content_type="text/csv")

        url = reverse('subir_prueba', args=[self.proyecto.pk, self.modulo.pk])
        response = self.client.post(url, {
            'tipo_prueba': 'unit',
            'archivo': archivo_csv
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # verifica que redirige a detalles
        self.assertContains(response, "Detalles de la Prueba")
        self.assertTrue(Prueba.objects.exists())
