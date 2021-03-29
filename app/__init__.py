# Importamos la libreria de app
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .consts import LOGIN_REQUIRED
from flask_mail import Mail

# Creamos una instancia de app
app = Flask(__name__)
# Generamos la instancia de la libria de proteccion del sitio web
csrf = CSRFProtect()
# Generamos la instancia de Bootstrap
bootstrap = Bootstrap()
# Creamos la instancias de sqlalchemy siendo el orm que nos ayuda con la base de datos
db = SQLAlchemy()
# Generamos la intancia de login manager que nos maneja las sesiones
login_manager = LoginManager()
# Inicializamos mail para todo el sistema
mail = Mail()

# Instanciamos las vistas desde views.py
# El .views es para que python sepa que estamos tomando desde un archivo python
from .views import page
from .models import User

# Definimos una funcion que retorne nuestra instancia
def create_app(config):

    app.config.from_object(config)  # Creamos el objeto de config desde el archivo config

    csrf.init_app(app)      # Inicializamos solo recibir formularios propios
    bootstrap.init_app(app)     # Realizamos la inicializacion del servidor con los stilos bootstrap
    login_manager.init_app(app) # Iniciamos la aplicacion con la instancia de loginmanager
    login_manager.login_view = '.login' # Redirigir login cuando no se tiene el login para evitar lo ingreso
    login_manager.login_message = LOGIN_REQUIRED #cambiamos el mensaje cuando no esta logiado

    app.register_blueprint(page)    # Realizamos la utilizacion de las instancias de page
    mail.init_app(app)      # Iniciamos nuestro gestor de correos

    # Vamos a crear nuestra tabla por medio de un objeto
    with app.app_context():
        db.init_app(app)    # Realizamos la inicializacion de nuestra base datos con alchemy
        db.create_all()     #Creamos todas las tablas del modelo
    return app