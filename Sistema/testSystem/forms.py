# core/forms.py
from django import forms
from .models import Usuario, Proyecto, Prueba, Rol, Reporte


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'contrasena', 'rol']
        widgets = {
            'contrasena': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Aquí puedes agregar hashing de contraseña si es necesario
        if commit:
            user.save()
        return user


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'caracteristicas']


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'id_participante', 'estado']


class PruebaForm(forms.ModelForm):
    class Meta:
        model = Prueba
        fields = ['nombre', 'descripcion', 'archivo_csv']


class SubidaCSVForm(forms.Form):
    archivo = forms.FileField()
