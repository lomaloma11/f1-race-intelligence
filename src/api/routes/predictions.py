from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from src.api.services.prediction_service import PredictionService
from src.api.schemas.prediction_schema import Top10PredictionInput

predictions_bp = Blueprint('predictions', __name__)
prediction_service = PredictionService()

@predictions_bp.route('/top10', methods=['POST'])
def predict_top10():
    """
    Prevê a probabilidade de um piloto terminar no Top 10.
    ---
    tags:
      - Predições
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - grid_position
            - avg_lap_time
            - std_lap_time
          properties:
            grid_position:
              type: integer
              example: 4
              description: Posição no grid de largada (1 a 20)
            avg_lap_time:
              type: number
              example: 76.5
              description: Tempo médio de volta em segundos
            std_lap_time:
              type: number
              example: 0.8
              description: Desvio padrão do tempo de volta (consistência)
            positions_gained:
              type: integer
              example: 1
              description: Posições ganhas ou perdidas
            is_rainy:
              type: integer
              example: 0
              description: 1 para pista molhada, 0 para pista seca
    responses:
      200:
        description: Predição realizada com sucesso
      400:
        description: Dados de entrada inválidos
      500:
        description: Erro interno no servidor
    """
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Nenhum dado fornecido."}), 400
    try:
        # Tenta validar o JSON usando o contrato da classe Top10PredictionInput
        validated_data = Top10PredictionInput(**data)
    except ValidationError as e:
        # Se os dados forem inválidos, devolve o erro 400 amigável sem derrubar o Python
        return jsonify({
            "status": "error",
            "message": "Dados de entrada inválidos",
            "errors": e.errors()
        }), 400

    try:
        # Se passou na validação, envia o dicionário limpo para a IA
        resultado = prediction_service.predict_top10(validated_data.model_dump())
        return jsonify({
            "status": "success",
            "data": resultado
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500