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
    data: str | None = None
    temperatura: float
    unidade_temperatura: str
    velocidade_vento: float
    unidade_velocidade_vento: str
    dia_noite: str

    @model_validator(mode="before")
    @classmethod
    def adaptar_dados_meteo(cls, dados: Any) -> Any:
        if not isinstance(dados, dict):
            return dados

        if "current_weather" in dados:
            current_weather_units = dados.get("current_weather_units", {})
            current_weather = dados.get("current_weather", {})
            data_valor = dados.get("data")

            return {
                "data": data_valor,
                "temperatura": float(current_weather.get("temperature", 0.0)),
                "unidade_temperatura": current_weather_units.get("temperature", "C"),
                "velocidade_vento": float(current_weather.get("windspeed", 0.0)),
                "unidade_velocidade_vento": current_weather_units.get("windspeed"),
                "dia_noite": str("Dia" if current_weather.get("is_day") == 1 else "Noite"),
            }
        elif "daily" in dados:
            daily = dados.get("daily", {})
            daily_units = dados.get("daily_units", {})
            lista_temperatura = daily.get("temperature_2m_max", [0.0])
            lista_vento = daily.get("wind_speed_10m_max", [0.0])
            lista_data = daily.get("time", [])

            return {
                "data": dados.get("data") or (lista_data[0] if lista_data else None),
                "temperatura": float(lista_temperatura[0] if lista_temperatura else 0.0),
                "unidade_temperatura": daily_units.get("temperature_2m_max", "C"),
                "velocidade_vento": float(lista_vento[0] if lista_vento else 0.0),
                "unidade_velocidade_vento": daily_units.get("wind_speed_10m_max", "km/h"),
                "dia_noite": "dia todo",
            }
        return dados

class EnderecoClimaResponse(BaseModel):
    endereco: EnderecoResponse
    clima: ClimaResponse
