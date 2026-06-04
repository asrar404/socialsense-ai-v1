import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    elif os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    app.config['YOUTUBE_API_KEY'] = os.environ.get('YOUTUBE_API_KEY', '')
    app.config['REDDIT_CLIENT_ID'] = os.environ.get('REDDIT_CLIENT_ID', '')
    app.config['REDDIT_CLIENT_SECRET'] = os.environ.get('REDDIT_CLIENT_SECRET', '')
    app.config['REDDIT_USER_AGENT'] = os.environ.get('REDDIT_USER_AGENT', 'SocialSenseAI/1.0')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'reports')

    from database import init_db
    init_db(app)

    from flask_login import LoginManager
    from models.user import User

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)

    from routes import auth_bp, dashboard_bp, analysis_bp, export_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(export_bp)

    @app.context_processor
    def inject_globals():
        is_demo = not app.config.get('YOUTUBE_API_KEY', '')
        has_reddit = bool(app.config.get('REDDIT_CLIENT_ID', '') and app.config.get('REDDIT_CLIENT_SECRET', ''))
        return {'is_demo_mode': is_demo, 'has_reddit_creds': has_reddit}

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
