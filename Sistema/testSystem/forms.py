# core/forms.py
from django import forms
from .models import Usuario, Proyecto, Prueba


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo',
                  'tipo_usuario', 'contraseña', 'estado']
        widgets = {
            'contraseña': forms.PasswordInput(),
        }


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
