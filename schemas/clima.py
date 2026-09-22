from typing import Any
from pydantic import BaseModel, Field, model_validator


class Endereco(BaseModel):
    logradouro: str
    bairro: str
    cidade: str
    estado: str

class Coordenadas(BaseModel):
    latitude: float
    longitude: float

class EnderecoResponse(BaseModel):
    cep: str = Field(..., pattern=r"^\d{5}-?\d{3}$")
    endereco: Endereco
    coordenadas: Coordenadas

    @model_validator(mode="before")
    @classmethod
    def adaptar_dados_brasilapi(cls, dados: Any) -> Any:
        if isinstance(dados, dict) and "street" in dados:
            location = dados.get("location", {})
            coordinates = location.get("coordinates", {})

            return {
                "cep": dados["cep"],
                "endereco": {
                    "logradouro": dados.get("street"),
                    "bairro": dados.get("neighborhood"),
                    "cidade": dados.get("city"),
                    "estado": dados.get("state"),
                },
                "coordenadas": {
                    "latitude": float(coordinates.get("latitude", 0.0)),
                    "longitude": float(coordinates.get("longitude", 0.0)),
                }
            }     
        return dados

class ClimaResponse(BaseModel):
    temperatura: float
    unidade_temperatura: str
    velocidade_vento: float
    codigo_condicao: int

    @model_validator(mode="before")
    @classmethod
    def adaptar_dados_meteo(cls, dados: Any) -> Any:
        if isinstance(dados, dict) and "current_weather" in dados:
            current_weather_units = dados.get("current_weather_units", {})
            current_weather = dados.get("current_weather", {})

            return {
                "clima": dados["clima"],
                "temperatura": float(current_weather.get("temperature", 0.0)),
                "unidade_temperatura": current_weather_units.get("temperature", "C"),
                "velocidade_vento": float(current_weather.get("windspeed", 0.0)),
                "codigo_condicao": int(current_weather.get("weathercode", 0)),
                }
        return dados

class EnderecoClimaResponse(BaseModel):
    endereco: EnderecoResponse
    clima: ClimaResponse
