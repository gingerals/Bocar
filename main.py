from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import jinja2
import database
from session import Session
from report import getDailyReportURL
from videos import getDailyReportTable

# Configuración del motor de plantillas Jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

# Crear objeto sesión
session = Session()

# Crear aplicación Flask
app = Flask(__name__)

# Clave secreta de la aplicación
app.secret_key = 'bocarkey'

# Configuración de usuarios autorizados
app.config['USERS'] = {'admin': '123bocar'}

# Ruta de la página principal


@app.route('/')
def home():
    # Obtener el usuario y estado de la URL
    user = request.args.get('user')
    state = request.args.get('state')
    # Verificar si el usuario está autenticado
    authenticated = session.is_authenticated
    # Renderizar la plantilla home.html
    return render_template('home.html', user=user, state=state, authenticated=authenticated)

# Rutas de dispositivos


@app.route('/dispositivos/<device>')
@app.route('/dispositivos')
def dispositivos(device=None):
    # Verificar si el usuario está autenticado
    if not session.is_authenticated:
        return redirect(url_for('login'))
    else:
        # Obtener los dispositivos y resultados de la base de datos
        devices, results = database.getSS(device)
        # Establecer el dispositivo activo
        active_device = device

        # Obtener el playerID para generar el reporte diario
        for device in devices:
            for row in results:
                playerID = row[1]
            break
        # Obtener la URL del reporte diario y la tabla de resultados
        url_report = getDailyReportURL(playerID)
        report_table = getDailyReportTable(url_report)

        if report_table is not None:
            # se agrupan los datos
            grouped_data = report_table.groupby('File Name')
            print(grouped_data)
        else:
            grouped_data = ""

        # Se obtienen los tokens de cada video
        video_tokens = {}


        for filename, file_data in grouped_data:
            videos = database.getVideos(filename)
            if videos:
                video_tokens[filename] = videos[0][1]
            else:
                video_tokens[filename] = "No disponible"

        # Ignoramos algunos de los dispositivos
        ignorar = ['DERECHO', 'IZQUIERDO', 'BCR']


        # Mapeo de los nombres de dispositivos a cambiar
        renombrar = {
            'SAN LUIS RECLUTAMIENTO': 'San Luis Potosí',
            'SLP COMEDOR': 'SLP Comedor',
            'CENTRO DE INGENIERIA': 'C.D.I. BOCAR',
            'QUERETARO': 'AUMA Tec',
            'FUGRA-LERMA': 'Lerma | Fugra',
            'PLASTITEC-LERMA': ' Lerma | Plastic Tec',
            'PRESION-LERMA': ' Lerma | Presión',
            'COYOACAN': 'Coyoacán',
            'PERISUR-IZQUIERDO': 'Perisur | IZQ',
            'PERISUR-DERECHO': 'Perisur | DER',
            'SALTILLO': 'Saltillo | 1',
            'SALTILLO DOS': 'Saltillo | 2'
        }


        # Renderizar la plantilla dispositivos.html
        return render_template('dispositivos.html', devices=devices, results=results, active_device=active_device, authenticated=session.is_authenticated, playerID=playerID, report_table=grouped_data, video_tokens=video_tokens, ignorar=ignorar, renombrar=renombrar)

# Ruta de inicio de sesión


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Obtener el nombre de usuario y la contraseña ingresados
        username = request.form.get('username')
        password = request.form.get('password')
        # Verificar si el usuario y la contraseña son correctos
        if app.config['USERS'].get(username) != password:
            error = 'Usuario o contraseña incorrectos'
        else:
            # Iniciar sesión y redirigir a la página principal
            session.login(username)
            return redirect(url_for('home'))
    # Renderizar la plantilla auth.html
    return render_template('auth.html', error=error, authenticated=session.is_authenticated)

# Ruta de cierre de sesión


@app.route('/logout')
def logout():
    # Cerrar sesión y redirigir a la página principal
    session.logout()
    return redirect(url_for('home'))

# Función que inyecta el objeto sesión en las plantillas


@app.context_processor
def inject_session():
    return dict(session=session)


# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run()
