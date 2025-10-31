# routes/reset_password.py
import random
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_mail import Message
from extensions import db
from models.user import User
from app import mail
from werkzeug.security import generate_password_hash

reset_bp = Blueprint('reset_password', __name__)

@reset_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('❌ No account found with that email', 'danger')
            return redirect(url_for('reset_password.forgot_password'))

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['reset_otp'] = otp

        msg = Message('🔑 Your Password Reset Code', recipients=[email])
        msg.body = f"Your password reset code is: {otp}"
        mail.send(msg)

        flash('✅ Reset code sent to your email.', 'info')
        return redirect(url_for('reset_password.verify_code'))

    return render_template('forgot_password.html')


@reset_bp.route('/verify', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        code = request.form.get('code')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if code != session.get('reset_otp'):
            flash('❌ Invalid code', 'danger')
            return redirect(url_for('reset_password.verify_code'))

        if new_password != confirm_password:
            flash('❌ Passwords do not match', 'danger')
            return redirect(url_for('reset_password.verify_code'))

        user = User.query.filter_by(email=session.get('reset_email')).first()
        user.password = generate_password_hash(new_password)
        db.session.commit()

        session.pop('reset_email', None)
        session.pop('reset_otp', None)

        flash('✅ Password has been reset. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('verify_code.html')
