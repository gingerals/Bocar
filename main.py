from flask import Flask, request, render_template, redirect, url_for
import jinja2
import database
from session import Session 
from report import getDailyReport


# Set up Jinja2 template engine
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

session = Session()

# Define the Flask application
app = Flask(__name__)
app.secret_key = 'bocarkey'
app.config['USERS'] = {'admin': '123bocar'}


@app.route('/')
def home():
    user = request.args.get('user')
    state = request.args.get('state')
    authenticated = session.is_authenticated
    return render_template('home.html', user=user, state=state, authenticated=authenticated) 

@app.route('/dispositivos/<device>')
@app.route('/dispositivos')
def dispositivos(device=None):
    if not session.is_authenticated:
        return redirect(url_for('login'))
    else:
        devices, results = database.db(device)
        active_device = device

        for device in devices:
            for row in results:
                playerID = row[1]
            break
        daily_report= getDailyReport(playerID)
        

        return render_template('dispositivos.html', devices=devices, results=results, active_device=active_device, authenticated=session.is_authenticated, playerID=playerID, daily_report=daily_report)
    
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if app.config['USERS'].get(username) != password:
            error = 'Usuario o contraseña incorrectos'
        else:
            session.print_session()

            session.login(username)
            return redirect(url_for('home'))
    return render_template('auth.html', error=error, authenticated= session.is_authenticated)

@app.route('/logout')
def logout():
    session.logout()
    return redirect(url_for('home'))

@app.context_processor
def inject_session():
    return dict(session=session)


# Start the Flask server
if __name__ == '__main__':
    app.run()
