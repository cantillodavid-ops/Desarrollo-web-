from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'organizer':
            return redirect(url_for('events.dashboard'))
        return redirect(url_for('events.catalog'))

    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'organizer':
                return redirect(url_for('events.dashboard'))
            return redirect(url_for('events.catalog'))

        flash('Credenciales inválidas', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.catalog'))

    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role')

        if role not in ('organizer', 'attendee'):
            flash('Rol inválido. Elige organizador o asistente.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('auth/register.html')

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
