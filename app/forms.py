# Para intalar la libreria utilizamos
# pip install WTForms
# Importamos la libreria de form
from wtforms import Form
from wtforms import validators
from wtforms import StringField, PasswordField, BooleanField, FileField, SelectField
from wtforms.fields.html5 import EmailField

from .models import User, Colaborador, registro_temperatura, Auto_reporte, Actualizacion_datos, Permisos_salida

# Creamos la clase que manejara los formularios de login
class LoginForm(Form):
    # Las validaciones son una lista que recibe el validator por cada campo a validar
    mesage = 'El usuario se encuentra fuera del rango'
    username = StringField('Usuario', [
        validators.length(min=4, max=30, message=mesage),
        validators.Required()    # Esta es una funcion de validators
    ])
    password = PasswordField('Contraseña', [
        validators.Required()       # Clase de validator para hacer referncia a requerido
    ])

# Formulario para registrar usuarios sobre la plataforma
class RegisterForm(Form):
    username = StringField('Usuario', [
        validators.length(min=4, max=50)
    ])
    email = EmailField('Correo Electronico', [
        validators.length(min=6, max=100),
        validators.Required(message='El E-mail es Requerido,'),
        validators.Email(message='Ingrese un E-mail valido.')
    ])
    password = PasswordField('Contraseña', [
        validators.Required('La contraseña es requerida.'),
        validators.length(min=6, max=18, message="La contraseña debe tener entre 6 y 18 caracteres."),
        validators.EqualTo('confirm_password', message='Las contraseñas no coiciden.')
    ])
    confirm_password = PasswordField('Confirme Contraseña')
    accept = BooleanField('', [
        validators.DataRequired()
    ])

    # Funcion que nos valida si el campo de username ya esta registrdo en la db
    def validate_username(self, username):
        if User.get_by_username(username.data):
            raise validators.ValidationError("El Usuario ya se encuentra registrado.")

    # Funcion que nos valida si el campo de email ya esta registrdo en la db
    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise validators.ValidationError("El E-mail ya se encuentra registrado.")

# Formulario para registrar un nuevo colaborador en la base de datos
class ColaboradoresForm(Form):
    full_name = StringField('Nombres Completo:', [
        validators.length(min=10, max=80, message='Nombre fuera de rango.'),
        validators.DataRequired(message='Nombres requeridos.')
    ])
    type_doc = StringField('Tipo de Documento:')        # Tipo de documento
    number_doc = StringField('Numero de Documento:')       # Numero de documento
    admission_date = StringField('Fecha de Ingreso:')       # Fecha de ingreso
    type_contract = StringField('Tipo de Contrato:')        # Tipo de Contrato
    cargo = StringField('Cargo:')         # Cargo
    salary = StringField('Salario:')       # Salario
    email = StringField('Correo Corporativo:')       # Salario
    area = StringField('Area Pertenece:')       #Area

    # Funcion que nos valida si el campo de cedula ya esta registrdo en la db
    def validate_full_name(self, full_name):
        if Colaborador.get_by_full_name(full_name.data):
            raise validators.ValidationError("El Usuario ya se encuentra registrado.")

# Formulario para registro de temperatura
class RegistTempForm(Form):
    full_name = StringField("Nombre Completo")

    ages = StringField('Edad:', [
        validators.length(min=2, max=2, message='Corregir Edad'),
        validators.DataRequired(message='Edad requeridos.')
    ])
    completion_date = StringField('Fecha de Diligenciamiento:', [
        validators.length(min=4, max=50, message='Fecha Fuera de rango.'),
        validators.DataRequired(message='La fecha es requerida.')
    ])
    days = StringField('Día de la semana:', [
        validators.DataRequired(message='Dia de la Semana Requerido.')
    ])
    handwashing = StringField('Lavado de manos:', [
        validators.DataRequired(message='Horas de lavado es requerido.')
    ])
    time_entry = StringField('Hora de Ingreso:', [
        validators.DataRequired(message='Hora de Ingreso Requerida.')
    ])
    entry_temperature = StringField('Temperatura de ingreso:', [
        validators.DataRequired(message='Temperatura de Ingreso requerida.')
    ])
    departure_time = StringField('Hora de Salida:', [
        validators.DataRequired(message='la Hora de Salida es requerida.')
    ])
    outlet_temperature = StringField('Temperatura de Salida:', [
        validators.DataRequired(message='Temperatura de Salida es requerida.')
    ])
    observations = StringField('Observaciones:')

# Formulario para registro de temperatura
class AutoReporteForm(Form):
    full_name = StringField("Nombre Completo")

    completion_date = StringField('Fecha de Diligenciamiento:', [
        validators.length(min=4, max=50, message='Fecha Fuera de rango.'),
        validators.DataRequired(message='La fecha es requerida.')
    ])
    eps = StringField('Eps a la que Pertence:', [
        validators.DataRequired(message='Eps Requerida.')
    ])
    pension_fund = StringField('Fondo de pensiones a la que Pertenece:', [
        validators.DataRequired(message='Fondo de Pensiones requerido.')
    ])
    name_contact = StringField('Nombre Persona Contacto:', [
        validators.DataRequired(message='Contacto Requerido.')
    ])
    relationship = StringField('Parentesco:')

    tos = StringField('¿Presenta Tos Recurrente o Espontanea hoy o en los Dias previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    escalofrios = StringField('¿Presenta Escalofrio Recurrente o Espontaneo hoy o en Dias Previos?', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    dolor_garganta = StringField('¿Presenta Dolor de Garganta Recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    dolor_corporal = StringField('¿Presenta Dolor de corporal o Malestar General recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    dolor_cabeza = StringField('¿Presenta Dolor de Cabeza Recurrente o Espontaneo hoy  o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    fiebre = StringField('¿Presenta Fiebre Mayor a 37.8°C, Recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    perdida_olfato = StringField('¿Presenta Perdida de Olfato, Recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    dificultad_respirar = StringField('¿Presenta Dificultad para Respirar como si NO Entrara Aire a sus pulmones de Manera Recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    fatiga = StringField('¿Presenta Fatiga o Real Deterioro de mis Movimientos y mis Ganas de Hacer Algo, es Recurrente o Espontaneo hoy o en Dias Previos? (2 o 3 Dias Antes):', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    viajado = StringField('¿Has Viajado en los ultimos 14 Dias Fuera de la Ciudad?:', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    zona_afectadas = StringField('¿Has Estado en Zonas Afectadas por Covid19?:', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    contacto_positivos = StringField('¿Has Estado en Contacto con Pacientes positivos Covid19?:', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    contactos_sospechosos = StringField('¿Has Estado en Contacto con Pasientes Sospechoso Covid19?:', [
        validators.DataRequired(message='Pregunta Requerida.')
    ])
    observations = StringField('Observaciones:')

# Formulario para Actualizacion de datos
class ActualizacionForm(Form):
    date_completion = StringField('Fecha de Diligenciamiento:')
    full_name = StringField("Apellidos y Nombres:")
    stratum = StringField("Estrato:")
    home_address = StringField("Dirección de Domicilio:")
    neighborhood = StringField("Barrio:")
    location = StringField("Localidad:")
    own_home = StringField("Vivienda Propia:")
    phone = StringField("Telefono:")
    cellular = StringField("Celular:")
    city = StringField("Ciudad:")
    Driving_license = StringField("Licencia De Condución:")
    motorcycle = StringField("Moto N°.")
    car = StringField("Carro N°.")
    category = StringField("Categoría:")
    own_vehicle = StringField("Vehículo Propio:")
    type_document = StringField("Doc. Identidad:")
    identity_document = StringField("N°.")
    expedition_place = StringField("De:")
    expedition_date = StringField("Fecha Expedición:")
    military_card = StringField("L.M N°.:")
    district = StringField("Distrito:")
    birthdate = StringField("Fecha de Nacimiento:")
    place_birth = StringField("Lugar:")
    sex = StringField("Sexo:")
    nationality = StringField("Nacionalidad:")
    rh = StringField("R.H.")
    position = StringField("Cargo:")
    area = StringField("Área:")
    personal_mail = StringField("Correo Personal:")
    date_admission = StringField("Fecha ingreso a la empresa:")
    account_number = StringField("N°. Cuenta:")
    entity = StringField("Entidad:")
    Account_type = StringField("Tipo de Cuenta:")
    eps = StringField("Eps:")
    pension_fund = StringField("Fondo de Pensiones:")
    Layoffs = StringField("Cesantías:")
    arl = StringField("ARL:")
    compensation_box = StringField("CCF:")
    civil_status = StringField("Estado Civil:")
    full_name_spouse = StringField("Apellidos y Nombre del Cónyuge:")
    number_children = StringField("N° Hijos:")
    emer_fullname = StringField("Nombre y Apellidos:")
    emer_parentesco = StringField("Parentesco:")
    emer_direction = StringField("Dirección de Domicilio:")
    emer_city = StringField("Ciudad:")
    emer_cellular = StringField("Celular:")
    emer_phone = StringField("Teléfono:")
    take_medications = StringField("Consume Medicamentos:")
    Which_medications = StringField("Cual:")
    Drug_allergy = StringField("Es Alérgico a un Medicamento:")
    which_allergy = StringField("Cual:")
    major_diseases = StringField("Enfermedades Importantes:")
    which_diseases = StringField("Cual:")
    Bachelor = StringField("Bachillerato.")
    entity_bachelor = StringField("Entidad:")
    technical = StringField("Técnico.")
    title_technical = StringField("Titulo obtenido:")
    technologist = StringField("Tecnológico.")
    title_technologist = StringField("Titulo obtenido:")
    academic = StringField("Universitario.")
    title_academic = StringField("Titulo obtenido:")
    postgraduate = StringField("Posgrado.")
    title_postgraduate = StringField("Titulo obtenido:")
    others = StringField("Otros.")
    title_others = StringField("")
    dependents_name1 = StringField("")
    dependents_relationship1 = StringField("")
    dependents_birthdate1 = StringField("")
    dependents_age1 = StringField("")
    dependents_educatlevel1 = StringField("")
    dependents_name2 = StringField("")
    dependents_relationship2 = StringField("")
    dependents_birthdate2 = StringField("")
    dependents_age2 = StringField("")
    dependents_educatlevel2 = StringField("")
    dependents_name3 = StringField("")
    dependents_relationship3 = StringField("")
    dependents_birthdate3 = StringField("")
    dependents_age3 = StringField("")
    dependents_educatlevel3 = StringField("")
    juramento = StringField("Juramento")
    fir_digital = StringField("Firma Digital")

# Formulario para solicitud de permisos
class PermisosForm(Form):
    email = StringField('Dirección de correo electrónico:')
    full_name = StringField("Apellidos y Nombres:")
    date_completion = StringField('Fecha de Diligenciamiento:')
    departure_date = StringField("Fecha de la salida o permiso:")
    departure_time = StringField("Hora estimada de salida:")
    check_in = StringField("Hora estimada de llegada:")
    reason_departure = StringField("Motivo de la Salida:")
    place_displacement = StringField("Nombre del Proveedor, Cliente o Entidad dónde se realizará el desplazamiento?:")
    prior_authorization = StringField("¿Cuenta con autorización previa de su jefe inmediato?")
    who_authorized = StringField("Mencione el nombre de su Jefe Inmediato o quien le autorizó el desplazamiento:")
    observations = StringField("Observaciones")

# Formulario de cantidad de colaboradores
class CantidadesForm(Form):
    quantity = StringField('Cantidad de Colaboradores Total:')

# Formulario de los cargos
class CargosForm(Form):
    charges = StringField('Cargo:')

# Formulario de los Areas
class AreasForm(Form):
    area_name = StringField('Area:')