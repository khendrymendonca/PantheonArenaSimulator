from flask import Flask, render_template
from flask_socketio import SocketIO

# Inicializa o SocketIO sem app vinculado ainda
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave_secreta_super_segura'
    
    # Vincula o app ao SocketIO e permite CORS para facilitar desenvolvimento
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Importa os eventos de socket
    # Importante: Importar aqui dentro para garantir que o socketio já esteja inicializado
    from . import events
    
    @app.route('/')
    def index():
        return render_template('index.html')

    return app
