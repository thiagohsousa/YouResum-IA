from flask import Flask
from dotenv import load_dotenv
from routes.main_routes import main_bp

load_dotenv()

app = Flask(__name__)

# Registra o módulo de rotas na aplicação
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)