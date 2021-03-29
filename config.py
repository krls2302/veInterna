# Este archivo alamacena 2 clases de configuracion
class config:
    # Generamos la llave secreta recomendable alfanumerica cambiar en produccion
    # Instanciamos la llave en __init__.py
    # Despues dirigirnos al archivo login.html
    SECRET_KEY = "K3yPr1v4d0*V3nT43Qu1p055.4.5"

class DevelopmentConfig(config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/registro.db'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/alcoholimetro'   # Atribute que nos ayuda con la db
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuramos el envio de correo electronicos
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'informacion@ventaequipos.com'
    MAIL_PASSWORD = '7f55D.2019'
    DONT_REPLY_FROM_EMAIL = ('Intranet_VE', 'informacion@ventaequipos.com')
    MAIL_ASCCI_ATTACHMENTS = False

# Diccionario con configuraciones que se le pasan a la clase DevelepmentConfig
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}