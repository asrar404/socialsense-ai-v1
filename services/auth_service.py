import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository=None):
        self.user_repo = user_repository or UserRepository()

    def register(self, username, email, password, confirm_password):
        errors = {}

        if not username or len(username.strip()) < 3:
            errors['username'] = 'Username must be at least 3 characters.'
        elif self.user_repo.username_exists(username):
            errors['username'] = 'Username already taken.'

        if not email or '@' not in email:
            errors['email'] = 'Valid email is required.'
        elif self.user_repo.email_exists(email):
            errors['email'] = 'Email already registered.'

        if not password or len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        elif not re.search(r'[A-Z]', password):
            errors['password'] = 'Password must contain an uppercase letter.'
        elif not re.search(r'[a-z]', password):
            errors['password'] = 'Password must contain a lowercase letter.'
        elif not re.search(r'[0-9]', password):
            errors['password'] = 'Password must contain a number.'

        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        if errors:
            return {'success': False, 'errors': errors}

        password_hash = generate_password_hash(password)
        user = self.user_repo.create(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=password_hash
        )

        return {'success': True, 'user': user}

    def login(self, email, password, remember=False):
        errors = {}

        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'

        if errors:
            return {'success': False, 'errors': errors}

        user = self.user_repo.get_by_email(email.strip().lower())
        if not user or not check_password_hash(user.password_hash, password):
            return {'success': False, 'errors': {'general': 'Invalid email or password.'}}

        login_user(user, remember=remember)
        return {'success': True, 'user': user}

    def logout(self):
        logout_user()

    def get_profile_data(self, user):
        analysis_count = self.user_repo.count_analyses(user.id) if hasattr(self.user_repo, 'count_analyses') else 0
        recent_analyses = self.user_repo.get_recent_analyses(user.id)

        return {
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'analysis_count': analysis_count,
            'recent_analyses': recent_analyses,
        }
