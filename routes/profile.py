# routes/profile.py
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.profile import Profile
from models.medical_history import MedicalHistory
from models.medication import Medication
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

# -------- PROFILE: view + create/update ----------
@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        creating = False
        if not profile:
            profile = Profile(user_id=current_user.id)
            db.session.add(profile)
            creating = True

        profile.full_name    = (request.form.get('full_name') or '').strip()
        profile.age          = int(request.form['age']) if request.form.get('age') else None
        profile.gender       = request.form.get('gender') or None
        profile.ssn          = request.form.get('ssn') or None
        profile.email        = request.form.get('email') or None
        profile.phone_number = request.form.get('phone_number') or None
        profile.address      = request.form.get('address') or None

        db.session.commit()
        flash('Profile created successfully!' if creating else 'Profile updated successfully!', 'success')
        return redirect(url_for('profile.manage_profile'))

    histories = MedicalHistory.query.filter_by(profile_id=profile.id)\
        .order_by(MedicalHistory.created_at.desc()).all() if profile else []
    return render_template('profile.html', profile=profile, medical_histories=histories)


# -------- PROFILE: delete ----------
@profile_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('No profile to delete.', 'info')
        return redirect(url_for('profile.manage_profile'))

    db.session.delete(profile)
    db.session.commit()
    flash('Profile deleted successfully.', 'info')
    return redirect(url_for('profile.manage_profile'))


# -------- MEDICAL HISTORY: add ----------
@profile_bp.route('/profile/medical-history', methods=['POST'])
@login_required
def add_medical_history():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your profile before adding medical records.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    disease     = (request.form.get('disease') or '').strip()
    doctor      = request.form.get('doctor') or None
    description = request.form.get('description') or None

    if not disease:
        flash('Disease/Condition is required.', 'warning')
        return redirect(url_for('profile.manage_profile'))
    report_upload = request.files.get('report_file')
    report_filename = None
    if report_upload and report_upload.filename:
        if not _allowed_report(report_upload.filename):
            flash('Only PDF report files are allowed.', 'warning')
            return redirect(url_for('profile.manage_profile'))
        report_filename = _save_report_file(report_upload)

    rec = MedicalHistory(
        profile_id=profile.id,
        disease=disease,
        doctor=doctor,
        description=description,
        report_filename=report_filename
    )
    db.session.add(rec)
    db.session.commit()
    flash('Medical record added.', 'success')
    return redirect(url_for('profile.manage_profile'))


# -------- MEDICAL HISTORY: edit ----------
@profile_bp.route('/profile/medical-history/<int:record_id>/edit', methods=['POST'])
@login_required
def edit_medical_history(record_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your profile first.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    rec = MedicalHistory.query.get_or_404(record_id)
    if rec.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    rec.disease     = (request.form.get('disease') or '').strip()
    rec.doctor      = request.form.get('doctor') or None
    rec.description = request.form.get('description') or None
    report_upload = request.files.get('report_file')
    if report_upload and report_upload.filename:
        if not _allowed_report(report_upload.filename):
            flash('Only PDF report files are allowed.', 'warning')
            return redirect(url_for('profile.manage_profile'))
        _delete_report_file(rec.report_filename)
        rec.report_filename = _save_report_file(report_upload)

    if not rec.disease:
        flash('Disease/Condition is required.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    db.session.commit()
    flash('Medical record updated.', 'success')
    return redirect(url_for('profile.manage_profile'))


# -------- MEDICAL HISTORY: delete ----------
@profile_bp.route('/profile/medical-history/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_medical_history(record_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Create your profile first.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    rec = MedicalHistory.query.get_or_404(record_id)
    if rec.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))
    
    _delete_report_file(rec.report_filename)

    db.session.delete(rec)
    db.session.commit()
    flash('Medical record deleted.', 'info')
    return redirect(url_for('profile.manage_profile'))

profile_bp.route('/profile/medical-history/<int:record_id>/report', methods=['GET'])

@profile_bp.route('/profile/medical-history/<int:record_id>/report', methods=['GET'])
@profile_bp.route(
    '/profile/medical-history/<int:record_id>/report',
    methods=['GET'],
    endpoint='view_medical_report'
)
@login_required

def serve_medical_report(record_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    rec = MedicalHistory.query.get_or_404(record_id)

    if not profile or rec.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    if not rec.report_filename:
        flash('No report available for this record.', 'info')
        return redirect(url_for('profile.manage_profile'))

    folder = current_app.config['MEDICAL_REPORT_UPLOAD_FOLDER']
    
    return send_from_directory(
        folder,
        rec.report_filename,
        mimetype='application/pdf',
        as_attachment=False
    )

# -------- MEDICATION: add (multiple allowed) ----------
@profile_bp.route('/profile/medical-history/<int:record_id>/medication', methods=['POST'])
@login_required
def add_medication(record_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    rec = MedicalHistory.query.get_or_404(record_id)
    if not profile or rec.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    reminder_time_str = request.form.get('reminder_time')

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    reminder_time = datetime.strptime(reminder_time_str, '%H:%M').time() if reminder_time_str else None

    med = Medication(
        medical_history_id=rec.id,
        name=(request.form.get('name') or '').strip(),
        dosage=(request.form.get('dosage') or None),
        frequency=(request.form.get('frequency') or None),
        start_date=start_date,
        end_date=end_date,
        reminder_time=reminder_time,
        notes=(request.form.get('notes') or None)
    )

    if not med.name:
        flash('Medication name is required.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    db.session.add(med)
    db.session.commit()
    flash('Medication added.', 'success')
    return redirect(url_for('profile.manage_profile'))


# -------- MEDICATION: edit (inside details) ----------
@profile_bp.route('/profile/medication/<int:med_id>/edit', methods=['POST'])
@login_required
def edit_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile or med.medical_history.profile_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('profile.manage_profile'))

    med.name = (request.form.get('name') or '').strip()
    med.dosage = request.form.get('dosage') or None
    med.frequency = request.form.get('frequency') or None

    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    reminder_time_str = request.form.get('reminder_time')

    med.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    med.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    med.reminder_time = datetime.strptime(reminder_time_str, '%H:%M').time() if reminder_time_str else None
    med.notes = request.form.get('notes') or None

    if not med.name:
        flash('Medication name is required.', 'warning')
        return redirect(url_for('profile.manage_profile'))

    db.session.commit()
    flash('Medication updated.', 'success')
    return redirect(url_for('profile.manage_profile'))


# -------- MEDICATION: delete ----------
@profile_bp.route('/profile/medication/<int:med_id>/delete', methods=['POST'])
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


def _allowed_report(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config.get('MEDICAL_REPORT_ALLOWED_EXTENSIONS', set())
    )


def _save_report_file(upload):
    if not upload or not upload.filename:
        return None

    if not _allowed_report(upload.filename):
        return None

    folder = current_app.config['MEDICAL_REPORT_UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    safe_name = secure_filename(upload.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload.save(os.path.join(folder, unique_name))
    return unique_name


def _delete_report_file(filename):
    if not filename:
        return

    folder = current_app.config['MEDICAL_REPORT_UPLOAD_FOLDER']
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        os.remove(path)


