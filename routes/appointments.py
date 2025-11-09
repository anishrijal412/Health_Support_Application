# routes/appointments.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.appointment import Appointment
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
@login_required
def index():
    items = (Appointment.query
             .filter_by(user_id=current_user.id)
             .order_by(Appointment.date.asc(), Appointment.time.asc())
             .all())
    return render_template('appointments.html', appointments=items)

@appointments_bp.route('/appointments/new', methods=['POST'])
@login_required
def create():
    title = request.form.get('title')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    description = request.form.get('description')

    if not title or not date_str or not time_str:
        flash('Please fill out Title, Date, and Time.', 'danger')
        return redirect(url_for('appointments.index'))

    try:
        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        flash('Invalid date/time format.', 'danger')
        return redirect(url_for('appointments.index'))

    appt = Appointment(
        user_id=current_user.id,
        title=title,
        date=appt_date,
        time=appt_time,
        description=description
    )
    db.session.add(appt)
    db.session.commit()
    flash('Appointment created successfully!', 'success')
    return redirect(url_for('appointments.index'))

@appointments_bp.route('/appointments/delete/<int:appointment_id>', methods=['POST'])
@login_required
def delete(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('appointments.index'))

    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted.', 'info')
    return redirect(url_for('appointments.index'))


@appointments_bp.route('/appointments/update/<int:appointment_id>', methods=['POST'])
@login_required
def update(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)

    if appt.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('appointments.index'))

    title = request.form.get('title')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    description = request.form.get('description')

    if not title or not date_str or not time_str:
        flash('Please fill out Title, Date, and Time.', 'danger')
        return redirect(url_for('appointments.index'))

    try:
        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        flash('Invalid date/time format.', 'danger')
        return redirect(url_for('appointments.index'))

    appt.title = title
    appt.date = appt_date
    appt.time = appt_time
    appt.description = description

    db.session.commit()
    flash('Appointment updated successfully!', 'success')
    return redirect(url_for('appointments.index'))