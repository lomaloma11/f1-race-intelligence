from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from src.api.routes.predictions import predictions_bp 
from src.api.routes.analytics import analytics_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuração do Swagger
    app.config['SWAGGER'] = {
        'title': 'F1 Race Intelligence API',
        'uiversion': 3,
        'description': 'API para predições e análises de corrida da Fórmula 1'
    }
    Swagger(app)

    # Registro das rotas
    app.register_blueprint(predictions_bp, url_prefix='/api/v1/predictions')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"status": "online", "message": "API rodando!"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)