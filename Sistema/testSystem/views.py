
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from django.http import HttpResponse

from .models import Usuario, Proyecto, Prueba, ModuloProyecto, Reporte, Recomendacion, Resultado, Rol
from .forms import UsuarioForm, ProyectoForm, PruebaForm, SubidaCSVForm, RolForm
# Create your views here.
import pandas as pd
from django.core.files.storage import FileSystemStorage


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


def subir_csv(request):
    if request.method == 'POST':
        form = SubidaCSVForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            fs = FileSystemStorage()
            filename = fs.save(archivo.name, archivo)
            ruta = fs.path(filename)

            datos = cargar_datos(ruta)
            resultados = detectar_pruebas_inestables(datos)

            prueba_padre = Prueba.objects.create(
                nombre=archivo.name,
                descripcion='Archivo subido para análisis de pruebas',
                archivo_csv=archivo
            )

            for index, fila in resultados.iterrows():
                Resultado.objects.create(
                    prueba=prueba_padre,
                    nombre_test=fila['Test Name'],
                    tipo_prueba='unit',  # o puedes inferirlo
                    clasificacion_ml='Inestable' if fila['Es Inestable'] == 'Sí' else 'Estable',
                    score_probabilidad_flaky=round(fila['Score'], 2),
                    estado=True
                )
            return redirect('listar_pruebas')
    else:
        form = SubidaCSVForm()
    return render(request, 'pruebas/subir_csv.html', {'form': form})


class inicio(TemplateView):
    template_name = 'index2.html'


# core/views.py
def crear_prueba(request):
    if request.method == 'POST':
        form = PruebaForm(request.POST, request.FILES)
        if form.is_valid():
            prueba = form.save()  # Guarda la Prueba con nombre, descripción y archivo

            # Procesamos el archivo CSV subido
            if prueba.archivo_csv:
                ruta_csv = prueba.archivo_csv.path  # Ruta real en el sistema de archivos
                datos = cargar_datos(ruta_csv)
                resultados = detectar_pruebas_inestables(datos)

                for index, fila in resultados.iterrows():
                    Resultado.objects.create(
                        prueba=prueba,
                        nombre_test=fila['Test Name'],
                        tipo_prueba='unit',  # Cambiar si puedes inferirlo del CSV
                        clasificacion_ml='Inestable' if fila['Es Inestable'] == 'Sí' else 'Estable',
                        score_probabilidad_flaky=round(fila['Score'], 2),
                        estado=True
                    )

            return redirect('listar_pruebas')
    else:
        form = PruebaForm()
    return render(request, 'pruebas/crear_prueba.html', {'form': form})


def listar_pruebas(request):
    pruebas = Prueba.objects.all().order_by('-fecha_creacion')
    return render(request, 'pruebas/listar_pruebas.html', {'pruebas': pruebas})


def detalle_prueba(request, pk):
    prueba = Prueba.objects.get(pk=pk)
    return render(request, 'Pruebas/detalle_prueba.html', {'prueba': prueba})

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
        return redirect('listar_usuarios')
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
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'Proyecto/crear_proyecto.html', {'form': form})


def lista_proyectos(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'Proyecto/lista_proyectos.html', {'proyectos': proyectos})


def index(request):
    return HttpResponse("Estas en la página principal")


def detail(request, question_id):
    return HttpResponse(f"Estás viendo la pregunta número {question_id}")


def result(request, question_id):
    return HttpResponse(f"Estás viendo los resultados de la pregunta {question_id}")


def vote(request, question_id):
    return HttpResponse(f"Estás votando a la pregunta {question_id}")
