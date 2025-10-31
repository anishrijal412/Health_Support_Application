# routes/dashboard.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def root_redirect():
    return redirect(url_for('auth.login'))

@dashboard.route('/dashboard')
@login_required
def home():
    return render_template('dashboard.html', user=current_user)
