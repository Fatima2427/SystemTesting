
from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Usuario, Proyecto, Prueba, ModuloProyecto, Reporte, Recomendacion, Resultado, Rol
from .forms import UsuarioForm, ProyectoForm, PruebaForm, SubidaCSVForm, RolForm, ModuloProyecto, ModuloProyectoForm
# Create your views here.
import pandas as pd
from django.core.files.storage import FileSystemStorage


# pruebas ----------------


def cargar_datos(path):
    df = pd.read_csv(path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by=['Test Name', 'Timestamp'])
    return df


def detectar_pruebas_inestables(df):
    resultados = []
    for test_name, grupo in df.groupby('Test Name'):
        estados = grupo['Status'].tolist()
        cambios = sum(estados[i] != estados[i+1]
                      for i in range(len(estados)-1))
        flaky = cambios >= 2
        resultados.append({
            'Test Name': test_name,
            'Total Runs': len(estados),
            'Cambios de Estado': cambios,
            'Es Inestable': 'Sí' if flaky else 'No',
            'Score': cambios / len(estados)
        })
    return pd.DataFrame(resultados)


def crear_prueba(request):
    if request.method == 'POST':
        form = PruebaForm(request.POST, request.FILES)
        if form.is_valid():
            prueba = form.save()
            if prueba.archivo:
                ruta_csv = prueba.archivo.path
                datos = cargar_datos(ruta_csv)
                resultados = detectar_pruebas_inestables(datos)
                for index, fila in resultados.iterrows():
                    Resultado.objects.create(
                        prueba=prueba,
                        nombre_test=fila['Test Name'],
                        tipo_prueba='unit',
                        clasificacion_ml='Inestable' if fila['Es Inestable'] == 'Sí' else 'Estable',
                        score_probabilidad_flaky=round(fila['Score'], 2),
                        estado=True
                    )
            return redirect('listar_pruebas')
    else:
        form = PruebaForm()
    return render(request, 'pruebas/crear_prueba.html', {'form': form})


def listar_pruebas(request):
    pruebas = Prueba.objects.all().order_by('-fecha')
    return render(request, 'pruebas/listar_pruebas.html', {'pruebas': pruebas})


def ver_prueba(request, pk):
    prueba = Prueba.objects.get(pk=pk)
    return render(request, 'Pruebas/detalle_prueba.html', {'prueba': prueba})


def eliminar_prueba(request, pk):
    prueba = get_object_or_404(Prueba, pk=pk)
    if request.method == 'POST':
        prueba.delete()
        return redirect('listar_pruebas')
    return render(request, 'pruebas/confirmar_eliminar.html', {'prueba': prueba})


class inicio(TemplateView):
    template_name = 'index2.html'


# ----------------------------------------------------------------------Usuarios


def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'Usuario/lista_usuarios.html', {'usuarios': usuarios})


def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(
            initial={'rol': Rol.objects.get_or_create(nombre='Administrador')[0].id})
    return render(request, 'Usuario/crear_usuario.html', {'form': form})


def modificar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if form.is_valid():
        form.save()
        return redirect('lista_usuarios')
    return render(request, 'Usuario/crear_usuario.html', {'form': form})


def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    return redirect('lista_usuarios')

# Roles


def listar_roles(request):
    roles = Rol.objects.all()
    return render(request, 'roles/listar.html', {'roles': roles})


def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_roles')
    else:
        form = RolForm()
    return render(request, 'roles/form.html', {'form': form})


def modificar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if rol.nombre == 'Administrador':
        return redirect('listar_roles')
    form = RolForm(request.POST or None, instance=rol)
    if form.is_valid():
        form.save()
        return redirect('listar_roles')
    return render(request, 'roles/form.html', {'form': form})


def eliminar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if rol.nombre != 'Administrador':
        rol.delete()
    return redirect('listar_roles')


# PROYECTOS --------------------------


def lista_proyectos(request):
    if request.user.is_superuser:
        proyectos = Proyecto.objects.all()
    # else:
     #   proyectos = request.user.proyectos_asignados.all()
    return render(request, 'proyectos/listar.html', {'proyectos': proyectos})


def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()
            proyecto.usuarios.add(request.user)  # Asignar creador
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear.html', {'form': form})


def modificar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if form.is_valid():
        form.save()
        return redirect('lista_proyectos')
    return render(request, 'proyectos/modificar.html', {'form': form})


def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    return redirect('lista_proyectos')


def ver_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    modulos = proyecto.modulos.all()
    return render(request, 'proyectos/ver.html', {'proyecto': proyecto, 'modulos': modulos})

# Módulo de proyectos


def crear_modulo(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    if request.method == 'POST':
        form = ModuloProyectoForm(request.POST)
        if form.is_valid():
            modulo = form.save(commit=False)
            modulo.proyecto = proyecto
            modulo.save()
            return redirect('ver_proyecto', pk=proyecto.id)
    else:
        form = ModuloProyectoForm()
    return render(request, 'modulos/crear.html', {'form': form, 'proyecto': proyecto})


def modificar_modulo(request, pk):
    modulo = get_object_or_404(ModuloProyecto, pk=pk)
    form = ModuloProyectoForm(request.POST or None, instance=modulo)
    if form.is_valid():
        form.save()
        return redirect('ver_proyecto', pk=modulo.proyecto.id)
    return render(request, 'modulos/modificar.html', {'form': form})


def eliminar_modulo(request, pk):
    modulo = get_object_or_404(ModuloProyecto, pk=pk)
    proyecto_id = modulo.proyecto.id
    modulo.delete()
    return redirect('ver_proyecto', pk=proyecto_id)


def ver_modulo(request, pk):
    modulo = get_object_or_404(ModuloProyecto, pk=pk)
    pruebas = modulo.prueba_set.all()  # Asumiendo modelo de prueba relacionado
    return render(request, 'modulos/ver.html', {'modulo': modulo, 'pruebas': pruebas})
