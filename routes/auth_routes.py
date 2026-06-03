from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        result = auth_service.register(
            username=request.form.get('username', ''),
            email=request.form.get('email', ''),
            password=request.form.get('password', ''),
            confirm_password=request.form.get('confirm_password', ''),
        )

        if result['success']:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            for field, error in result['errors'].items():
                flash(error, 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        result = auth_service.login(
            email=request.form.get('email', ''),
            password=request.form.get('password', ''),
            remember=request.form.get('remember') == 'on',
        )

        if result['success']:
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            for field, error in result['errors'].items():
                flash(error, 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    auth_service.logout()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    data = auth_service.get_profile_data(current_user)
    return render_template('auth/profile.html', data=data)
