from django.shortcuts import redirect
from functools import wraps


def rol_requerido(nombre_rol):
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if hasattr(request.user, 'usuario') and request.user.usuario.rol.nombre.lower() == nombre_rol.lower():
                    return view_func(request, *args, **kwargs)
            # puedes crear una vista para esto
            return redirect('acceso_denegado')
        return _wrapped_view
    return decorador
