from flask import Flask, redirect, url_for, request, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)
    migrate.init_app(app, db)  # Flask-Migrate'i uygulamaya ekliyoruz

    from .views import views
    from .auth import auth
    from .models import User, Group, Poll, Vote

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.before_request
    def before_request():
        g.user = current_user

    @app.context_processor
    def inject_user():
        return dict(user=g.user)

    @app.before_request
    def require_login():
        allowed_routes = ['auth.login', 'auth.sign_up', 'views.create_poll']
        if request.endpoint and request.endpoint not in allowed_routes and not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all(app=app)
        print('Created Database!')