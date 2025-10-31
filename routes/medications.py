# routes/medications.py
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.medication import Medication
from models.medical_history import MedicalHistory
from models.profile import Profile
from datetime import datetime

medications_bp = Blueprint('medications', __name__)

# ➕ ADD MEDICATION
@medications_bp.route('/medications/add', methods=['POST'])
@login_required
def add_medication():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your profile first.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    history_id = request.form.get('medical_history_id')
    history = MedicalHistory.query.get_or_404(history_id)
    if history.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    med = Medication(
        medical_history_id=history.id,
        name=request.form.get('name'),
        dosage=request.form.get('dosage'),
        frequency=request.form.get('frequency'),
        start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None,
        end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None,
        reminder_time=datetime.strptime(request.form.get('reminder_time'), '%H:%M').time() if request.form.get('reminder_time') else None,
        notes=request.form.get('notes')
    )

    db.session.add(med)
    db.session.commit()
    flash('Medication added successfully.', 'success')
    return redirect(url_for('profile.manage_profile'))


# ✏ UPDATE MEDICATION
@medications_bp.route('/medications/<int:med_id>/update', methods=['POST'])
@login_required
def update_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile or med.medical_history.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    med.name = request.form.get('name')
    med.dosage = request.form.get('dosage')
    med.frequency = request.form.get('frequency')
    med.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None
    med.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
    med.reminder_time = datetime.strptime(request.form.get('reminder_time'), '%H:%M').time() if request.form.get('reminder_time') else None
    med.notes = request.form.get('notes')

    db.session.commit()
    flash('Medication updated successfully.', 'success')
    return redirect(url_for('profile.manage_profile'))


# 🗑 DELETE MEDICATION (optional)
@medications_bp.route('/medications/<int:med_id>/delete', methods=['POST'])
@login_required
def delete_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile or med.medical_history.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    db.session.delete(med)
    db.session.commit()
    flash('Medication deleted.', 'info')
    return redirect(url_for('profile.manage_profile'))
