# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models.user import User
import random
from flask_mail import Message
from extensions import mail


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard.home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ✅ Forgot Password - Step 1: Enter Email
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('❌ No account found with that email.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Generate 6-digit reset code
        code = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['reset_code'] = code

        # Send code to the user's email
        msg = Message('🔐 Password Reset Code', recipients=[email])
        msg.body = f"Your password reset code is: {code}"
        mail.send(msg)

        flash('✅ A reset code has been sent to your email.', 'info')
        return redirect(url_for('auth.verify_reset_code'))

    return render_template('forgot_password.html')

    # ✅ Forgot Password - Step 2: Verify Code
@auth.route('/verify-reset', methods=['GET', 'POST'])
def verify_reset_code():
    if request.method == 'POST':
        code = request.form.get('code')

        if code != session.get('reset_code'):
            flash('❌ Invalid code. Try again.', 'danger')
            return redirect(url_for('auth.verify_reset_code'))

        # If code matches, go to reset form
        return redirect(url_for('auth.reset_password'))

    return render_template('verify_reset.html')

    # ✅ Forgot Password - Step 3: Reset Password
@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        flash('⚠️ Session expired. Please try again.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')

        user = User.query.filter_by(email=session['reset_email']).first()
        if not user:
            flash('❌ Something went wrong.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Hash and update new password
        from extensions import bcrypt
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        # Clear session
        session.pop('reset_email', None)
        session.pop('reset_code', None)

        flash('✅ Password has been reset. You can LogIn.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')

