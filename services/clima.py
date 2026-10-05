from datetime import date, timedelta

import requests


class CepInvalidoError(Exception):
    pass

class CepNaoEncontradoError(Exception):
    pass

class CepServicoIndisponivelError(Exception):
    pass

class ClimaServicoIndisponivelError(Exception):
    pass


def consultar_clima_por_cep(cep: str, data_previsao: date | None) -> dict:
    resposta_cep = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}")

    if resposta_cep.status_code == 400:
        raise CepInvalidoError
    if resposta_cep.status_code == 404:
        raise CepNaoEncontradoError
    if resposta_cep.status_code == 500:
        raise CepServicoIndisponivelError

    dados_cep = resposta_cep.json()
    lat = float(dados_cep["location"]["coordinates"]["latitude"])
    lng = float(dados_cep["location"]["coordinates"]["longitude"])

    url_clima = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}")
    parametros_diarios = (
        "daily=weather_code,temperature_2m_min,temperature_2m_max,"
        "wind_speed_10m_max&timezone=auto"
    )

    if data_previsao:
        data_final = data_previsao + timedelta(days=2)
        url_clima += (
            f"&start_date={data_previsao}&end_date={data_final}&{parametros_diarios}"
        )
    else:
        url_clima += f"&current_weather=true&forecast_days=3&{parametros_diarios}"

    resposta_clima = requests.get(url_clima)

    if resposta_clima.status_code != 200:
        raise ClimaServicoIndisponivelError

    clima = resposta_clima.json()
    if data_previsao:
        clima["data"] = data_previsao.isoformat()
    else:
        clima["data"] = date.today().isoformat()

    return {
        "endereco": dados_cep,
        "clima": clima,
    }