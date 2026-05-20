from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Event, Registration
from decorators import role_required

events_bp = Blueprint('events', __name__)


# ─── Catálogo público ────────────────────────────────────────────────────────

@events_bp.route('/catalog')
def catalog():
    """Lista todos los eventos. Accesible sin login."""
    category = request.args.get('category', '')
    query = Event.query

    if category:
        query = query.filter_by(category=category)

    all_events = query.order_by(Event.date.asc()).all()
    categories = db.session.query(Event.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('events/catalog.html',
                           events=all_events,
                           categories=categories,
                           selected_category=category)


# ─── Dashboard del organizador ───────────────────────────────────────────────

@events_bp.route('/dashboard')
@login_required
@role_required('organizer')
def dashboard():
    """Panel del organizador: ve y gestiona sus propios eventos."""
    my_events = Event.query.filter_by(organizer_id=current_user.id)\
                           .order_by(Event.date.asc()).all()
    return render_template('events/dashboard.html', my_events=my_events)


# ─── Detalle de evento ───────────────────────────────────────────────────────

@events_bp.route('/event/<int:event_id>')
def detail(event_id):
    """Muestra el detalle de un evento."""
    event = Event.query.get_or_404(event_id)

    # Verificar si el usuario actual ya está inscrito
    already_registered = False
    if current_user.is_authenticated:
        already_registered = Registration.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first() is not None

    return render_template('events/detail.html',
                           event=event,
                           already_registered=already_registered)


# ─── Crear evento ────────────────────────────────────────────────────────────

@events_bp.route('/event/new', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def create_event():
    """Formulario para crear un nuevo evento."""
    if request.method == 'POST':
        title       = request.form.get('title')
        description = request.form.get('description')
        date_str    = request.form.get('date')
        capacity    = request.form.get('capacity')
        category    = request.form.get('category')

        # Validaciones básicas
        if not all([title, description, date_str, capacity, category]):
            flash('Todos los campos son obligatorios.', 'error')
            return render_template('events/form.html', event=None)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido.', 'error')
            return render_template('events/form.html', event=None)

        event = Event(
            title=title,
            description=description,
            date=date,
            capacity=int(capacity),
            category=category,
            organizer_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash('Evento creado exitosamente.', 'success')
        return redirect(url_for('events.dashboard'))

    return render_template('events/form.html', event=None)


# ─── Editar evento ───────────────────────────────────────────────────────────

@events_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def edit_event(event_id):
    """Editar un evento existente. Solo el organizador dueño puede hacerlo."""
    event = Event.query.get_or_404(event_id)

    # Verificar que el evento pertenece al organizador actual
    if event.organizer_id != current_user.id:
        flash('No tienes permiso para editar este evento.', 'error')
        return redirect(url_for('events.dashboard'))

    if request.method == 'POST':
        title       = request.form.get('title')
        description = request.form.get('description')
        date_str    = request.form.get('date')
        capacity    = request.form.get('capacity')
        category    = request.form.get('category')

        if not all([title, description, date_str, capacity, category]):
            flash('Todos los campos son obligatorios.', 'error')
            return render_template('events/form.html', event=event)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido.', 'error')
            return render_template('events/form.html', event=event)

        # Validar que la nueva capacidad no sea menor a los inscritos actuales
        if int(capacity) < event.spots_taken:
            flash(f'La capacidad no puede ser menor a los inscritos actuales ({event.spots_taken}).', 'error')
            return render_template('events/form.html', event=event)

        event.title       = title
        event.description = description
        event.date        = date
        event.capacity    = int(capacity)
        event.category    = category
        db.session.commit()

        flash('Evento actualizado exitosamente.', 'success')
        return redirect(url_for('events.dashboard'))

    return render_template('events/form.html', event=event)


# ─── Eliminar evento ─────────────────────────────────────────────────────────

@events_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
@role_required('organizer')
def delete_event(event_id):
    """Eliminar un evento. Solo el organizador dueño puede hacerlo."""
    event = Event.query.get_or_404(event_id)

    if event.organizer_id != current_user.id:
        flash('No tienes permiso para eliminar este evento.', 'error')
        return redirect(url_for('events.dashboard'))

    db.session.delete(event)
    db.session.commit()

    flash('Evento eliminado.', 'info')
    return redirect(url_for('events.dashboard'))


# ─── Inscribirse a un evento ─────────────────────────────────────────────────

@events_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
@role_required('attendee')
def register_event(event_id):
    """Un asistente se inscribe a un evento."""
    event = Event.query.get_or_404(event_id)

    # Verificar si ya está inscrito
    existing = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()

    if existing:
        flash('Ya estás inscrito en este evento.', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    if event.is_full:
        flash('Este evento ya no tiene cupos disponibles.', 'error')
        return redirect(url_for('events.detail', event_id=event_id))

    registration = Registration(user_id=current_user.id, event_id=event_id)
    db.session.add(registration)
    db.session.commit()

    flash(f'Te has inscrito a "{event.title}" exitosamente.', 'success')
    return redirect(url_for('events.detail', event_id=event_id))


# ─── Cancelar inscripción ────────────────────────────────────────────────────

@events_bp.route('/event/<int:event_id>/unregister', methods=['POST'])
@login_required
@role_required('attendee')
def unregister_event(event_id):
    """Un asistente cancela su inscripción a un evento."""
    registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first_or_404()

    db.session.delete(registration)
    db.session.commit()

    flash('Inscripción cancelada.', 'info')
    return redirect(url_for('events.detail', event_id=event_id))