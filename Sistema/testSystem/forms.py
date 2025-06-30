from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Proyecto, Prueba, Rol, Reporte, ModuloProyecto
from django.forms import ModelForm


class LoginForm(forms.Form):
    username = forms.CharField(label='Correo')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear un usuario del sistema y asociarlo al modelo Usuario"""
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1',
                  'password2', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Crea la instancia del modelo Usuario relacionado
        rol = self.cleaned_data['rol']
        Usuario.objects.create(user=user, rol=rol)
        return user


class UsuarioForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True)
    proyectos = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Proyectos asignados (si no es Administrador)"
    )

    class Meta:
        model = Usuario
        fields = ['rol']  # Solo campos del modelo Usuario

    def save(self, commit=True):
        rol = self.cleaned_data['rol']
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        usuario = super().save(commit=False)
        usuario.user = user
        usuario.rol = rol
        if commit:
            usuario.save()
            if rol.nombre.lower() != 'administrador':
                usuario.user.proyectos_asignados.set(
                    self.cleaned_data['proyectos'])
        return usuario


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'caracteristicas']


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'fecha', 'estado']


class ModuloProyectoForm(forms.ModelForm):
    class Meta:
        model = ModuloProyecto
        fields = ['nombre', 'descripcion', 'fecha']


class PruebaForm(forms.ModelForm):
    class Meta:
        model = Prueba
        fields = ['tipo_prueba', 'archivo']


class ReporteForm(forms.ModelForm):
    resultados = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Seleccionar Resultados para el Reporte"
    )

    class Meta:
        model = Reporte
        fields = ['tipo', 'archivo_pdf', 'proyecto', 'modulo', 'resultados']

    def __init__(self, *args, **kwargs):
        super(ReporteForm, self).__init__(*args, **kwargs)
        from .models import Resultado
        self.fields['resultados'].queryset = Resultado.objects.all()


class SubidaCSVForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV de prueba")
