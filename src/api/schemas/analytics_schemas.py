from pydantic import BaseModel, Field, field_validator


class DriverClusterInput(BaseModel):
    avg_lap_time: float = Field(
        ...,
        ge=50.0,
        le=200.0,
        description="Tempo médio por volta em segundos (50.0 a 200.0)"
    )
    std_lap_time: float = Field(
        ...,
        ge=0.0,
        le=20.0,
        description="Desvio padrão do tempo por volta em segundos (0.0 a 20.0)"
    )

    @field_validator('avg_lap_time')
    def validate_avg_lap_time(cls, v):
        if not (50.0 <= v <= 200.0):
            raise ValueError('O tempo médio por volta deve estar entre 50.0 e 200.0 segundos.')
        return v

    @field_validator('std_lap_time')
    def validate_std_lap_time(cls, v):
        if not (0.0 <= v <= 20.0):
            raise ValueError('O desvio padrão do tempo por volta deve estar entre 0.0 e 20.0 segundos.')
        return v


class TireCompoundInput(BaseModel):
    compound: str = Field(..., description="Composto de pneu (SOFT ou HARD)")

    @field_validator('compound')
    def validate_compound(cls, v):
        if not isinstance(v, str):
            raise ValueError('O composto de pneu deve ser uma string.')

        normalized = v.strip().upper()
        if normalized not in ('SOFT', 'HARD'):
            raise ValueError('Composto de pneu não suportado. Os compostos suportados são: SOFT e HARD.')
        return normalized
