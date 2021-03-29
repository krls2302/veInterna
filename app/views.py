# Importamos libreria de clases
from flask import Blueprint
from werkzeug.utils import secure_filename
from .forms import LoginForm, RegisterForm, ColaboradoresForm, RegistTempForm, AutoReporteForm, ActualizacionForm, PermisosForm, CantidadesForm, CargosForm, AreasForm
from .consts import *
import os
from datetime import datetime, timedelta, date
from collections import defaultdict

# Envio de correos electronicos
from flask_mail import Message
from . import mail

# Generamos los pdf con la app
import pdfkit

# Importamos la pantalla virtual de ubuntu para el pytonanywhre.com
from pyvirtualdisplay import Display

# Generar excel con flask
from io import BytesIO
import xlwt
import xlsxwriter

# Libreria que nos genera la session para cada usuario
from flask_login import login_user, logout_user, login_required, current_user
from . import login_manager

#Importamos librerias de funciones
from .models import User, Colaborador, registro_temperatura, Auto_reporte, Actualizacion_datos, Permisos_salida, Cantida_colaborador, Cargos, Areas
from flask import render_template, request, flash, redirect, url_for, Response, send_file, current_app, make_response

# Creamos una instancia de Blueprint
# Blueprint recibe dos parametros uno el contesto de page
# El otro el contesto donde se crea la page
page = Blueprint('page', __name__)

# Generamos la funcion que nos cargara el usuario desde la base de datos que esta logiado
@login_manager.user_loader
def load_user(id):
    return User.get_by_id(id)

# Creamos nuestras rutas del servidor con decoradores
# Despues de crear las rutas las tenemos que instanciar en nuestro
# Archivo manager.py

@page.app_errorhandler(404) # Recibe como parametro el error
def page_404(error):    # Recibe si o si el error para darle manejo
    return render_template('errors/404.html'), 404

@page.route('/')
def index():
    title = "Index"
    return render_template('index.html', title = title)

# Creamos la url que cierra la session que tenemos iniciada
@page.route('/logout')
def logout():
    logout_user()
    flash(LOGOUT)
    return redirect(url_for('.index'))

# El login recibe dos metodos entonces se modifica estos dos metodos
@page.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    else:
        form = LoginForm(request.form)  # Instanaciamos nuestro formulario desde forms
        if request.method == "POST" and form.validate():
            user = User.get_by_username(form.username.data)
            if user and user.verify_password(form.password.data):
                login_user(user)
                # flash(LOGIN_USER)
                return redirect(url_for('.reportes'))
            else:
                flash(ERROR_USER_PASSWORD, 'error')
         # Tenemos que pasarle como parametro al html el form para despues validarlo desde html
        return render_template('auth/login.html', title='Login', form = form)


@page.route("/register", methods=['GET', 'POST'])
@login_required
def registroUser():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate():
            User.create_element(form.username.data, form.password.data, form.email.data)
            flash(USER_CREATED)
            #login_user(user)    # Con este parametro genero sessiones en automatico
            return redirect(url_for('.index'))

    title = "Registro Usuarios"
    return render_template('auth/registerUser.html', title=title, form=form)

# Registro de colaboradores
@page.route("/colaborador/new", methods=['GET', 'POST'])
@login_required
def new_colaborador():
    form = ColaboradoresForm(request.form)  # Recibe como parametro el form
    # Capturamos las areas y se pasa a lista
    area = Areas.query.order_by(Areas.area_name.asc()).all()
    areas = []
    for a in area:
        areas.append(a.area_name)
    tdoc = sorted(["Cedula de Ciudadanía", "Cedula Extranjeria", "Pasaporte"])
    tcon = sorted(["Termino Indefinido", "Contrato de Aprendizaje", "Obra labor"])

    # Capturamos los cargos desde la db y pasamos a lista
    cargo = Cargos.query.order_by(Cargos.charges.asc()).all()
    select_cargos = []
    for carg in cargo:
        select_cargos.append(carg.charges)

    # Recoleccion de Datos
    tip_doc = request.form.get("doct")
    cont = request.form.get("contrato")
    carg = request.form.get("cargos")
    ares = request.form.get("area")

    if request.method == 'POST' and form.validate():    # Validamos el tipo de peticion realizada y form
        colaborador = Colaborador.create_element(form.full_name.data, tip_doc,
                                                form.number_doc.data, form.admission_date.data,
                                                cont, carg, form.salary.data, form.email.data, ares)
        if colaborador:
            flash(COLABORADOR_CREATED)
            return redirect(url_for('.lista_colaboradores', page_num=1))

    return render_template('views/colaborador/nuevo.html', title='Nuevo Colaborador',
                            form=form, ar=areas, tdoc=tdoc, carg=select_cargos, cont=tcon)

@page.route('/colaborador/list/<int:page_num>')
@login_required
def lista_colaboradores(page_num):  # Generamos dos parametros primer la pagina donde estoy, y elementos a mostrar
    # Este atributo paginate nos debuelve un objeto con los datos
    # all_colaboradores = Colaborador.query.order_by(Colaborador.full_name.asc()).all()
    all_colaboradores = Colaborador.query.order_by(Colaborador.full_name.asc()).paginate(per_page=6, page=page_num, error_out=True)
    return render_template('views/colaborador/listas.html', title="Colaboradores",
                            colaborador=all_colaboradores)

@page.route('/colaborador/edit/<int:id_colab>', methods=['GET', 'POST'])
@login_required
def edit_colaboradores(id_colab):
    colab = Colaborador.query.get_or_404(id_colab)  # Manejamos el id por medio de 404
    form = ColaboradoresForm(request.form, obj=colab)     # Pintamos los valores del obj al form

    cargo = Cargos.query.order_by(Cargos.charges.asc()).all()
    select_cargos = []
    for carg in cargo:
        select_cargos.append(carg.charges)

    # Capturamos las areas y se pasa a lista
    area = Areas.query.order_by(Areas.area_name.asc()).all()
    areas = []
    for a in area:
        areas.append(a.area_name)

    tdoc = sorted(["Cedula de Ciudadanía", "Cedula Extranjeria", "Pasaporte"])
    tcon = sorted(["Término Indefinido", "Contrato de Aprendizaje", "Hora labor"])

    if request.method == "POST": # and form.validate():
        tipo_doct = request.form.get("tpdoc")
        tipo_cont = request.form.get("tpcon")
        cargo = request.form.get("cargo")
        areas = request.form.get("area")
        colaborador = Colaborador.update_element(colab.id, form.full_name.data, str(tipo_doct),
                                                form.number_doc.data, form.admission_date.data,
                                                str(tipo_cont), str(cargo),
                                                form.salary.data, form.email.data, str(areas))
        if colaborador:
            flash(COLABORADOR_UPDATED)
            return redirect(url_for('.lista_colaboradores', page_num=1 ))

    return render_template('views/colaborador/edit.html', title='Editar Colaborador',
                            form=form, cargo=select_cargos, tdoc=tdoc, tcon=tcon, areas=areas)

@page.route("/colaborador/delete/<int:id_colab>")
@login_required
def delete_colaborador(id_colab):
    colab = Colaborador.query.get_or_404(id_colab)

    if Colaborador.delete_element(colab.id):
        flash(COLABORADOR_DELETED)
        return redirect(url_for('.lista_colaboradores', page_num=1))

# Registro de temperatura de colaboradores
@page.route("/Temperatura", methods=['GET', 'POST'])
def registTemp():
    title = 'Registro Temperatura'
    data = registro_temperatura.query.all()
    form = RegistTempForm(request.form)  # Recibe como parametro el form
    listUsuarios = [(usua.id, usua.full_name) for usua in Colaborador.query.order_by(Colaborador.full_name.asc()).all()]

    days = [{'id': 1, 'dia': 'Lunes'}, {'id': 2, 'dia': 'Martes'}, {'id': 3, 'dia': 'Miércoles'},
            {'id': 4, 'dia': 'Jueves'}, {'id': 5, 'dia': 'Viernes'}]

    # Pausas activas Registro Temperatura
    pausas = request.form.get('PAUSAS')

    dias = [(day['id'], day['dia']) for day in days]
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        select = request.form.get('user_select')

        if not select == "Seleccione su Nombre....":
            dia = request.form.get('dia_semana')
            h1 = request.form.get('lav1')
            h2 = request.form.get('lav2')
            h3 = request.form.get('lav3')
            horas = '{} {} {}'.format(h1, h2, h3)
            # Validar la temperatura de entrada y salida
            ting = float(form.entry_temperature.data)
            tsal = float(form.outlet_temperature.data)
            if ting <= float(30.0) or ting >= float(49.0):
                flash(TEMP_ERROR, 'error')
            elif tsal <= float(30.0) or tsal >= float(49.0):
                flash(TEMP_ERROR, 'error')
            else:
                # Validar fechas por formato
                toma = form.completion_date.data
                try:
                    f = datetime.strptime(toma, '%Y-%m-%d')
                    fecha = date(f.year, f.month, f.day)
                    # Validar si el registro que se esta ingresando a existe
                    info = 0
                    for i in data:
                        if i.full_name == str(select) and i.completion_date == str(fecha):
                            info += 1
                    if info >= 1:
                        flash(EXISTING_REGISTRY, 'error')
                    else:
                        regisTemp = registro_temperatura.create_element(str(select), form.ages.data,
                                                            str(fecha), str(dia), str(horas), form.time_entry.data,
                                                            form.entry_temperature.data, form.departure_time.data,
                                                            form.outlet_temperature.data, str(pausas),
                                                            form.observations.data)
                        if regisTemp:
                            flash(TEMPERATURA_CREATE)
                            return redirect(url_for('.index'))
                except ValueError:
                    flash(FECHA_INCORRECTA, 'error')
        else:
            flash(NAME_SELECT, 'error')

    return render_template('views/registros/registroTemperatura.html', title = title, form=form,
                            users_names=listUsuarios, dia=dias)

# Auto reporte de salud de los colaboradores
@page.route("/AutoReporte", methods=['GET', 'POST'])
def autoreporte():
    title = 'Auto-Reporte'
    form = AutoReporteForm(request.form)  # Recibe como parametro el form
    # Realizamos las peticiones a la db para recuperar los nombres de los colaboradores
    listUsuario = [(usua.id, usua.full_name) for usua in Colaborador.query.order_by(Colaborador.full_name.asc()).all()]

    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        select = request.form.get('user_select')
        if not select == "Seleccione su Nombre....":
            # Validar el formato de la fecha para no tener errores
            toma = form.completion_date.data
            try:
                f = datetime.strptime(toma, '%Y-%m-%d')
                fecha = date(f.year, f.month, f.day)
                tos = request.form.get("TOS")
                escalofios = request.form.get("ESCAL")
                dolor_garganta = request.form.get("DGARG")
                dolor_corporal = request.form.get("DCORP")
                dolor_cabeza = request.form.get("DCAB")
                fiebre = request.form.get("FIEBR")
                perdida_olfato = request.form.get("OLFAT")
                dificultad_respirar = request.form.get("DRESP")
                fatiga = request.form.get("FATIG")
                viajado = request.form.get("VIAJAD")
                zona_afectadas = request.form.get("ZAFECT")
                contacto_positivos = request.form.get("CPOSIT")
                contactos_sospechosos = request.form.get("CSOSPEC")

                auto_rep = Auto_reporte.create_element(str(select), str(fecha), form.eps.data,
                                                        form.pension_fund.data, form.name_contact.data,
                                                        form.relationship.data, str(tos), str(escalofios),
                                                        str(dolor_garganta), str(dolor_corporal), str(dolor_cabeza),
                                                        str(fiebre), str(perdida_olfato), str(dificultad_respirar),
                                                        str(fatiga), str(viajado), str(zona_afectadas),
                                                        str(contacto_positivos), str(contactos_sospechosos),
                                                        form.observations.data)
                if auto_rep:
                    flash(AUTO_REPORTE)
                return redirect(url_for('.index'))
            except ValueError:
                flash(FECHA_INCORRECTA, 'error')

        else:
            flash(NAME_SELECT, 'error')

    return render_template('views/registros/autoReporte.html', title = title, form=form,
                            users_names=listUsuario)

# Permisos y registro de salidas
@page.route("/permiso", methods=['GET', 'POST'])
def permiso_Salida():
    title = 'Permisos Salidas'
    form = PermisosForm(request.form)  # Recibe como parametro el form
    # Realizamos las peticiones a la db para recuperar los nombres de los colaboradores
    listUsua = [(usua.id, usua.full_name) for usua in Colaborador.query.order_by(Colaborador.full_name.asc()).all()]

    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        select = request.form.get('user_select')
        if not select == "Seleccione su Nombre....":
            # Validar el formato de la fecha para no tener errores
            toma = form.date_completion.data
            try:
                f = datetime.strptime(toma, '%Y-%m-%d')
                fecha = date(f.year, f.month, f.day)

                msalida = request.form.get("MSALIDA")
                cpji = request.form.get("PJI")

                permis = Permisos_salida.create_element(form.email.data, str(select), str(fecha), form.departure_date.data,
                                                        form.departure_time.data, form.check_in.data,
                                                        str(msalida), form.place_displacement.data,
                                                        str(cpji), form.who_authorized.data, form.observations.data)
                if permis:
                    msg = Message('Notificación de Permisos y/o Salidas',
                                    sender=current_app.config['DONT_REPLY_FROM_EMAIL'],
                                    recipients=["gestion.humana@ventaequipos.com"])
                    msg.body = "Notificación de permisos y/o salidas Venta Equipos SAS"
                    msg.html = f'''<p>El sr/sra: <strong>{select}</strong>.<br><br>
                                Solicito permiso de salida el dia {fecha}, para salir el dia {form.departure_date.data},
                                motivo del permiso {msalida} con destino {form.place_displacement.data},
                                quien autorizó es {form.who_authorized.data},
                                con las observaciónes {form.observations.data}.<br><br>
                                Cordial Saludos</p>'''
                    mail.send(msg)
                    flash(PERMIS_SAVE)
                return redirect(url_for('.index'))
            except ValueError:
                flash(FECHA_INCORRECTA, 'error')

        else:
            flash(NAME_SELECT, 'error')

    return render_template('views/registros/permisos.html', title = title, form=form,
                            users_names=listUsua)

# Realizar formulario para Actualizacion de datos
@page.route("/actualizaciones", methods=['GET', 'POST'])
def actual_datos():
    title = 'Actualización Datos'
    form = ActualizacionForm(request.form) # Recoleccion de la data desde el navegador
    # Realizamos las peticiones a la db para recuperar los nombres de los colaboradores
    listCol = [(usua.id, usua.full_name) for usua in Colaborador.query.order_by(Colaborador.full_name.asc()).all()]

    # Capturamos las areas y se pasa a lista
    area = Areas.query.order_by(Areas.area_name.asc()).all()
    areas = []
    for a in area:
        areas.append(a.area_name)

    # Capturamos los cargos desde la db y pasamos a lista
    cargo = Cargos.query.order_by(Cargos.charges.asc()).all()
    select_cargos = []
    for carg in cargo:
        select_cargos.append(carg.charges)

    # Validamos el tipo de peticion realizada al form
    if request.method == 'POST':
        select = request.form.get('user_select')
        # Validar el nombre del usuario
        if not select == "Seleccione su Nombre....":
            # Validar el formato de la fecha para no tener errores
            toma = form.date_completion.data
            try:
                f = datetime.strptime(toma, '%Y-%m-%d')
                fecha = date(f.year, f.month, f.day)

                select_area = request.form.get("area")
                select_cargo = request.form.get("cargos")
                vvp = request.form.get("VVP")
                lic = request.form.get("LIC")
                vhp = request.form.get("VHP")
                dti = request.form.get("TYD")
                sexo = request.form.get("SEXO")
                cuenta = request.form.get("CUENTA")
                stado_civil = request.form.get("STCIVIL")
                conmed = request.form.get("CONMED")
                alerg = request.form.get("ALERG")
                enfimp = request.form.get("ENFIMP")
                bach = request.form.get("BACH")
                tec = request.form.get("TEC")
                tecnol = request.form.get("TECNOL")
                univ = request.form.get("UNIV")
                postg = request.form.get("POSTG")
                otro = request.form.get("OTRO")
                nveled1 = request.form.get("NIVED1")
                nveled2 = request.form.get("NIVED2")
                nveled3 = request.form.get("NIVED3")
                juram = request.form.get("JURAM")
                firm = request.form.get("FIRMA")

                act_datos = Actualizacion_datos.create_element(str(fecha), str(select), form.stratum.data, form.home_address.data, form.neighborhood.data,
                                                            form.location.data, str(vvp), form.phone.data, form.cellular.data, form.city.data, str(lic),
                                                            form.motorcycle.data, form.car.data, form.category.data, str(vhp), str(dti),
                                                            form.identity_document.data, form.expedition_place.data, form.expedition_date.data,
                                                            form.military_card.data, form.district.data,
                                                            form.birthdate.data, form.place_birth.data, str(sexo), form.nationality.data, form.rh.data, str(select_cargo),
                                                            str(select_area), form.personal_mail.data, form.date_admission.data, form.account_number.data, form.entity.data,
                                                            str(cuenta), form.eps.data, form.pension_fund.data, form.Layoffs.data, form.arl.data, form.compensation_box.data,
                                                            str(stado_civil), form.full_name_spouse.data, form.number_children.data, form.emer_fullname.data,
                                                            form.emer_parentesco.data, form.emer_direction.data, form.emer_city.data, form.emer_cellular.data,
                                                            form.emer_phone.data, str(conmed), form.Which_medications.data, str(alerg),
                                                            form.which_allergy.data, str(enfimp), form.which_diseases.data, str(bach), form.entity_bachelor.data,
                                                            str(tec), form.title_technical.data, str(tecnol), form.title_technologist.data, str(univ),
                                                            form.title_academic.data, str(postg), form.title_postgraduate.data, str(otro), form.title_others.data,
                                                            form.dependents_name1.data, form.dependents_relationship1.data,
                                                            form.dependents_birthdate1.data, form.dependents_age1.data, str(nveled1),
                                                            form.dependents_name2.data, form.dependents_relationship2.data,
                                                            form.dependents_birthdate2.data, form.dependents_age2.data, str(nveled2),
                                                            form.dependents_name3.data, form.dependents_relationship3.data,
                                                            form.dependents_birthdate3.data, form.dependents_age3.data, str(nveled3), str(juram), str(firm))

                if act_datos:
                    flash(ACTU_DATOS)
                return redirect(url_for('.index'))
            except ValueError:
                flash(FECHA_INCORRECTA, 'error')

        else:
            flash(NAME_SELECT, 'error')

    return render_template('views/registros/actualizaciones.html', title = title,
                            form=form, users_names=listCol, selarea=areas, selec_cargo=select_cargos)

@page.route("/reports")
@login_required
def reportes():
    title = 'Dashboard'

    # Realizamos la lista de usuarios registrados en las base de datos
    rev = Cantida_colaborador.query.all()
    emp = 0
    for i in rev:
        emp = int(i.quantity)

    cants = len(Colaborador.query.all())
    # cantidad de usuarios registrados
    user = "Cant. de Colaboradores"
    cant = str(cants)
    porje = "{:.2f}%".format(100*(cants/emp))

    # Cantidad de pruebas en el dia
    txt_dia = "N°. pruebas de Temp. de Ayer"
    a = datetime.today() - timedelta(days=1)
    ayer = date(a.year, a.month, a.day)
    pb_dia = len(registro_temperatura.query.filter(registro_temperatura.completion_date == ayer).all())
    pb_porj = "{:.2f}%".format(100*(pb_dia/emp))

    # Validar el mes completo para saber quien cuantos se han realizado durante el mes
    pxmes = "N° de Pruebas de Temperatura"
    mes = datetime.today() - timedelta(days=30)
    rtemp = len(registro_temperatura.query.filter(registro_temperatura.completion_date >= mes).all())
    perm = len(Permisos_salida.query.filter(Permisos_salida.completion_date >= mes).all())

    return render_template('views/registros/reports.html', title=title, user=user, cant=cant,
                            cent=porje, txt=txt_dia, pb_txt=pb_dia, pbxdia=pb_porj, pxmes=pxmes,
                            ptxmes=rtemp,  perm=perm)

@page.route("/configuraciones")
@login_required
def configuraciones():
    title = 'Configuraciones'

    # capturamos la info de la tabla de cantidad de colaboradores
    cant_col = Cantida_colaborador.query.all()

    # Capturamos la informacion con los cargos de la compañia
    cargo = Cargos.query.order_by(Cargos.charges.asc()).all()

    # Capturamos la informacion de las Areas de la compañia
    area = Areas.query.order_by(Areas.area_name.asc()).all()

    return render_template('views/registros/configuraciones.html', title=title,
                            cant=cant_col, cargo=cargo, area=area)

# Editar la cantidad de Colaboradores
@page.route("/cantidad/edit/<int:id_cant>", methods=['POST'])
@login_required
def edit_cantidad(id_cant):
    # Recoleccion de Datos
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        descript = request.form.get('quantity')
        cant = Cantida_colaborador.update_element(id_cant, descript)
        if cant:
            flash(UPDATE_QUANTITY)
            return redirect(url_for('.configuraciones'))

    return redirect(url_for('.configuraciones'))

# Registro de Area nuevas
@page.route("/area/new", methods=['POST'])
@login_required
def new_area():
    # Recoleccion de Datos
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        descript = request.form.get('area')
        area = Areas.create_element(descript)
        if area:
            flash(AREA_CREATED)
            return redirect(url_for('.configuraciones'))

    return redirect(url_for('.configuraciones'))

# Editar los area de la compañia
@page.route("/area/edit/<int:id_area>", methods=['POST'])
@login_required
def edit_area(id_area):
    # Recoleccion de Datos
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        descript = request.form.get('area')
        area = Areas.update_element(id_area, descript)
        if area:
            flash(UPDATE_AREA)
            return redirect(url_for('.configuraciones'))

    return redirect(url_for('.configuraciones'))

# Eliminar los area de la compañia
@page.route("/area/delete/<int:id_area>")
@login_required
def delete_area(id_area):
    area = Areas.query.get_or_404(id_area)

    if Areas.delete_element(area.id):
        flash(AREA_DELETED)
        return redirect(url_for('.configuraciones'))

# Registro de nuevos cargos
@page.route("/cargos/new", methods=['POST'])
@login_required
def new_cargos():
    # Recoleccion de Datos
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        post = request.form.get('carg').upper()
        carg = Cargos.create_element(post)
        if carg:
            flash(CARGO_CREATED)
            return redirect(url_for('.configuraciones'))

    return redirect(url_for('.configuraciones'))

# Editar los cargos de la compañia
@page.route("/cargos/edit/<int:id_cargo>", methods=['POST'])
@login_required
def edit_cargos(id_cargo):
    # Recoleccion de Datos
    if request.method == 'POST':    # Validamos el tipo de peticion realizada y form
        descript = request.form.get('carg')
        carg = Cargos.update_element(id_cargo, descript)
        if carg:
            flash(UPDATE_CARGO)
            return redirect(url_for('.configuraciones'))

    return redirect(url_for('.configuraciones'))

# Eliminar los cargos de la compañia
@page.route("/cargos/delete/<int:id_cargo>")
@login_required
def delete_cargo(id_cargo):
    carg = Cargos.query.get_or_404(id_cargo)

    if Cargos.delete_element(carg.id):
        flash(CARGO_DELETED)
        return redirect(url_for('.configuraciones'))

@page.route("/reports/reporte_all")
@login_required
def download_reports():
    # Recolectamos todo la informacion de la db
    # eg = excel_gf()
    datos = registro_temperatura.query.all()
    datos_auto = Auto_reporte.query.all()
    # eg.exportar_all_temp(str(datos))

    #output in bytes
    output = BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()

    # add a sheet
    tp = workbook.add_sheet('Temperatura')
    ar = workbook.add_sheet('Auto-Reporte')

    # Agregar encabezado Temperatura
    tp.write(0, 0, 'Nombre Completo')
    tp.write(0, 1, 'Edad')
    tp.write(0, 2, 'Fecha de Dilingenciamiento')
    tp.write(0, 3, 'Dia')
    tp.write(0, 4, 'Lavado de manos')
    tp.write(0, 5, 'Hora Ingreso')
    tp.write(0, 6, 'Temp. Ingreso')
    tp.write(0, 7, 'Hora Salida')
    tp.write(0, 8, 'Temp. Salida')
    tp.write(0, 9, 'Observaciones')
    # agregar columnas para temperatura
    temp = 0
    for tem in datos:
        tp.write(temp+1, 0, tem.full_name)
        tp.write(temp+1, 1, str(tem.ages))
        tp.write(temp+1, 2, tem.completion_date)
        tp.write(temp+1, 3, tem.days)
        tp.write(temp+1, 4, tem.handwashing)
        tp.write(temp+1, 5, tem.time_entry)
        tp.write(temp+1, 6, str(tem.entry_temperature))
        tp.write(temp+1, 7, tem.departure_time)
        tp.write(temp+1, 8, str(tem.outlet_temperature))
        tp.write(temp+1, 9, tem.observations)
        temp += 1

    # Agregar pestaña de autoreporte al mismo excel
    ar.write(0, 0, 'Nombre Completo')
    ar.write(0, 1, 'Fecha de Dilingenciamiento')
    ar.write(0, 2, 'Eps')
    ar.write(0, 3, 'Fondo de pensiones')
    ar.write(0, 4, 'Contacto')
    ar.write(0, 5, 'Parentesto')
    ar.write(0, 6, 'Tos')
    ar.write(0, 7, 'Escalofrios')
    ar.write(0, 8, 'Dolor de garganta')
    ar.write(0, 9, 'Dolor corporal')
    ar.write(0, 10, 'Dolor de cabeza')
    ar.write(0, 11, 'Fiebre')
    ar.write(0, 12, 'Perdida de olfato')
    ar.write(0, 13, 'Difucultad para respirar')
    ar.write(0, 14, 'Fatiga')
    ar.write(0, 15, 'Viajado')
    ar.write(0, 16, 'Zona afectadas')
    ar.write(0, 17, 'Contactos con personas positivas')
    ar.write(0, 18, 'Contactos con personas sospechosos')
    ar.write(0, 19, 'Observaciones')
    # agregar columnas para temperatura

    aut = 0
    for row in datos_auto:
        ar.write(aut+1, 0, row.full_name)
        ar.write(aut+1, 1, row.completion_date)
        ar.write(aut+1, 2, row.eps)
        ar.write(aut+1, 3, row.pension_fund)
        ar.write(aut+1, 4, row.name_contact)
        ar.write(aut+1, 5, row.relationship)
        ar.write(aut+1, 6, row.tos)
        ar.write(aut+1, 7, row.escalofrios)
        ar.write(aut+1, 8, row.dolor_garganta)
        ar.write(aut+1, 9, row.dolor_corporal)
        ar.write(aut+1, 10, row.dolor_cabeza)
        ar.write(aut+1, 11, row.fiebre)
        ar.write(aut+1, 12, row.perdida_olfato)
        ar.write(aut+1, 13, row.dificultad_respirar)
        ar.write(aut+1, 14, row.fatiga)
        ar.write(aut+1, 15, row.viajado)
        ar.write(aut+1, 16, row.zona_afectadas)
        ar.write(aut+1, 17, row.contacto_positivos)
        ar.write(aut+1, 18, row.contactos_sospechosos)
        ar.write(aut+1, 19, row.observations)
        aut += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Reporte_empreados.xls"})

# Generamos el excel para las temperaturas por fecha
@page.route("/reports/reporte_date")
@login_required
def download_date():
    # Recolectamos las dos parametros que vienen por get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    # Recolectamos todo la informacion de la db
    datos = registro_temperatura.query.all()

    # Definimos la salida en bytes - output in bytes
    output = BytesIO()
    # Creamos las hojas para trabjar con excel - create WorkBook object
    workbook = xlwt.Workbook()

    # Agregamos la nueva pestaña - add a sheet
    tp = workbook.add_sheet('Temperatura')

    # Agregar encabezado Temperatura
    tp.write(0, 0, 'Nombre Completo')
    tp.write(0, 1, 'Edad')
    tp.write(0, 2, 'Fecha de Dilingenciamiento')
    tp.write(0, 3, 'Dia')
    tp.write(0, 4, 'Lavado de manos')
    tp.write(0, 5, 'Hora Ingreso')
    tp.write(0, 6, 'Temp. Ingreso')
    tp.write(0, 7, 'Hora Salida')
    tp.write(0, 8, 'Temp. Salida')
    tp.write(0, 9, 'Pausas Activas')
    tp.write(0, 10, 'Observaciones')

    # Iniciamos el contador para ir agregando una nueva fila
    temp = 0
    for tem in datos:
        if tem.completion_date >= str(inicio) and tem.completion_date <= str(fin):
            tp.write(temp+1, 0, tem.full_name)
            tp.write(temp+1, 1, str(tem.ages))
            tp.write(temp+1, 2, tem.completion_date)
            tp.write(temp+1, 3, tem.days)
            tp.write(temp+1, 4, tem.handwashing)
            tp.write(temp+1, 5, tem.time_entry)
            tp.write(temp+1, 6, str(tem.entry_temperature))
            tp.write(temp+1, 7, tem.departure_time)
            tp.write(temp+1, 8, str(tem.outlet_temperature))
            tp.write(temp+1, 9, tem.active_breaks)
            tp.write(temp+1, 10, tem.observations)
            temp += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=reporte_temp_por_fecha.xls"})

# Link para descargar el auto-reporte de los colaboradores
@page.route("/reports/auto_date")
@login_required
def downAuto_date():
    # Se captura los datos que vienen por peticion get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    # Recolectamos todo la informacion de la db
    datos_auto = Auto_reporte.query.all()

    #output in bytes
    output = BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()
    # add a sheet
    ar = workbook.add_sheet('Auto-Reporte')

    # Agregar pestaña de autoreporte al mismo excel
    ar.write(0, 0, 'Nombre Completo')
    ar.write(0, 1, 'Fecha de Dilingenciamiento')
    ar.write(0, 2, 'Eps')
    ar.write(0, 3, 'Fondo de pensiones')
    ar.write(0, 4, 'Contacto')
    ar.write(0, 5, 'Parentesto')
    ar.write(0, 6, 'Tos')
    ar.write(0, 7, 'Escalofrios')
    ar.write(0, 8, 'Dolor de garganta')
    ar.write(0, 9, 'Dolor corporal')
    ar.write(0, 10, 'Dolor de cabeza')
    ar.write(0, 11, 'Fiebre')
    ar.write(0, 12, 'Perdida de olfato')
    ar.write(0, 13, 'Difucultad para respirar')
    ar.write(0, 14, 'Fatiga')
    ar.write(0, 15, 'Viajado')
    ar.write(0, 16, 'Zona afectadas')
    ar.write(0, 17, 'Contactos con personas positivas')
    ar.write(0, 18, 'Contactos con personas sospechosos')
    ar.write(0, 19, 'Observaciones')
    # agregar columnas para temperatura

    aut = 0
    for row in datos_auto:
        if row.completion_date >= str(inicio) and row.completion_date <= str(fin):
            ar.write(aut+1, 0, row.full_name)
            ar.write(aut+1, 1, row.completion_date)
            ar.write(aut+1, 2, row.eps)
            ar.write(aut+1, 3, row.pension_fund)
            ar.write(aut+1, 4, row.name_contact)
            ar.write(aut+1, 5, row.relationship)
            ar.write(aut+1, 6, row.tos)
            ar.write(aut+1, 7, row.escalofrios)
            ar.write(aut+1, 8, row.dolor_garganta)
            ar.write(aut+1, 9, row.dolor_corporal)
            ar.write(aut+1, 10, row.dolor_cabeza)
            ar.write(aut+1, 11, row.fiebre)
            ar.write(aut+1, 12, row.perdida_olfato)
            ar.write(aut+1, 13, row.dificultad_respirar)
            ar.write(aut+1, 14, row.fatiga)
            ar.write(aut+1, 15, row.viajado)
            ar.write(aut+1, 16, row.zona_afectadas)
            ar.write(aut+1, 17, row.contacto_positivos)
            ar.write(aut+1, 18, row.contactos_sospechosos)
            ar.write(aut+1, 19, row.observations)
            aut += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=AutoReporte_por_Fechas.xls"})

# Link para descargar el auto-reporte de los colaboradores
@page.route("/reports/gf_temperatura")
@login_required
def gf_temp():
    # Se captura los datos que vienen por peticion get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    # create a random Pandas dataframe
    datos_temp = registro_temperatura.query.all()

    # Declaramos la creacion de los archivos y convertilos en binarios
    temp_gf = BytesIO()
    workbook = xlsxwriter.Workbook(temp_gf)
    worksheet = workbook.add_worksheet("Temperatura")

    col = []
    new = []
    # Estraemos la data de la base de datos y la montamos en una lista
    for t in datos_temp:
        if t.completion_date >= str(inicio) and t.completion_date <= str(fin):
            new_data = [t.full_name, t.completion_date, t.entry_temperature, t.outlet_temperature]
            colabor = [t.full_name, t.days, t.entry_temperature, t.outlet_temperature]
            col.append(colabor)
            new.append(new_data)

    # Generamos las listas con la info de cada colaborador
    user = defaultdict(list)
    for t in new:
        user[t[0]].append(t[1:])


    # Opciones generales para todos las vistas
    tomas = ["Ingreso", "Salida"]
    tittle = 1
    valores = 2
    for k, v in user.items():
        fechas = []
        temperatura = []
        for item in v:
            f = item[0]
            r = datetime.strptime(f, '%Y-%m-%d')
            q = datetime.strftime(r, '%d/%m/%Y')
            fechas.append(q)
            item.pop(0)
            temperatura.append(list(map(float, item)))

        if len(temperatura) == 4:
            for _ in range(1):
                # Create a new Chart object.
                grafica = workbook.add_chart({'type': 'column'})

                worksheet.write_column('A{}'.format(int(tittle)), ['Categoria'])
                worksheet.write_column('B{}'.format(int(tittle)), [str(fechas[0])])
                worksheet.write_column('C{}'.format(int(tittle)), [str(fechas[1])])
                worksheet.write_column('D{}'.format(int(tittle)), [str(fechas[2])])
                worksheet.write_column('E{}'.format(int(tittle)), [str(fechas[3])])

                worksheet.write_column('A{}'.format(int(valores)), tomas)

                # Datos de Para generar cada usuario----------------------------------------------------------------
                worksheet.write_column('B{}'.format(int(valores)), temperatura[0])        # lunes
                worksheet.write_column('C{}'.format(int(valores)), temperatura[1])        # Martes
                worksheet.write_column('D{}'.format(int(valores)), temperatura[2])        # Miercoles
                worksheet.write_column('E{}'.format(int(valores)), temperatura[3])        # Jueves

                # Configurar los datos
                grafica.set_title({'name': k})
                grafica.add_series({'categories': '=Temperatura!B{}:F{}'.format(int(tittle),int(tittle)),
                                'values': '=Temperatura!$B${}:$F${}'.format(int(valores),int(valores)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A2:A2',
                                })
                grafica.add_series({'values': '=Temperatura!$B${}:$F${}'.format(int(valores)+1, int(valores+1)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A3:A3',
                                })
                grafica.set_x_axis({'name': "Temperatura",
                                'name_font': {'size': 10, 'bold': True},
                                'num_font':  {'italic': True },})
                # Generamos las graficas para tos
                worksheet.insert_chart('H{}'.format(int(valores)), grafica)
                tittle += 18
                valores += 18
                grafica = None
            continue

        elif len(temperatura) == 3:
            for _ in range(1):
                # Create a new Chart object.
                grafica = workbook.add_chart({'type': 'column'})

                worksheet.write_column('A{}'.format(int(tittle)), ['Categoria'])
                worksheet.write_column('B{}'.format(int(tittle)), [str(fechas[0])])
                worksheet.write_column('C{}'.format(int(tittle)), [str(fechas[1])])
                worksheet.write_column('D{}'.format(int(tittle)), [str(fechas[2])])

                worksheet.write_column('A{}'.format(int(valores)), tomas)

                # Datos de Para generar cada usuario----------------------------------------------------------------
                worksheet.write_column('B{}'.format(int(valores)), temperatura[0])        # lunes
                worksheet.write_column('C{}'.format(int(valores)), temperatura[1])        # Martes
                worksheet.write_column('D{}'.format(int(valores)), temperatura[2])        # Miercoles

                # Configurar los datos
                grafica.set_title({'name': k})
                grafica.add_series({'categories': '=Temperatura!B{}:F{}'.format(int(tittle),int(tittle)),
                                'values': '=Temperatura!$B${}:$F${}'.format(int(valores),int(valores)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A2:A2',
                                })
                grafica.add_series({'values': '=Temperatura!$B${}:$F${}'.format(int(valores)+1, int(valores+1)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A3:A3',
                                })
                grafica.set_x_axis({'name': "Temperatura",
                                'name_font': {'size': 10, 'bold': True},
                                'num_font':  {'italic': True },})
                # Generamos las graficas para tos
                worksheet.insert_chart('H{}'.format(int(valores)), grafica)
                tittle += 18
                valores += 18
                grafica = None
            continue

        elif len(temperatura) == 2:
            for _ in range(1):
                # Create a new Chart object.
                grafica = workbook.add_chart({'type': 'column'})

                worksheet.write_column('A{}'.format(int(tittle)), ['Categoria'])
                worksheet.write_column('B{}'.format(int(tittle)), [str(fechas[0])])
                worksheet.write_column('C{}'.format(int(tittle)), [str(fechas[1])])

                worksheet.write_column('A{}'.format(int(valores)), tomas)

                # Datos de Para generar cada usuario----------------------------------------------------------------
                worksheet.write_column('B{}'.format(int(valores)), temperatura[0])        # lunes
                worksheet.write_column('C{}'.format(int(valores)), temperatura[1])        # Martes

                # Configurar los datos
                grafica.set_title({'name': k})
                grafica.add_series({'categories': '=Temperatura!B{}:F{}'.format(int(tittle),int(tittle)),
                                'values': '=Temperatura!$B${}:$F${}'.format(int(valores),int(valores)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A2:A2',
                                })
                grafica.add_series({'values': '=Temperatura!$B${}:$F${}'.format(int(valores)+1, int(valores+1)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A3:A3',
                                })
                grafica.set_x_axis({'name': "Temperatura",
                                'name_font': {'size': 10, 'bold': True},
                                'num_font':  {'italic': True },})
                # Generamos las graficas para tos
                worksheet.insert_chart('H{}'.format(int(valores)), grafica)
                tittle += 18
                valores += 18
                grafica = None
            continue

        elif len(temperatura) == 1:
            for _ in range(1):
                # Create a new Chart object.
                grafica = workbook.add_chart({'type': 'column'})

                worksheet.write_column('A{}'.format(int(tittle)), ['Categoria'])
                worksheet.write_column('B{}'.format(int(tittle)), [str(fechas[0])])

                worksheet.write_column('A{}'.format(int(valores)), tomas)

                # Datos de Para generar cada usuario----------------------------------------------------------------
                worksheet.write_column('B{}'.format(int(valores)), temperatura[0])        # lunes

                # Configurar los datos
                grafica.set_title({'name': k})
                grafica.add_series({'categories': '=Temperatura!B{}:F{}'.format(int(tittle),int(tittle)),
                                'values': '=Temperatura!$B${}:$F${}'.format(int(valores),int(valores)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A2:A2',
                                })
                grafica.add_series({'values': '=Temperatura!$B${}:$F${}'.format(int(valores)+1, int(valores+1)),
                                'data_labels': {'series_name': False, 'value':True},
                                'name': '=Temperatura!A3:A3',
                                })
                grafica.set_x_axis({'name': "Temperatura",
                                'name_font': {'size': 10, 'bold': True},
                                'num_font':  {'italic': True },})
                # Generamos las graficas para tos
                worksheet.insert_chart('H{}'.format(int(valores)), grafica)
                tittle += 18
                valores += 18
                grafica = None
            continue

        for _ in range(1):
            # Create a new Chart object.
            grafica = workbook.add_chart({'type': 'column'})

            worksheet.write_column('A{}'.format(int(tittle)), ['Categoria'])
            worksheet.write_column('B{}'.format(int(tittle)), [str(fechas[0])])
            worksheet.write_column('C{}'.format(int(tittle)), [str(fechas[1])])
            worksheet.write_column('D{}'.format(int(tittle)), [str(fechas[2])])
            worksheet.write_column('E{}'.format(int(tittle)), [str(fechas[3])])
            worksheet.write_column('F{}'.format(int(tittle)), [str(fechas[4])])

            worksheet.write_column('A{}'.format(int(valores)), tomas)

            # Datos de Para generar cada usuario----------------------------------------------------------------
            worksheet.write_column('B{}'.format(int(valores)), temperatura[0])        # lunes
            worksheet.write_column('C{}'.format(int(valores)), temperatura[1])        # Martes
            worksheet.write_column('D{}'.format(int(valores)), temperatura[2])        # Miercoles
            worksheet.write_column('E{}'.format(int(valores)), temperatura[3])        # Jueves
            worksheet.write_column('F{}'.format(int(valores)), temperatura[4])        # Viernes

            # Configurar los datos
            grafica.set_title({'name': k})
            grafica.add_series({'categories': '=Temperatura!B{}:F{}'.format(int(tittle),int(tittle)),
                            'values': '=Temperatura!$B${}:$F${}'.format(int(valores),int(valores)),
                            'data_labels': {'series_name': False, 'value':True},
                            'name': '=Temperatura!A2:A2',
                            })
            grafica.add_series({'values': '=Temperatura!$B${}:$F${}'.format(int(valores)+1, int(valores+1)),
                            'data_labels': {'series_name': False, 'value':True},
                            'name': '=Temperatura!A3:A3',
                            })
            grafica.set_x_axis({'name': "Temperatura",
                            'name_font': {'size': 10, 'bold': True},
                            'num_font':  {'italic': True },})
            # Generamos las graficas para tos
            worksheet.insert_chart('H{}'.format(int(valores)), grafica)
            tittle += 18
            valores += 18
            grafica = None

    # Se encapsula el archivo en excel para ser enviado al navegador
    workbook.close()
    xlsx_temp = temp_gf.getvalue()

    return Response(xlsx_temp, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Grafica_Temperatura_Fechas.xlsx"})

# Link para descargar el auto-reporte de los colaboradores
@page.route("/reports/gf_autoreporte")
@login_required
def gf_autorpt():

    # Se captura los datos que vienen por peticion get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    output_gf = BytesIO()
    workbook = xlsxwriter.Workbook(output_gf)
    worksheet = workbook.add_worksheet("Graficas")

    # Create a new Chart object.
    chart_tos = workbook.add_chart({'type': 'column'})
    chart_escalofrios = workbook.add_chart({'type': 'column'})
    chart_garganta = workbook.add_chart({'type': 'column'})
    chart_corparal = workbook.add_chart({'type': 'column'})
    chart_cabeza = workbook.add_chart({'type': 'column'})
    chart_fiebre = workbook.add_chart({'type': 'column'})
    chart_polfato = workbook.add_chart({'type': 'column'})
    chart_respirar = workbook.add_chart({'type': 'column'})
    chart_fatiga = workbook.add_chart({'type': 'column'})
    chart_viajado = workbook.add_chart({'type': 'column'})
    chart_zafec = workbook.add_chart({'type': 'column'})
    chart_cont = workbook.add_chart({'type': 'column'})
    chart_sospec = workbook.add_chart({'type': 'column'})

    # Write some data to add to plot on the chart.
     # create a random Pandas dataframe
    datos_graficas = Auto_reporte.query.all()
    listdatos = []
    listescal = []
    listdgarganta = []
    listcorporal = []
    listcabeza = []
    listfiebre = []
    listpolfato = []
    listrespirar = []
    listfatiga = []
    listviaj = []
    listzafectadas = []
    listcontac = []
    listsospec = []
    for i in datos_graficas:
        if i.completion_date >= str(inicio) and i.completion_date <= str(fin):
            tos = [i.tos.count("SI"), i.tos.count("NO"), i.tos.count("ANTES")]
            escal = [i.escalofrios.count("SI"), i.escalofrios.count("NO"), i.escalofrios.count("ANTES")]
            dgarganta = [i.dolor_garganta.count("SI"), i.dolor_garganta.count("NO"), i.dolor_garganta.count("ANTES")]
            dcorporal = [i.dolor_corporal.count("SI"), i.dolor_corporal.count("NO"), i.dolor_corporal.count("ANTES")]
            dcabeza = [i.dolor_cabeza.count("SI"), i.dolor_cabeza.count("NO"), i.dolor_cabeza.count("ANTES")]
            fieb = [i.fiebre.count("SI"), i.fiebre.count("NO"), i.fiebre.count("ANTES")]
            polfat = [i.perdida_olfato.count("SI"), i.perdida_olfato.count("NO"), i.perdida_olfato.count("ANTES")]
            respirar = [i.dificultad_respirar.count("SI"), i.dificultad_respirar.count("NO"), i.dificultad_respirar.count("ANTES")]
            fatiga = [i.fatiga.count("SI"), i.fatiga.count("NO"), i.fatiga.count("ANTES")]
            viajado = [i.viajado.count("SI"), i.viajado.count("NO"), i.viajado.count("ANTES")]
            zafectad = [i.zona_afectadas.count("SI"), i.zona_afectadas.count("NO"), i.zona_afectadas.count("ANTES")]
            contact = [i.contacto_positivos.count("SI"), i.contacto_positivos.count("NO"), i.contacto_positivos.count("ANTES")]
            sospechos = [i.contactos_sospechosos.count("SI"), i.contactos_sospechosos.count("NO"), i.contactos_sospechosos.count("ANTES")]
            listdatos.append(tos)
            listescal.append(escal)
            listdgarganta.append(dgarganta)
            listcorporal.append(dcorporal)
            listcabeza.append(dcabeza)
            listfiebre.append(fieb)
            listpolfato.append(polfat)
            listrespirar.append(respirar)
            listfatiga.append(fatiga)
            listviaj.append(viajado)
            listzafectadas.append(zafectad)
            listcontac.append(contact)
            listsospec.append(sospechos)

    tos = [sum(x) for x in zip(*listdatos)]
    escal = [sum(x) for x in zip(*listescal)]
    dgarg = [sum(x) for x in zip(*listdgarganta)]
    dcorp = [sum(x) for x in zip(*listcorporal)]
    dcab = [sum(x) for x in zip(*listcabeza)]
    fiebre = [sum(x) for x in zip(*listfiebre)]
    polf = [sum(x) for x in zip(*listpolfato)]
    dresp = [sum(x) for x in zip(*listrespirar)]
    fatig = [sum(x) for x in zip(*listfatiga)]
    viajad = [sum(x) for x in zip(*listviaj)]
    zafect = [sum(x) for x in zip(*listzafectadas)]
    contp = [sum(x) for x in zip(*listcontac)]
    sosp = [sum(x) for x in zip(*listsospec)]

    # Opciones generales para todos las vistas
    option = ["SI","NO","ANTES"]

    # Datos de tos----------------------------------------------------------------------------------
    worksheet.write_column('A1', ['Categorio'])
    worksheet.write_column('B1', ['Valor'])
    worksheet.write_column('A2', option)
    worksheet.write_column('B2', tos)
    # Configurar los datos de Tos
    chart_tos.set_title({'name': '¿PRESENTA TOS RECURRENTE O ESPONTANEA HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_tos.add_series({'values': '=Graficas!$B$2:$B$4',
                        'categories': '=Graficas!A2:A4',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_tos.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})
    # Generamos las graficas para tos
    worksheet.insert_chart('C2', chart_tos)

    # Datos de escalofrios--------------------------------------------------------------------------
    worksheet.write_column('K1', ['Categorio'])
    worksheet.write_column('L1', ['Valor'])
    worksheet.write_column('K2', option)
    worksheet.write_column('L2', escal)

    # Configurar los datos de Escalofrios
    chart_escalofrios.set_title({'name': '¿PRESENTA ESCALOFRIO RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS?'})
    chart_escalofrios.add_series({'values': '=Graficas!$L$2:$L$4',
                        'categories': '=Graficas!K2:K4',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_escalofrios.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas para Escalofrios
    worksheet.insert_chart('M2', chart_escalofrios)

    # Datos de dolor de garganta---------------------------------------------------------------------
    worksheet.write_column('A18', ['Categorio'])
    worksheet.write_column('B18', ['Valor'])
    worksheet.write_column('A19', option)
    worksheet.write_column('B19', dgarg)

    # Configurar los datos
    chart_garganta.set_title({'name':'¿PRESENTA DOLOR DE GARGANTA RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_garganta.add_series({
                        'categories': '=Graficas!A19:A21',
                        'values': '=Graficas!$B$19:$B$21',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_garganta.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C19', chart_garganta)

    # Datos de dolor de corporal---------------------------------------------------------------------
    worksheet.write_column('K18', ['Categorio'])
    worksheet.write_column('L18', ['Valor'])
    worksheet.write_column('K19', option)
    worksheet.write_column('L19', dcorp)

    # Configurar los datos
    chart_corparal.set_title({'name':'¿PRESENTA DOLOR CORPORAL O MALESTAR GENERAL RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_corparal.add_series({
                        'categories': '=Graficas!K19:K21',
                        'values': '=Graficas!$L$19:$L$21',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_corparal.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('M19', chart_corparal)

    # Datos de dolor de corporal---------------------------------------------------------------------
    worksheet.write_column('A35', ['Categorio'])
    worksheet.write_column('B35', ['Valor'])
    worksheet.write_column('A36', option)
    worksheet.write_column('B36', dcab)

    # Configurar los datos
    chart_cabeza.set_title({'name':'¿PRESENTA DOLOR DE CABEZA RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_cabeza.add_series({
                        'categories': '=Graficas!A36:A38',
                        'values': '=Graficas!$B$36:$B$38',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_cabeza.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C36', chart_cabeza)

    # Datos de dolor de corporal---------------------------------------------------------------------
    worksheet.write_column('K35', ['Categorio'])
    worksheet.write_column('L35', ['Valor'])
    worksheet.write_column('K36', option)
    worksheet.write_column('L36', fiebre)

    # Configurar los datos
    chart_fiebre.set_title({'name':'¿PRESENTA FIEBRE MAYOR A 37.8 °C, RECURRENTE O ESPONTANEA HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_fiebre.add_series({
                        'categories': '=Graficas!K36:K38',
                        'values': '=Graficas!$L$36:$L$38',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_fiebre.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('M36', chart_fiebre)

    # Datos de perdida de olfato---------------------------------------------------------------------
    worksheet.write_column('A52', ['Categorio'])
    worksheet.write_column('B52', ['Valor'])
    worksheet.write_column('A53', option)
    worksheet.write_column('B53', polf)

    # Configurar los datos
    chart_polfato.set_title({'name':'¿PRESENTA PERDIDA DEL OLFATO, RECURRENTE O ESPONTANEA HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_polfato.add_series({
                        'categories': '=Graficas!A53:A55',
                        'values': '=Graficas!$B$53:$B$55',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_polfato.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C53', chart_polfato)

    # Datos de dificultad al respirar---------------------------------------------------------------------
    worksheet.write_column('K52', ['Categorio'])
    worksheet.write_column('L52', ['Valor'])
    worksheet.write_column('K53', option)
    worksheet.write_column('L53', dresp)

    # Configurar los datos
    chart_respirar.set_title({'name':'¿PRESENTA DIFICULTAD PARA RESPIRAR COMO SI NO ENTRARA AIRE A SUS PULMONES DE MANERA RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_respirar.add_series({
                        'categories': '=Graficas!K53:K55',
                        'values': '=Graficas!$L$53:$L$55',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_respirar.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('M53', chart_respirar)

    # Datos de sintomas de fatiga---------------------------------------------------------------------
    worksheet.write_column('A69', ['Categorio'])
    worksheet.write_column('B69', ['Valor'])
    worksheet.write_column('A70', option)
    worksheet.write_column('B70', fatig)

    # Configurar los datos
    chart_fatiga.set_title({'name':'¿PRESENTO FATIGA O REAL DETERIORO DE MIS MOVIMIENTOS Y MIS GANAS DE HACER ALGO, ES RECURRENTE O ESPONTANEO HOY O EN DIAS PREVIOS? (2 o 3 DIAS ANTES)'})
    chart_fatiga.add_series({
                        'categories': '=Graficas!A70:A72',
                        'values': '=Graficas!$B$70:$B$72',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_fatiga.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C70', chart_fatiga)

    # Datos de viajado en los ultimos 14 dias---------------------------------------------------------------------
    worksheet.write_column('K69', ['Categorio'])
    worksheet.write_column('L69', ['Valor'])
    worksheet.write_column('K70', option)
    worksheet.write_column('L70', viajad)

    # Configurar los datos
    chart_viajado.set_title({'name':'¿HAS VIAJADO EN LOS UTIMOS 14 DIAS FUERA DE LA CIUDAD?'})
    chart_viajado.add_series({
                        'categories': '=Graficas!k70:K72',
                        'values': '=Graficas!$L$70:$L$72',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_viajado.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('M70', chart_viajado)

    # Datos de sintomas de zonas afectadas---------------------------------------------------------------------
    worksheet.write_column('A86', ['Categorio'])
    worksheet.write_column('B86', ['Valor'])
    worksheet.write_column('A87', option)
    worksheet.write_column('B87', zafect)

    # Configurar los datos
    chart_zafec.set_title({'name':'¿HAS ESTADO EN ZONAS AFECTADAS POR COVID19?'})
    chart_zafec.add_series({
                        'categories': '=Graficas!A87:A89',
                        'values': '=Graficas!$B$87:$B$89',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_zafec.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C87', chart_zafec)

        # Datos de ha tenido contacto positivos------------------------------------------------------------
    worksheet.write_column('K86', ['Categorio'])
    worksheet.write_column('L86', ['Valor'])
    worksheet.write_column('K87', option)
    worksheet.write_column('L87', contp)

    # Configurar los datos
    chart_cont.set_title({'name':'¿HAS ESTADO EN CONTACTO CON PACIENTE POSITIVO COVID19?'})
    chart_cont.add_series({
                        'categories': '=Graficas!k87:K89',
                        'values': '=Graficas!$L$87:$L$89',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_cont.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('M87', chart_cont)

    # Datos de contactos sospechosos---------------------------------------------------------------------
    worksheet.write_column('A103', ['Categorio'])
    worksheet.write_column('B103', ['Valor'])
    worksheet.write_column('A104', option)
    worksheet.write_column('B104', sosp)

    # Configurar los datos
    chart_sospec.set_title({'name':'¿HAS ESTADO EN CONTACTO CON PACIENTE SOSPECHOSO COVID19?'})
    chart_sospec.add_series({
                        'categories': '=Graficas!A104:A106',
                        'values': '=Graficas!$B$104:$B$106',
                        'data_labels': {'series_name': False, 'value':True},
                        'name': 'Cantidad',
                        })
    chart_sospec.set_x_axis({'name': "AUTO-REPORTE",
                    'name_font': {'size': 10, 'bold': True},
                    'num_font':  {'italic': True },})

    # Generamos las graficas
    worksheet.insert_chart('C104', chart_sospec)

    workbook.close()
    xlsx_data = output_gf.getvalue()

    return Response(xlsx_data, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Grafica_AutoReporte_Fechas.xlsx"})

# Reporte de Permisos de trabajo
@page.route("/reports/permisos")
@login_required
def rep_permisos():
    # Se captura los datos que vienen por peticion get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    # create a random Pandas dataframe
    datos_permisos = Permisos_salida.query.all()

    # Declaramos la creacion de los archivos y convertilos en binarios
    dpermisos = BytesIO()
    workbook = xlsxwriter.Workbook(dpermisos)
    worksheet = workbook.add_worksheet("Listado")

    col = []
    valores = 2

    # Estraemos la data de la base de datos y la montamos en una lista
    for p in datos_permisos:
        if p.completion_date >= str(inicio) and p.completion_date <= str(fin):
            colabor = [p.email, p.full_name, p.completion_date, p.departure_date, p.departure_time, p.check_in,
                        p.reason_departure, p.place_displacement, p.prior_authorization, p.who_authorized, p.observations]
            col.append(colabor)

    for i in col:
        worksheet.write_column('A1', ['Correo Electrónico'])
        worksheet.write_column('B1', ['Nombre del Colaborador'])
        worksheet.write_column('C1', ['Fecha de diligenciamiento'])
        worksheet.write_column('D1', ['Fecha de la salida o permiso'])
        worksheet.write_column('E1', ['Hora estimada de salida'])
        worksheet.write_column('F1', ['Hora estimada de llegada'])
        worksheet.write_column('G1', ['Motivo de la Salida'])
        worksheet.write_column('H1', ['Nombre del Proveedor o Cliente'])
        worksheet.write_column('I1', ['Cuenta con autorización previa de su jefe inmediato'])
        worksheet.write_column('J1', ['Mencione el nombre de su Jefe Inmediato'])
        worksheet.write_column('K1', ['Observaciones'])

        # Datos de Para generar cada usuario----------------------------------------------------------------
        worksheet.write_column('A{}'.format(int(valores)), [i[0]])
        worksheet.write_column('B{}'.format(int(valores)), [i[1]])
        worksheet.write_column('C{}'.format(int(valores)), [i[2]])
        worksheet.write_column('D{}'.format(int(valores)), [i[3]])
        worksheet.write_column('E{}'.format(int(valores)), [i[4]])
        worksheet.write_column('F{}'.format(int(valores)), [i[5]])
        worksheet.write_column('G{}'.format(int(valores)), [i[6]])
        worksheet.write_column('H{}'.format(int(valores)), [i[7]])
        worksheet.write_column('I{}'.format(int(valores)), [i[8]])
        worksheet.write_column('J{}'.format(int(valores)), [i[9]])
        worksheet.write_column('K{}'.format(int(valores)), [i[10]])
        valores += 1

    # Se encapsula el archivo en excel para ser enviado al navegador
    workbook.close()
    xlsx_temp = dpermisos.getvalue()

    return Response(xlsx_temp, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=reporte_permisos.xlsx"})

# Reporte de Actualizacion de datos
@page.route("/reports/actualizacion")
@login_required
def rep_actualizacion():
    # Se captura los datos que vienen por peticion get
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    # create a random Pandas dataframe
    actualizacion = Actualizacion_datos.query.all()

    # Declaramos la creacion de los archivos y convertilos en binarios
    dactualiza = BytesIO()
    workbook = xlsxwriter.Workbook(dactualiza)
    worksheet = workbook.add_worksheet("Datos")

    col = []
    valores = 2

    # Estraemos la data de la base de datos y la montamos en una lista
    for act in actualizacion:
        if act.date_completion >= str(inicio) and act.date_completion <= str(fin):
            colabor = [act.date_completion, act.full_name, act.stratum, act.home_address,
            act.neighborhood, act.location, act.own_home, act.phone, act.cellular,
            act.city, act.Driving_license, act.motorcycle, act.car, act.category,
            act.own_vehicle, act.type_document, act.identity_document, act.expedition_place,
            act.expedition_date,
            act.military_card, act.district, act.birthdate, act.place_birth, act.sex,
            act.nationality, act.rh, act.position, act.area, act.personal_mail,
            act.date_admission, act.account_number, act.entity, act.Account_type,
            act.eps, act.pension_fund, act.Layoffs, act.arl, act.compensation_box, act.civil_status,
            act.full_name_spouse, act.number_children, act.emer_fullname, act.emer_parentesco,
            act.emer_direction, act.emer_city, act.emer_cellular, act.emer_phone, act.take_medications,
            act.Which_medications, act.Drug_allergy, act.which_allergy, act.major_diseases, act.which_diseases,
            act.Bachelor, act.entity_bachelor, act.technical, act.title_technical, act.technologist,
            act.title_technologist, act.academic, act.title_academic, act.postgraduate, act.title_postgraduate,
            act.others, act.title_others, act.dependents_name1, act.dependents_relationship1,
            act.dependents_birthdate1, act.dependents_age1, act.dependents_educatlevel1, act.dependents_name2,
            act.dependents_relationship2, act.dependents_birthdate2, act.dependents_age2,
            act.dependents_educatlevel2, act.dependents_name3, act.dependents_relationship3,
            act.dependents_birthdate3, act.dependents_age3, act.dependents_educatlevel3]
            col.append(colabor)

    worksheet.write_column('A1', ['Fecha de Diligenciamiento'])
    worksheet.write_column('B1', ['Apellidos y Nombres'])
    worksheet.write_column('C1', ['Estrato'])
    worksheet.write_column('D1', ['Dirección de Domicilio'])
    worksheet.write_column('E1', ['Barrio'])
    worksheet.write_column('F1', ['Localidad'])
    worksheet.write_column('G1', ['Vivienda propia'])
    worksheet.write_column('H1', ['Teléfono'])
    worksheet.write_column('I1', ['Celular'])
    worksheet.write_column('J1', ['Ciudad'])
    worksheet.write_column('K1', ['Licencia de Conducción'])
    worksheet.write_column('L1', ['Moto No'])
    worksheet.write_column('M1', ['Carro No'])
    worksheet.write_column('N1', ['Categoría'])
    worksheet.write_column('O1', ['Vehículo propio'])
    worksheet.write_column('P1', ['Doc. Identidad'])
    worksheet.write_column('Q1', ['No.'])
    worksheet.write_column('R1', ['De'])
    worksheet.write_column('S1', ['Fecha Expedición'])
    worksheet.write_column('T1', ['L.M No.'])
    worksheet.write_column('U1', ['Distrito'])
    worksheet.write_column('V1', ['Fecha de Nacimiento'])
    worksheet.write_column('W1', ['Lugar de Nacimiento'])
    worksheet.write_column('X1', ['Sexo'])
    worksheet.write_column('Y1', ['Nacionalidad '])
    worksheet.write_column('Z1', ['R.H.'])
    worksheet.write_column('AA1', ['Cargo'])
    worksheet.write_column('AB1', ['Área'])
    worksheet.write_column('AC1', ['Correo Personal'])
    worksheet.write_column('AD1', ['Fecha de ingreso'])
    worksheet.write_column('AE1', ['N°. Cuenta'])
    worksheet.write_column('AF1', ['Entidad'])
    worksheet.write_column('AG1', ['Tipo de Cuenta'])
    worksheet.write_column('AH1', ['Eps'])
    worksheet.write_column('AI1', ['Fondo de pensiones'])
    worksheet.write_column('AJ1', ['Cesantías'])
    worksheet.write_column('AK1', ['ARL'])
    worksheet.write_column('AL1', ['Caja de compensación'])
    worksheet.write_column('AM1', ['Estado Civil'])
    worksheet.write_column('AN1', ['nombres  del cónyuge'])
    worksheet.write_column('AO1', ['N° Hijos'])
    worksheet.write_column('AP1', ['Nombres y Apellidos'])
    worksheet.write_column('AQ1', ['Parentesco'])
    worksheet.write_column('AR1', ['Dirección de Domicilio'])
    worksheet.write_column('AS1', ['Ciudad'])
    worksheet.write_column('AT1', ['Celular'])
    worksheet.write_column('AU1', ['Teléfono'])
    worksheet.write_column('AV1', ['Consume medicamentos'])
    worksheet.write_column('AW1', ['Cual'])
    worksheet.write_column('AX1', ['Es alérgico a un medicamento'])
    worksheet.write_column('AY1', ['Cual'])
    worksheet.write_column('AZ1', ['Enfermedades importantes'])
    worksheet.write_column('BA1', ['Cual'])
    worksheet.write_column('BB1', ['Bachillerato'])
    worksheet.write_column('BC1', ['Entidad'])
    worksheet.write_column('BD1', ['Técnico'])
    worksheet.write_column('BE1', ['Titulo obtenido'])
    worksheet.write_column('BF1', ['Tecnológico'])
    worksheet.write_column('BG1', ['Titulo obtenido'])
    worksheet.write_column('BH1', ['Universitario'])
    worksheet.write_column('BI1', ['Titulo obtenido'])
    worksheet.write_column('BJ1', ['Postgrado'])
    worksheet.write_column('BK1', ['Titulo obtenido'])
    worksheet.write_column('BL1', ['Otros'])
    worksheet.write_column('BM1', ['Cuales'])
    worksheet.write_column('BN1', ['Nombre Persona a Cargo 1'])
    worksheet.write_column('BO1', ['Parentesco'])
    worksheet.write_column('BP1', ['Fecha Nacimiento'])
    worksheet.write_column('BQ1', ['Edad'])
    worksheet.write_column('BR1', ['Nivel Educativo'])
    worksheet.write_column('BS1', ['Nombre Persona a Cargo 2'])
    worksheet.write_column('BT1', ['Parentesco'])
    worksheet.write_column('BU1', ['Fecha Nacimiento'])
    worksheet.write_column('BV1', ['Edad'])
    worksheet.write_column('BW1', ['Nivel Educativo'])
    worksheet.write_column('BX1', ['Nombre Persona a Cargo 3'])
    worksheet.write_column('BY1', ['Parentesco'])
    worksheet.write_column('BZ1', ['Fecha Nacimiento'])
    worksheet.write_column('CA1', ['Edad'])
    worksheet.write_column('CB1', ['Nivel Educativo'])

    for i in col:
        # Datos de Para generar cada usuario----------------------------------------------------------------
        worksheet.write_column('A{}'.format(int(valores)), [i[0]])
        worksheet.write_column('B{}'.format(int(valores)), [i[1]])
        worksheet.write_column('C{}'.format(int(valores)), [i[2]])
        worksheet.write_column('D{}'.format(int(valores)), [i[3]])
        worksheet.write_column('E{}'.format(int(valores)), [i[4]])
        worksheet.write_column('F{}'.format(int(valores)), [i[5]])
        worksheet.write_column('G{}'.format(int(valores)), [i[6]])
        worksheet.write_column('H{}'.format(int(valores)), [i[7]])
        worksheet.write_column('I{}'.format(int(valores)), [i[8]])
        worksheet.write_column('J{}'.format(int(valores)), [i[9]])
        worksheet.write_column('K{}'.format(int(valores)), [i[10]])
        worksheet.write_column('L{}'.format(int(valores)), [i[11]])
        worksheet.write_column('M{}'.format(int(valores)), [i[12]])
        worksheet.write_column('N{}'.format(int(valores)), [i[13]])
        worksheet.write_column('O{}'.format(int(valores)), [i[14]])
        worksheet.write_column('P{}'.format(int(valores)), [i[15]])
        worksheet.write_column('Q{}'.format(int(valores)), [i[16]])
        worksheet.write_column('R{}'.format(int(valores)), [i[17]])
        worksheet.write_column('S{}'.format(int(valores)), [i[18]])
        worksheet.write_column('T{}'.format(int(valores)), [i[19]])
        worksheet.write_column('U{}'.format(int(valores)), [i[20]])
        worksheet.write_column('V{}'.format(int(valores)), [i[21]])
        worksheet.write_column('W{}'.format(int(valores)), [i[22]])
        worksheet.write_column('X{}'.format(int(valores)), [i[23]])
        worksheet.write_column('Y{}'.format(int(valores)), [i[24]])
        worksheet.write_column('Z{}'.format(int(valores)), [i[25]])
        worksheet.write_column('AA{}'.format(int(valores)), [i[26]])
        worksheet.write_column('AB{}'.format(int(valores)), [i[27]])
        worksheet.write_column('AC{}'.format(int(valores)), [i[28]])
        worksheet.write_column('AD{}'.format(int(valores)), [i[29]])
        worksheet.write_column('AE{}'.format(int(valores)), [i[30]])
        worksheet.write_column('AF{}'.format(int(valores)), [i[31]])
        worksheet.write_column('AG{}'.format(int(valores)), [i[32]])
        worksheet.write_column('AH{}'.format(int(valores)), [i[33]])
        worksheet.write_column('AI{}'.format(int(valores)), [i[34]])
        worksheet.write_column('AJ{}'.format(int(valores)), [i[35]])
        worksheet.write_column('AK{}'.format(int(valores)), [i[36]])
        worksheet.write_column('AL{}'.format(int(valores)), [i[37]])
        worksheet.write_column('AM{}'.format(int(valores)), [i[38]])
        worksheet.write_column('AN{}'.format(int(valores)), [i[39]])
        worksheet.write_column('AO{}'.format(int(valores)), [i[40]])
        worksheet.write_column('AP{}'.format(int(valores)), [i[41]])
        worksheet.write_column('AQ{}'.format(int(valores)), [i[42]])
        worksheet.write_column('AR{}'.format(int(valores)), [i[43]])
        worksheet.write_column('AS{}'.format(int(valores)), [i[44]])
        worksheet.write_column('AT{}'.format(int(valores)), [i[45]])
        worksheet.write_column('AU{}'.format(int(valores)), [i[46]])
        worksheet.write_column('AV{}'.format(int(valores)), [i[47]])
        worksheet.write_column('AW{}'.format(int(valores)), [i[48]])
        worksheet.write_column('AX{}'.format(int(valores)), [i[49]])
        worksheet.write_column('AY{}'.format(int(valores)), [i[50]])
        worksheet.write_column('AZ{}'.format(int(valores)), [i[51]])
        worksheet.write_column('BA{}'.format(int(valores)), [i[52]])
        worksheet.write_column('BB{}'.format(int(valores)), [i[53]])
        worksheet.write_column('BC{}'.format(int(valores)), [i[54]])
        worksheet.write_column('BD{}'.format(int(valores)), [i[55]])
        worksheet.write_column('BE{}'.format(int(valores)), [i[56]])
        worksheet.write_column('BF{}'.format(int(valores)), [i[57]])
        worksheet.write_column('BG{}'.format(int(valores)), [i[58]])
        worksheet.write_column('BH{}'.format(int(valores)), [i[59]])
        worksheet.write_column('BI{}'.format(int(valores)), [i[60]])
        worksheet.write_column('BJ{}'.format(int(valores)), [i[61]])
        worksheet.write_column('BK{}'.format(int(valores)), [i[62]])
        worksheet.write_column('BL{}'.format(int(valores)), [i[63]])
        worksheet.write_column('BM{}'.format(int(valores)), [i[64]])
        worksheet.write_column('BN{}'.format(int(valores)), [i[65]])
        worksheet.write_column('BO{}'.format(int(valores)), [i[66]])
        worksheet.write_column('BP{}'.format(int(valores)), [i[67]])
        worksheet.write_column('BQ{}'.format(int(valores)), [i[68]])
        worksheet.write_column('BR{}'.format(int(valores)), [i[69]])
        worksheet.write_column('BS{}'.format(int(valores)), [i[70]])
        worksheet.write_column('BT{}'.format(int(valores)), [i[71]])
        worksheet.write_column('BU{}'.format(int(valores)), [i[72]])
        worksheet.write_column('BV{}'.format(int(valores)), [i[73]])
        worksheet.write_column('BW{}'.format(int(valores)), [i[74]])
        worksheet.write_column('BX{}'.format(int(valores)), [i[75]])
        worksheet.write_column('BY{}'.format(int(valores)), [i[76]])
        worksheet.write_column('BZ{}'.format(int(valores)), [i[77]])
        worksheet.write_column('CA{}'.format(int(valores)), [i[78]])
        worksheet.write_column('CB{}'.format(int(valores)), [i[79]])

        valores += 1

    # Se encapsula el archivo en excel para ser enviado al navegador
    workbook.close()
    xlsx_temp = dactualiza.getvalue()

    return Response(xlsx_temp, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Actualización_Datos.xlsx"})

# Generar Certificados Laborales
@page.route("/certificados/laboral", methods=['GET', 'POST'])
def laboral():
    title = 'Certificado Laboral'
    cedula = request.form.get("CED")
    tdirig = str(request.form.get("DIRIG"))
    dirig = tdirig.upper()

    mesesDic = {
        "1":'Enero',
        "2":'Febrero',
        "3":'Marzo',
        "4":'Abril',
        "5":'Mayo',
        "6":'Junio',
        "7":'Julio',
        "8":'Agosto',
        "9":'Septiembre',
        "10":'Octubre',
        "11":'Noviembre',
        "12":'Diciembre'
    }

    fecha = datetime.now().date()
    dia = fecha.day
    now = fecha.month
    mes = mesesDic[str(now)]
    year = fecha.year

    diasDic = {
        "1":'un',
        "2":'dos',
        "3":'tres',
        "4":'cuatro',
        "5":'cinco',
        "6":'seis',
        "7":'siete',
        "8":'ocho',
        "9":'nueve',
        "10":'diez',
        "11":'once',
        "12":'doce',
        "13":"trece",
        "14":"catorce",
        "15":"quince",
        "16":"dieciséis",
        "17":"diecisiete",
        "18":"dieciocho",
        "19":"diecinueve",
        "20":"veinte",
        "21":"veintiun",
        "22":"veintidós",
        "23":"veintitrés",
        "24":"veinticuatro",
        "25":"veinticinco",
        "26":"veintiséis",
        "27":"veintisiete",
        "28":"veintiocho",
        "29":"veintinueve",
        "30":"treinta",
        "31":"treinta y un"
    }
    tdia = diasDic[str(dia)]

    strfecha = "{} de {} de {}".format(dia, mes, year)

    if request.method == 'POST':
        ncert = Colaborador.query.filter_by(number_doc=cedula).first()
        if not ncert == None:
            image = "file:///home/ventaequipossas/Temperatura/app/static/images/logo-ori.png"
            col = ncert
            fec = datetime.strptime(ncert.admission_date, "%Y-%m-%d")
            ing_fech = "{} de {} del {}".format(fec.day, mesesDic[str(fec.month)], fec.year)
            print_html = render_template('cert/certificado.html', img=image, fecha=strfecha,
                                        colab=col, ingr=ing_fech, sr=dirig, dia=tdia,
                                        ndia=dia, mes=mes, year=year)

            options={
                'page-size': 'Letter',
                'margin-top': '15',
                'margin-right': '25',
                'margin-left': '20',
                'margin-bottom': '5',
                'zoom': '1.1',
                'encoding': "UTF-8",
            }

            direct = "./Temperatura/app/certificates"
            url_direct = direct + "/" + cedula
            if not os.path.exists(url_direct):
                os.makedirs(url_direct)

            disp = Display().start() # Generamos una dependecia de venvDisplay

            image = "file:///home/ventaequipossas/Temperatura/app/static/images/logo-ori.png"
            firma = "file:///home/ventaequipossas/Temperatura/app/static/images/firma.png"
            print_html = render_template('cert/certificado.html', img=image, fecha=strfecha,
                                        colab=col, ingr=ing_fech, sr=dirig, dia=tdia,
                                        ndia=dia, mes=mes, year=year, firma=firma)

            #disp = Display().start() # Generamos una dependecia de venvDisplay
            # Convertimos el html a nuestro pdf sin guardarlo en el servidor ,configuration=PDFKIT_CONFIGURATION
            pdfkit.from_string(print_html, url_direct+"/certificado.pdf", options=options)#, configuration=PDFKIT_CONFIGURATION)
            #pdf = pdfkit.from_string(print_html, False, options=options)#, configuration=PDFKIT_CONFIGURATION)
            #response = make_response(pdf)
            #response.headers["Content-Type"] = "application/pdf"
            #response.headers["Content-Disposition"] = "inline; filename=output.pdf"
            #return response
            disp.stop()     # Cerramos la conexion del pdf

            url = os.path.abspath(url_direct+"/certificado.pdf")
            f = datetime.now().date()
            now = datetime.strftime(f, "%d/%m/%Y")
            # Enviar correo electronico
            msg = Message('Certificados Laborales',
                        sender=current_app.config['DONT_REPLY_FROM_EMAIL'],
                        recipients=[col.email])
            msg.body = "Correo Informativo Venta Equipos SAS"
            msg.html = f'''<p>Apreciado usuario(a): <strong>{col.full_name}</strong>.<br><br>
                        Nos permitimos informar que se acaba de generar
                        el Certificado Laboral Solicitado el Dia {now}, en nuestro modulo Certificados.<br>
                        Le recordamos que esta dirección de correo es utilizada solamente para envíos de correos automáticos.<br>
                        Por favor no responda este correo, ya que no podrá ser atendido.<br>
                        Si desea contactarse con nosotros, envíe un correo o comuníquese telefónicamente con Talento Humano
                        de <strong>VENTA EQUIPOS SAS</strong><br><br>Cordial saludo.</p>'''
            with current_app.open_resource(str(url)) as fp:
                msg.attach("Certificado_Laboral.pdf", "file/pdf", fp.read())
            mail.send(msg)

            flash(CERTIF_ENV)
            return redirect(url_for(".index"))

        else:
            flash("Usuario No se encuentra Regitrado Por favor validar con Gestion Humana", "error")

    return render_template('views/colaborador/cert_laboral.html', title = title)