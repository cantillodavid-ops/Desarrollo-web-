from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user


def role_required(role):
    """Decorador que exige que el usuario autenticado tenga el rol indicado.
    Redirige al login si no está autenticado. Devuelve 403 si el rol no coincide."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator