from datetime import date
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


class PrevisaoDia(BaseModel):
    data: str
    dia: str
    codigo_tempo: int
    descricao: str
    icone: str
    temperatura_min: float
    temperatura_max: float


def normalizar_previsao_diaria(dados: dict[str, Any]) -> list[dict[str, Any]]:
    diaria = dados.get("daily", {})
    datas = diaria.get("time", [])
    codigos = diaria.get("weather_code", [])
    temperaturas_minimas = diaria.get("temperature_2m_min", [])
    temperaturas_maximas = diaria.get("temperature_2m_max", [])
    dias_semana = (
        "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo",
    )
    previsao = []

    for indice, data_texto in enumerate(datas):
        data_previsao = date.fromisoformat(data_texto)
        dias_ate_previsao = (data_previsao - date.today()).days
        if dias_ate_previsao == 0:
            nome_dia = "Hoje"
        elif dias_ate_previsao == 1:
            nome_dia = "Amanhã"
        else:
            nome_dia = dias_semana[data_previsao.weekday()].capitalize()

        codigo = int(codigos[indice]) if indice < len(codigos) else -1
        icone, descricao = _condicao_meteorologica(codigo)
        temperatura_minima = (
            temperaturas_minimas[indice] if indice < len(temperaturas_minimas) else 0
        )
        temperatura_maxima = (
            temperaturas_maximas[indice] if indice < len(temperaturas_maximas) else 0
        )
        previsao.append(
            {
                "data": data_texto,
                "dia": nome_dia,
                "codigo_tempo": codigo,
                "descricao": descricao,
                "icone": icone,
                "temperatura_min": float(temperatura_minima),
                "temperatura_max": float(temperatura_maxima),
            }
        )

    return previsao


def _condicao_meteorologica(codigo: int) -> tuple[str, str]:
    condicoes = {
        0: ("☀️", "Ensolarado"),
        1: ("🌤️", "Predominantemente limpo"),
        2: ("⛅", "Parcialmente nublado"),
        3: ("☁️", "Nublado"),
        45: ("🌫️", "Neblina"),
        48: ("🌫️", "Neblina"),
        51: ("🌦️", "Chuvisco"),
        53: ("🌦️", "Chuvisco"),
        55: ("🌧️", "Chuvisco intenso"),
        56: ("🌧️", "Chuvisco congelante"),
        57: ("🌧️", "Chuvisco congelante"),
        61: ("🌧️", "Chuva fraca"),
        63: ("🌧️", "Chuva"),
        65: ("🌧️", "Chuva intensa"),
        66: ("🌧️", "Chuva congelante"),
        67: ("🌧️", "Chuva congelante"),
        71: ("🌨️", "Neve fraca"),
        73: ("🌨️", "Neve"),
        75: ("🌨️", "Neve intensa"),
        77: ("🌨️", "Grãos de neve"),
        80: ("🌦️", "Pancadas de chuva"),
        81: ("🌧️", "Pancadas de chuva"),
        82: ("🌧️", "Pancadas de chuva intensas"),
        85: ("🌨️", "Pancadas de neve"),
        86: ("🌨️", "Pancadas de neve intensas"),
        95: ("⛈️", "Trovoadas"),
        96: ("⛈️", "Trovoadas com granizo"),
        99: ("⛈️", "Trovoadas com granizo"),
    }
    return condicoes.get(codigo, ("☁️", "Condição variável"))

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
    previsao: list[PrevisaoDia] = Field(default_factory=list)

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
                "previsao": normalizar_previsao_diaria(dados),
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
                "previsao": normalizar_previsao_diaria(dados),
            }
        return dados

class EnderecoClimaResponse(BaseModel):
    endereco: EnderecoResponse
    clima: ClimaResponse
