from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Registration

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile')
@login_required
def profile():
    """Muestra el perfil del usuario actual."""
    # Si es asistente, también mostramos sus eventos inscritos
    registrations = []
    if current_user.is_attendee():
        registrations = Registration.query\
            .filter_by(user_id=current_user.id)\
            .order_by(Registration.registered_at.desc())\
            .all()

    return render_template('users/profile.html',
                           user=current_user,
                           registrations=registrations)


@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Permite al usuario editar su bio y nombre de usuario."""
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_bio      = request.form.get('bio', '')

        # Verificar que el nuevo username no esté tomado por otro usuario
        from models import User
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != current_user.id:
            flash('Ese nombre de usuario ya está en uso.', 'error')
            return render_template('users/edit_profile.html', user=current_user)

        current_user.username = new_username
        current_user.bio      = new_bio
        db.session.commit()

        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('users.profile'))

    return render_template('users/edit_profile.html', user=current_user)