import datetime
from . import db

# Importamos la libreria que nos ayuda a entriptar las contraseñas
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin

# Creamos la clase de db.Model para que generemos de un modelo
# La clase hereda de db.model y usermixin para el anejo de sessiones
class User(db.Model, UserMixin):
    # Solo quede definir los atributos tener en cuenta que los atributos
    # son las columnas de la tabla que estamos generando
    # El atributo __tablename__ solo nos ayuda a cambiar el nombre de la tabla

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    encrypted_password = db.Column(db.String(93), unique=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Comparamos la contraseña del usuario con la que esta almacenada en la db
    def verify_password(self, password):
        return check_password_hash(self.encrypted_password, password)
        # check_password_hash realiza la comparacion de las dos contraseñas y devuelve un valor bool

    # Convertimos password en una propiedad
    @property
    def password(self):
        pass

    # Utilizamos del atributo de la propiedad creada anteriormente
    @password.setter
    def password(self, value):
        self.encrypted_password = generate_password_hash(value)

    # metodo str cada que se imprima el objeto de type username se imprime el username
    def __str__(self):
        return self.username

    # Despues de tener creado el modelo de la tabla solo queda importarla al __init__.py

    #Creamos metodo de clase asi que se decora
    @classmethod
    def create_element(cls, username, password, email):
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    # Metodo que nos ayuda a validar si el usuario ya se encuentra registrado en la db
    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    # Metodo que nos ayuda a validar si el correo ya se encuentra registrado en la db
    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()

    # Funcion que nos retorna el id del usuario desde db
    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()

# Creamos el modelo para nuestro colaboradores que se van a registrar
class Colaborador(db.Model):
    __tablename__= 'colaboradores'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    type_doc = db.Column(db.String(100))        # Tipo de documento
    number_doc = db.Column(db.String(15))       # Numero de documento
    admission_date = db.Column(db.String(15))       # Fecha de ingreso
    type_contract = db.Column(db.String(50))        # Tipo de Contrato
    cargo = db.Column(db.String(50))        # Cargo
    salary = db.Column(db.String(15))        # Salario
    email = db.Column(db.String(80))        # Email
    area = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Creamos metodo de clase realizando decoracion
    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, full_name, type_doc, number_doc, admission_date, type_contract,
                        cargo, salary, email, area):
        colaborador = Colaborador(full_name=full_name, type_doc=type_doc, number_doc=number_doc,
                                admission_date=admission_date, type_contract=type_contract,
                                cargo=cargo, salary=salary, email=email, area=area)
        db.session.add(colaborador) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return colaborador

    # Metodo que nos ayuda a validar si el nombre ya se encuentra registrado en la db
    @classmethod
    def get_by_full_name(cls, full_name):
        return Colaborador.query.filter_by(full_name=full_name).first()

    # Generamos el metodo de captura del id desde la db
    @classmethod
    def get_by_id(cls, id):
        return Colaborador.query.filter_by(id=id).first()

    # Generamos un nuevo metodo para realizar la actualizacion de las elementos
    @classmethod
    def update_element(cls, id, full_name=full_name, type_doc=type_doc, number_doc=number_doc,
                        admission_date=admission_date, type_contract=type_contract,
                        cargo=cargo, salary=salary, email=email, area=area):
        colaborador = Colaborador.get_by_id(id)
        if colaborador is None:
            return False

        colaborador.full_name = full_name
        colaborador.type_doc = type_doc
        colaborador.number_doc = number_doc
        colaborador.admission_date = admission_date
        colaborador.type_contract = type_contract
        colaborador.cargo = cargo
        colaborador.salary = salary
        colaborador.email = email
        colaborador.area = area

        db.session.add(colaborador)
        db.session.commit()

        return colaborador

    @classmethod
    def delete_element(cls, id):
        colabor = Colaborador.get_by_id(id)

        if colabor is None:
            return False

        db.session.delete(colabor)
        db.session.commit()

        return True

# Nueva clase para realizar reporte de temperatura
class registro_temperatura(db.Model):
    __tablename__= 'Registro_temperatura'
    # Linea que se tiene que poner en la tabla que tienen relacion
    # tasks = db.relationship('modelo_al_con_el_que_se_relaciona_este_modelo_ej.User')
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))   # Nombre completo
    ages = db.Column(db.String(5))      # Edades de los colaboradores
    completion_date = db.Column(db.String(50))     # FECHA DILIGENCIAMIENTO
    days = db.Column(db.String(20))       # ESCOGER DÍA DE LA SEMANA
    handwashing = db.Column(db.String(50))      # Lavado de manos
    time_entry = db.Column(db.String(20))       # HORA DE INGRESO
    entry_temperature = db.Column(db.String(5))    # TEMPERATURA DE INGRESO
    departure_time = db.Column(db.String(20))    # HORA DE SALIDA
    outlet_temperature = db.Column(db.String(5))   # TEMPERATURA DE SALIDA
    active_breaks = db.Column(db.String(20))        # Pausas Activas
    observations = db.Column(db.String(1000))     # Observaciones
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # # Creamos metodo de clase realizando decoracion
    # # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, full_name, ages, completion_date, days, handwashing, time_entry, entry_temperature,
                        departure_time, outlet_temperature, active_breaks, observations):
        temp = registro_temperatura(full_name=full_name, ages=ages,
                                    completion_date=completion_date, days=days, handwashing=handwashing,
                                    time_entry=time_entry, entry_temperature=entry_temperature,
                                    departure_time=departure_time, outlet_temperature=outlet_temperature,
                                    active_breaks=active_breaks, observations=observations)
        db.session.add(temp) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return temp

# Nueva clase para realizar reporte de temperatura
class Auto_reporte(db.Model):
    __tablename__= 'Auto-Reporte'
    # Linea que se tiene que poner en la tabla que tienen relacion
    # tasks = db.relationship('modelo_al_con_el_que_se_relaciona_este_modelo_ej.User')
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))   # Nombre completo
    completion_date = db.Column(db.String(50))     # Fecha de diligenciaminto
    eps = db.Column(db.String(20))       # Eps a la que pertenece
    pension_fund = db.Column(db.String(50))      # Fondo de pensiones
    name_contact = db.Column(db.String(50))      # Nombre persona contacto
    relationship = db.Column(db.String(50))      # Parentesto
    tos = db.Column(db.String(50))      # Presenta tos
    escalofrios = db.Column(db.String(50))      # Presenta escalofrios
    dolor_garganta = db.Column(db.String(50))      # Presenta dolor de garganta
    dolor_corporal = db.Column(db.String(50))      # Presenta dolor corporal
    dolor_cabeza = db.Column(db.String(50))      # Presenta dolor de cabeza
    fiebre = db.Column(db.String(50))      # presenta fiebre
    perdida_olfato = db.Column(db.String(50))      # perdida de olfato
    dificultad_respirar = db.Column(db.String(50))      # Difucultad para respirar
    fatiga = db.Column(db.String(50))      # presenta fatiga
    viajado = db.Column(db.String(50))      # ha viajado en los ultimos 14 dias
    zona_afectadas = db.Column(db.String(50))      # Zona afectadas por covid
    contacto_positivos = db.Column(db.String(50))      # Contactos con personas positivas covid19
    contactos_sospechosos = db.Column(db.String(50))      # Contactos con personas sospechosos covid19
    observations = db.Column(db.String(1000))     # Observaciones
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Creamos metodo de clase realizando decoracion
    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, full_name, completion_date, eps, pension_fund,
                        name_contact, relationship, tos, escalofrios,
                        dolor_garganta, dolor_corporal, dolor_cabeza, fiebre, perdida_olfato,
                        dificultad_respirar, fatiga, viajado, zona_afectadas,
                        contacto_positivos, contactos_sospechosos, observations):
        auto = Auto_reporte(full_name=full_name, completion_date=completion_date, eps=eps,
                                    pension_fund=pension_fund, name_contact=name_contact,
                                    relationship=relationship, tos=tos, escalofrios=escalofrios,
                                    dolor_garganta=dolor_garganta, dolor_corporal=dolor_corporal,
                                    dolor_cabeza=dolor_cabeza, fiebre=fiebre, perdida_olfato=perdida_olfato,
                                    dificultad_respirar=dificultad_respirar, fatiga=fatiga, viajado=viajado,
                                    zona_afectadas=zona_afectadas, contacto_positivos=contacto_positivos,
                                    contactos_sospechosos=contactos_sospechosos, observations=observations)
        db.session.add(auto) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return auto

# Nueva clase para realizar Actualizacion de datos
class Actualizacion_datos(db.Model):
    __tablename__= 'Actualizacion_Datos'
    # Linea que se tiene que poner en la tabla que tienen relacion
    # tasks = db.relationship('modelo_al_con_el_que_se_relaciona_este_modelo_ej.User')
    id = db.Column(db.Integer, primary_key=True)
    date_completion = db.Column(db.String(20))     # Fecha de diligenciamiento
    full_name = db.Column(db.String(100))   # Nombre completo
    stratum = db.Column(db.String(5))       # Estrato
    home_address = db.Column(db.String(100))       # Dirección de Domicilio
    neighborhood = db.Column(db.String(50))       # Barrio
    location = db.Column(db.String(50))       # Localidad
    own_home = db.Column(db.String(5))       # Vivienda propia
    phone = db.Column(db.String(15))       # Telefono
    cellular = db.Column(db.String(15))       # Celular
    city = db.Column(db.String(50))       # Ciudad
    Driving_license = db.Column(db.String(5))       # Licencia de conduccion
    motorcycle = db.Column(db.String(20))       # Motocicleta N°
    car = db.Column(db.String(20))       # Automovil N°
    category = db.Column(db.String(10))       # Categoria
    own_vehicle = db.Column(db.String(5))       # Vehiculo Propio
    type_document = db.Column(db.String(5))       #  Tipo de documento de Identidad
    identity_document = db.Column(db.String(20))       # Documento Identidad n°
    expedition_place = db.Column(db.String(50))       # Lugar de expedición
    expedition_date = db.Column(db.String(20))      # Fecha de expedicion
    military_card = db.Column(db.String(20))       # Libreta militar
    district = db.Column(db.String(10))       # Distrito
    birthdate = db.Column(db.String(10))       # Fecha de nacimiento
    place_birth = db.Column(db.String(10))       # Lugar de nacimiento
    sex = db.Column(db.String(2))       # Sexo
    nationality = db.Column(db.String(20))       # Nacionalidad
    rh = db.Column(db.String(5))       # R.H
    position = db.Column(db.String(100))       # Cargo
    area = db.Column(db.String(20))       # Área
    personal_mail = db.Column(db.String(10))       # Correo Personal
    date_admission = db.Column(db.String(20))       # Fecha de ingreso
    account_number = db.Column(db.String(50))       # Numero de cuenta
    entity = db.Column(db.String(50))       # Entidad
    Account_type = db.Column(db.String(15))       # Tipo de cuenta
    eps = db.Column(db.String(50))       # Eps
    pension_fund = db.Column(db.String(50))       # Fondo de pensiones
    Layoffs = db.Column(db.String(50))       # Cesantías
    arl = db.Column(db.String(50))       # ARL
    compensation_box = db.Column(db.String(50))       # Caja de compensación
    civil_status = db.Column(db.String(30))       # Estado Civil
    full_name_spouse = db.Column(db.String(100))       # Nombre completo de conyuge
    number_children = db.Column(db.String(5))       # Numero de Hijos
    emer_fullname = db.Column(db.String(100))       # En caso de emergencia nombre
    emer_parentesco = db.Column(db.String(50))       # Parentesco en caso de emergencia
    emer_direction = db.Column(db.String(100))       # Direccion de Domicilio
    emer_city = db.Column(db.String(50))       # Ciudad en caso de emergencia
    emer_cellular = db.Column(db.String(15))       # Celular en caso de emergencia
    emer_phone = db.Column(db.String(15))       # Telefono en caso de emergencia
    take_medications = db.Column(db.String(3))       # Consume medicamentos
    Which_medications = db.Column(db.String(100))       # Cual medicamento consume
    Drug_allergy = db.Column(db.String(3))       # Alergico algun medicamento
    which_allergy = db.Column(db.String(100))       # A Cual medicamento es alergico
    major_diseases = db.Column(db.String(3))       # Enfermedades Importantes
    which_diseases = db.Column(db.String(100))       # Cual es la enfermedad importante
    Bachelor = db.Column(db.String(3))       # Estudios Realizados Bachicherato
    entity_bachelor = db.Column(db.String(150))       # Entidad donde realizo bachicherato
    technical = db.Column(db.String(3))       # Titulo de técnico
    title_technical = db.Column(db.String(150))       # Entidad donde realizo el tecnico
    technologist = db.Column(db.String(3))       # Tecnologo
    title_technologist = db.Column(db.String(3))       # entidad donde realizo tecnologo
    academic = db.Column(db.String(3))       # Universitario
    title_academic = db.Column(db.String(150))       # Titulo obtenido
    postgraduate = db.Column(db.String(3))       # Posgrado
    title_postgraduate = db.Column(db.String(150))       # titulo de posgrado
    others = db.Column(db.String(3))       # otros titulos
    title_others = db.Column(db.String(3))       # Otros titulos
    dependents_name1 = db.Column(db.String(100))       # Nombre de persona a cargo
    dependents_relationship1 = db.Column(db.String(100))       # Parentesco
    dependents_birthdate1 = db.Column(db.String(20))       # Fecha de nacimiento
    dependents_age1 = db.Column(db.String(5))       # Edad
    dependents_educatlevel1 = db.Column(db.String(20))       # Nivel educativo, prescolar
    dependents_name2 = db.Column(db.String(100))       # Nombre de persona a cargo
    dependents_relationship2 = db.Column(db.String(100))       # Parentesco
    dependents_birthdate2 = db.Column(db.String(20))       # Fecha de nacimiento
    dependents_age2 = db.Column(db.String(5))       # Edad
    dependents_educatlevel2 = db.Column(db.String(20))       # Nivel educativo, prescolar
    dependents_name3 = db.Column(db.String(100))       # Nombre de persona a cargo
    dependents_relationship3 = db.Column(db.String(100))       # Parentesco
    dependents_birthdate3 = db.Column(db.String(20))       # Fecha de nacimiento
    dependents_age3 = db.Column(db.String(5))       # Edad
    dependents_educatlevel3 = db.Column(db.String(20))       # Nivel educativo, prescolar
    juramento = db.Column(db.String(3))     # Declaro bajo juramento
    fir_digital = db.Column(db.String(3))       # Firma digital para almacenar esta info
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # # Creamos metodo de clase realizando decoracion
    # # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, date_completion, full_name, stratum, home_address, neighborhood,
                        location, own_home, phone, cellular, city, Driving_license,
                        motorcycle, car, category, own_vehicle, type_document,
                        identity_document, expedition_place, expedition_date, military_card, district,
                        birthdate, place_birth, sex, nationality, rh, position,
                        area, personal_mail, date_admission, account_number, entity,
                        Account_type, eps, pension_fund, Layoffs, arl, compensation_box,
                        civil_status, full_name_spouse, number_children, emer_fullname,
                        emer_parentesco, emer_direction, emer_city, emer_cellular,
                        emer_phone, take_medications, Which_medications, Drug_allergy,
                        which_allergy, major_diseases, which_diseases, Bachelor, entity_bachelor,
                        technical, title_technical, technologist, title_technologist, academic,
                        title_academic, postgraduate, title_postgraduate, others, title_others,
                        dependents_name1, dependents_relationship1,
                        dependents_birthdate1, dependents_age1, dependents_educatlevel1,
                        dependents_name2, dependents_relationship2,
                        dependents_birthdate2, dependents_age2, dependents_educatlevel2,
                        dependents_name3, dependents_relationship3,
                        dependents_birthdate3, dependents_age3, dependents_educatlevel3,
                        juramento, fir_digital):
        actual = Actualizacion_datos(date_completion=date_completion, full_name=full_name,
                                    stratum=stratum, home_address=home_address,
                                    neighborhood=neighborhood, location=location,
                                    own_home=own_home, phone=phone, cellular=cellular,
                                    city=city, Driving_license=Driving_license,
                                    motorcycle=motorcycle, car=car, category=category,
                                    own_vehicle=own_vehicle, type_document=type_document,
                                    identity_document=identity_document, expedition_place=expedition_place,
                                    expedition_date=expedition_date,
                                    military_card=military_card, district=district, birthdate=birthdate,
                                    place_birth=place_birth, sex=sex, nationality=nationality, rh=rh,
                                    position=position, area=area, personal_mail=personal_mail,
                                    date_admission=date_admission, account_number=account_number,
                                    entity=entity, Account_type=Account_type, eps=eps, pension_fund=pension_fund,
                                    Layoffs=Layoffs, arl=arl, compensation_box=compensation_box,
                                    civil_status=civil_status, full_name_spouse=full_name_spouse,
                                    number_children=number_children, emer_fullname=emer_fullname,
                                    emer_parentesco=emer_parentesco, emer_direction=emer_direction,
                                    emer_city=emer_city, emer_cellular=emer_cellular, emer_phone=emer_phone,
                                    take_medications=take_medications, Which_medications=Which_medications,
                                    Drug_allergy=Drug_allergy, which_allergy=which_allergy,
                                    major_diseases=major_diseases, which_diseases=which_diseases,
                                    Bachelor=Bachelor, entity_bachelor=entity_bachelor, technical=technical,
                                    title_technical=title_technical, technologist=technologist,
                                    title_technologist=title_technologist, academic=academic, title_academic=title_academic,
                                    postgraduate=postgraduate, title_postgraduate=title_postgraduate, others=others,
                                    title_others=title_others, dependents_name1=dependents_name1,
                                    dependents_relationship1=dependents_relationship1, dependents_birthdate1=dependents_birthdate1,
                                    dependents_age1=dependents_age1, dependents_educatlevel1=dependents_educatlevel1, dependents_name2=dependents_name2,
                                    dependents_relationship2=dependents_relationship2,
                                    dependents_birthdate2=dependents_birthdate2, dependents_age2=dependents_age2,
                                    dependents_educatlevel2=dependents_educatlevel2, dependents_name3=dependents_name3,
                                    dependents_relationship3=dependents_relationship3,
                                    dependents_birthdate3=dependents_birthdate3, dependents_age3=dependents_age3,
                                    dependents_educatlevel3=dependents_educatlevel3, juramento=juramento, fir_digital=fir_digital)
        db.session.add(actual) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return actual

# Nueva clase para realizar reporte de temperatura
class Permisos_salida(db.Model):
    __tablename__= 'Perm_Salidas'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))       # Correo corporativo
    full_name = db.Column(db.String(100))   # Nombre completo
    completion_date = db.Column(db.String(50))     # Fecha de diligenciaminto
    departure_date = db.Column(db.String(50))       # Fecha de la salida o permiso
    departure_time = db.Column(db.String(20))      # Hora estimada de salida
    check_in = db.Column(db.String(20))      # Hora estimada de llegada
    reason_departure = db.Column(db.String(50))      # Motivo de la Salida
    place_displacement = db.Column(db.String(150))      # Nombre del Proveedor, Cliente
    prior_authorization = db.Column(db.String(5))      # Cuenta con autorización previa
    who_authorized = db.Column(db.String(50))      # Mencione el nombre de su Jefe Inmediato
    observations = db.Column(db.String(200))        # Observaciones
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Creamos metodo de clase realizando decoracion
    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, email, full_name, completion_date, departure_date,
                        departure_time, check_in, reason_departure,
                        place_displacement, prior_authorization, who_authorized,
                        observations):

        perm = Permisos_salida(email=email, full_name=full_name, completion_date=completion_date,
                                    departure_date=departure_date, departure_time=departure_time,
                                    check_in=check_in, reason_departure=reason_departure,
                                    place_displacement=place_displacement, prior_authorization=prior_authorization,
                                    who_authorized=who_authorized, observations=observations)
        db.session.add(perm) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return perm

# Tablas de configuraciones
# Tabla con cantidad de empleados
class Cantida_colaborador(db.Model):
    __tablename__= 'Cant_Empleados'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Creamos metodo de clase realizando decoracion
    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, quantity):
        cant_colab = Cantida_colaborador(quantity=quantity)
        db.session.add(cant_colab) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return cant_colab

    # Generamos el metodo de captura del id desde la db
    @classmethod
    def get_by_id(cls, id):
        return Cantida_colaborador.query.filter_by(id=id).first()

    # Generamos un nuevo metodo para realizar la actualizacion de las elementos
    @classmethod
    def update_element(cls, id, quantity=quantity):
        cant_colab = Cantida_colaborador.get_by_id(id)
        if cant_colab is None:
            return False

        cant_colab.quantity = quantity

        db.session.add(cant_colab)
        db.session.commit()

        return cant_colab

    @classmethod
    def delete_element(cls, id):
        cant_colab = Cantida_colaborador.get_by_id(id)

        if cant_colab is None:
            return False

        db.session.delete(cant_colab)
        db.session.commit()

        return True

# Tabla de Cargos
class Cargos(db.Model):
    __tablename__= 'Cargos'
    id = db.Column(db.Integer, primary_key=True)
    charges = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Creamos metodo de clase realizando decoracion
    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, charges):
        cargo = Cargos(charges=charges)
        db.session.add(cargo) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return cargo

    # Generamos subclase para buscar id
    @classmethod
    def get_by_id(cls, id):
        return Cargos.query.filter_by(id=id).first()

    # Generamos un nuevo metodo para realizar la actualizacion de las elementos
    @classmethod
    def update_element(cls, id, charges=charges):
        cargo = Cargos.get_by_id(id)
        if cargo is None:
            return False

        cargo.charges = charges
        db.session.add(cargo)
        db.session.commit()
        return cargo

    @classmethod
    def delete_element(cls, id):
        cargo = Cargos.get_by_id(id)

        if cargo is None:
            return False

        db.session.delete(cargo)
        db.session.commit()
        return True

# Tabla de Areas
class Areas(db.Model):
    __tablename__= 'Areas'
    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # Generamos la creacion del usuario por elemento
    @classmethod
    def create_element(cls, area_name):
        area = Areas(area_name=area_name)
        db.session.add(area) # Agregamos el colaborador a la db
        db.session.commit() # Almacenamos el colaborador en la db
        return area

    # Generamos subclase para buscar id
    @classmethod
    def get_by_id(cls, id):
        return Areas.query.filter_by(id=id).first()

    # Generamos un nuevo metodo para realizar la actualizacion de las elementos
    @classmethod
    def update_element(cls, id, area_name=area_name):
        area = Areas.get_by_id(id)
        if area is None:
            return False

        area.area_name = area_name
        db.session.add(area)
        db.session.commit()
        return area

    @classmethod
    def delete_element(cls, id):
        area = Areas.get_by_id(id)

        if area is None:
            return False

        db.session.delete(area)
        db.session.commit()
        return True