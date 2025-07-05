
from .utils import analizar_csv


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .decorators import rol_requerido
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario, Proyecto, Prueba, ModuloProyecto, Reporte, Resultado, Rol
from .forms import LoginForm, CustomUserCreationForm, UsuarioForm, ProyectoForm, PruebaForm, SubidaCSVForm, RolForm, ModuloProyecto, ModuloProyectoForm
from django.contrib.auth.forms import UserChangeForm

# Create your views here.
import pandas as pd
from django.core.files.storage import FileSystemStorage


def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                try:
                    usuario = Usuario.objects.get(user=user)
                    return redirect('inicio')
                   # if usuario.rol.nombre.lower() == 'administrador':
                    # cambia esto por tu vista real
                    #    return redirect('vista_administrador')
                  #  else:
                    # cambia esto por tu vista real
                   #     return redirect('vista_usuario')
                except Usuario.DoesNotExist:
                    error = 'El usuario no tiene un perfil asignado.'
            else:
                error = 'Credenciales inválidas'
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})


class inicio(LoginRequiredMixin, TemplateView):
    template_name = 'index2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.get(user=self.request.user)
        context['usuario'] = usuario
        return context

# Roles

# pruebas ----------------


def cargar_datos(path):
    df = pd.read_csv(path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by=['Test Name', 'Timestamp'])
    return df

# verdadero


@login_required
def subir_prueba(request, proyecto_pk, modulo_pk):
    modulo = get_object_or_404(
        ModuloProyecto, pk=modulo_pk, proyecto_id=proyecto_pk)

    if request.method == 'POST':
        form = PruebaForm(request.POST, request.FILES)
        if form.is_valid():
            prueba = form.save(commit=False)
            prueba.modulo = modulo
            prueba.save()

            # Procesar CSV y obtener resultados
            resultados = analizar_csv(prueba.archivo.path)

            for r in resultados:
                Resultado.objects.create(
                    prueba=prueba,
                    nombre_test=r['nombre_test'],

                    clasificacion_ml=r['clasificacion_ml'],
                    score_probabilidad_flaky=round(
                        r['score_probabilidad_flaky'], 2),
                    detalle_probabilidades=r.get(
                        'detalle_probabilidades'),
                    estado=r['estado']
                )

            return redirect('ver_modulo', proyecto_pk=proyecto_pk, modulo_pk=modulo_pk)
    else:
        form = PruebaForm()

    return render(request, 'pruebas/crear_prueba.html', {'form': form, 'modulo': modulo})


@login_required
def listar_pruebas(request):
    pruebas = Prueba.objects.all().order_by('-fecha')
    return render(request, 'pruebas/listar_pruebas.html', {'pruebas': pruebas})


@login_required
def ver_prueba(request, proyecto_pk, modulo_pk, pk):
    prueba = get_object_or_404(Prueba, pk=pk, modulo_id=modulo_pk)
    return render(request, 'pruebas/detalle_prueba.html', {'prueba': prueba})


@login_required
def eliminar_prueba(request, proyecto_pk, modulo_pk, pk):
    prueba = get_object_or_404(Prueba, pk=pk, modulo_id=modulo_pk)

    prueba.delete()
    return redirect('ver_modulo', proyecto_pk=proyecto_pk, modulo_pk=modulo_pk)


@login_required
@rol_requerido('Administrador')
def lista_usuarios(request):
    usuarios = Usuario.objects.select_related('user', 'rol').all()
    return render(request, 'Usuario/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@rol_requerido('Administrador')
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'Usuario/crear_usuario.html', {'form': form})


@rol_requerido('Administrador')
@login_required
def modificar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    user_instance = usuario.user

    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=user_instance)
        rol_id = request.POST.get('rol')
        if user_form.is_valid():
            user_form.save()
            if rol_id:
                usuario.rol_id = rol_id
                usuario.save()
            return redirect('lista_usuarios')
    else:
        user_form = UserChangeForm(instance=user_instance)

    roles = Rol.objects.all()
    return render(request, 'Usuario/modificar_usuario.html', {
        'form': user_form,
        'usuario': usuario,
        'roles': roles
    })


@login_required
@rol_requerido('Administrador')
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    user_instance = usuario.user
    usuario.delete()
    user_instance.delete()  # Elimina también el usuario del sistema auth
    return redirect('lista_usuarios')


@login_required
@rol_requerido('Administrador')
def listar_roles(request):
    roles = Rol.objects.all()
    return render(request, 'roles/lista_roles.html', {'roles': roles})


@login_required
@rol_requerido('Administrador')
def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_roles')
    else:
        form = RolForm()
    return render(request, 'roles/crear_rol.html', {'form': form})


@login_required
@rol_requerido('Administrador')
def eliminar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if rol.nombre != 'Administrador':
        rol.delete()
    return redirect('listar_roles')


# PROYECTOS --------------------------

@login_required
def lista_proyectos(request):
    usuario = request.user.usuario
    if usuario.rol.nombre.lower() != 'administrador':
        proyectos = usuario.proyectos_asignados.all()
    else:
        proyectos = Proyecto.objects.all()
    return render(request, 'proyecto/lista_proyectos.html', {'proyectos': proyectos})


def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()

            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'proyecto/crear_proyecto.html', {'form': form})


def modificar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if form.is_valid():
        form.save()
        return redirect('lista_proyectos')
    return render(request, 'proyecto/modificar.html', {'form': form})


def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    return redirect('lista_proyectos')


def ver_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    modulos = proyecto.modulos.all()
    return render(request, 'proyecto/lista_modulos.html', {'proyecto': proyecto, 'modulos': modulos})

# Módulo de proyectos


def crear_modulo(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == 'POST':
        form = ModuloProyectoForm(request.POST)
        if form.is_valid():
            modulo = form.save(commit=False)
            modulo.proyecto = proyecto
            modulo.save()
            return redirect('ver_proyecto', pk=proyecto.pk)
    else:
        form = ModuloProyectoForm()

    return render(request, 'modulos/crear_modulo.html', {
        'form': form,
        'proyecto': proyecto
    })


def modificar_modulo(request, proyecto_pk, modulo_pk):
    modulo = get_object_or_404(
        ModuloProyecto, pk=modulo_pk, proyecto_id=proyecto_pk)
    form = ModuloProyectoForm(request.POST or None, instance=modulo)
    if form.is_valid():
        form.save()
        return redirect('ver_proyecto', pk=modulo.proyecto.id)
    return render(request, 'modulos/modificar.html', {'form': form})


def eliminar_modulo(request, proyecto_pk, modulo_pk):
    modulo = get_object_or_404(
        ModuloProyecto, pk=modulo_pk, proyecto_id=proyecto_pk)
    proyecto_id = modulo.proyecto.id
    modulo.delete()
    return redirect('ver_proyecto', pk=proyecto_id)


def ver_modulo(request, proyecto_pk, modulo_pk):
    modulo = get_object_or_404(
        ModuloProyecto, pk=modulo_pk, proyecto_id=proyecto_pk)
    pruebas = modulo.pruebas.all()  # si related_name='pruebas'
    return render(request, 'pruebas/listar_pruebas.html', {
        'modulo': modulo,
        'proyecto': modulo.proyecto,
        'pruebas': pruebas
    })
