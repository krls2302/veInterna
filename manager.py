# Importamos la librerias de app y Flask-scrip
from app import create_app
from flask_script import Manager
from config import config
import sys
path = "/home/ventaequipossas/.virtualenvs/venv/lib/python3.7/site-packages"
if path not in sys.path:
    sys.path.append(path)

# Creamos la instancia de las configuraciones de config
config_class = config['development']

# Instanciamos nuestra funcion de app, el argumento es para desarrollo
app = create_app(config_class)

# Creamos la validacion del inicio de app
if __name__ == "__main__":
    manager = Manager(app)
    manager.run()