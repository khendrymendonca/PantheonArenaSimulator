import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando Pantheon Arena Server na porta {port}...")
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
