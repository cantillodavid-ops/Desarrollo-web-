import os
from flask import Flask, render_template
from models import db, User
from flask_login import LoginManager
from config import config
import pymysql

app = Flask(__name__)
app.secret_key = "clave_secreta"

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        port=3307,
        database="gestion_eventos",
        cursorclass=pymysql.cursors.DictCursor
    )

def create_app():
    app = Flask(__name__)

    
    env = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[env])

    
    db.init_app(app)

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    
    from auth.routes import auth_bp
    from events.routes import events_bp
    from users.routes import users_bp

    app.register_blueprint(auth_bp,   url_prefix='/auth')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(users_bp,  url_prefix='/users')

    
    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('events.catalog'))

    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
