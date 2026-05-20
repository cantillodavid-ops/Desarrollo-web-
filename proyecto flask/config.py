import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-dev-cambiar-en-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    # Formato: mysql+pymysql://usuario:contraseña@host/nombre_base_datos
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/gestion_eventos'
        #                 ^^^^  ^         ^^^^^^^^^^^^^^^^
        #                 user  password  nombre de la BD en XAMPP
        # Si pusiste contraseña en XAMPP: 'mysql+pymysql://root:TU_CLAVE@localhost/gestion_eventos'
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}