import json
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from src.api.services.analytics_service import AnalyticsService
from src.api.schemas.analytics_schemas import (
    DriverClusterInput,
    TireCompoundInput,
)

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

# 🛞 Rota 1: Pneus 
@analytics_bp.route('/tires/<compound>', methods=['GET'])
def get_tires(compound):
    """
    Retorna a análise de degradação e ritmo por composto de pneu.
    ---
    tags:
      - Analytics 
    summary: Análise de Desempenho dos Compostos de Pneu
    description: Retorna métricas agregadas de degradação e tempo por volta para pneus Soft e Hard.
    responses:
      200:
        description: Dados de analytics dos pneus recuperados com sucesso
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  compound:
                    type: string
                    example: SOFT
                  avg_lap_time:
                    type: number
                    example: 77.2
                  degradation_rate:
                    type: number
                    example: 0.08
      400:
        description: Composto de pneu inválido
      500:
        description: Erro ao processar dados de analytics
    """
    try:
        validated_input = TireCompoundInput(compound=compound)
        resultado = analytics_service.get_tire_degradation(validated_input.compound)
        return jsonify({"status": "success", "data": resultado}), 200
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Composto de pneu inválido ou não suportado. Compostos suportados: SOFT e HARD.",
            "errors": json.loads(e.json())
        }), 400
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "errors": [{"msg": str(e)}]
        }), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota 2: Clusterização
@analytics_bp.route('/drivers/cluster', methods=['POST'])
def predict_cluster():
    """
    Retorna o agrupamento (Clustering/K-Means) dos perfis de pilotagem.
    ---
    tags:
      - Analytics
    summary: Perfis de Pilotagem (K-Means)
    description: Exibe em qual cluster cada piloto se enquadra (ex. Agressivo, Consistente, Conservador).
    parameters:
      - name: body
        in: body
        required: true
        description: Métricas do piloto para classificação de perfil.
        schema:
          type: object
          required:
            - avg_lap_time
            - std_lap_time
          properties:
            avg_lap_time:
              type: number
              example: 76.5
              description: Tempo médio de volta em segundos
            std_lap_time:
              type: number
              example: 0.8
              description: Desvio padrão do tempo de volta (consistência)
    responses:
      200:
        description: Cluster e perfil do piloto
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                avg_lap_time:
                  type: number
                  example: 76.5
                std_lap_time:
                  type: number
                  example: 0.8
                assigned_cluster:
                  type: integer
                  example: 0
      400:
        description: Dados de entrada inválidos
      500:
        description: Erro interno no servidor
    """
    data = request.get_json(silent=True)
    
    try:
        if data is None or not isinstance(data, dict):
            # Provoca erro Pydantic com payload vazio se não for dict
            validated_data = DriverClusterInput(**{})
        else:
            validated_data = DriverClusterInput(**data)
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Dados de entrada inválidos",
            "errors": json.loads(e.json())
        }), 400

    try:
        resultado = analytics_service.predict_cluster(
            avg_lap_time=validated_data.avg_lap_time,
            std_lap_time=validated_data.std_lap_time
        )
        return jsonify({"status": "success", "data": resultado}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
