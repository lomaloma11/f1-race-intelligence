from pydantic import BaseModel, Field, field_validator


class Top10PredictionInput(BaseModel):
    # Valida que grid_position é um número inteiro entre 1 e 20
    grid_position: int = Field(
        ..., ge=1, le=20, description="Posição de largada no grid (1 a 20)"
    )

    # Valida que o tempo médio é um número flutuante positivo em um intervalo realista de F1
    avg_lap_time: float = Field(
        ..., ge=50.0, le=200.0, description="Tempo médio por volta em segundos"
    )

    # Valida o desvio padrão (consistência)
    std_lap_time: float = Field(
        ..., ge=0.0, le=20.0, description="Consistência/Desvio padrão em segundos"
    )

    # Valida posições ganhas/perdidas (entre -20 e 20)
    positions_gained: int = Field(
        0, ge=-20, le=20, description="Posições ganhas/perdidas em relação ao grid"
    )

    # Aceita apenas 0 (sem chuva) ou 1 (com chuva)
    is_rainy: int = Field(
        0, ge=0, le=1, description="1 se choveu na sessão, 0 se foi pista seca"
    )

    @field_validator("grid_position")
    def validate_grid(cls, v):
        if not (1 <= v <= 20):
            raise ValueError("A posição do grid na F1 deve ser entre 1 e 20.")
        return v
