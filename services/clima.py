from datetime import date

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
    coordenadas = dados_cep["location"]["coordinates"]
    latitude = float(coordenadas["latitude"])
    longitude = float(coordenadas["longitude"])

    url_clima = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
    )

    if data_previsao:
        url_clima += (
            f"&start_date={data_previsao}&end_date={data_previsao}"
            "&daily=temperature_2m_max,wind_speed_10m_max&timezone=auto"
        )
    else:
        url_clima += "&current_weather=true"

    resposta_clima = requests.get(url_clima)

    if resposta_clima.status_code != 200:
        raise ClimaServicoIndisponivelError

    return {
        "endereco": dados_cep,
        "clima": resposta_clima.json(),
    }