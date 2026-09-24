import requests

from datetime import date
from typing import Optional
from fastapi import APIRouter, status
from schemas.clima import EnderecoClimaResponse
from fastapi import HTTPException, Query

router = APIRouter(prefix="/clima", tags=["Clima"])

@router.get("/{cep}", response_model=EnderecoClimaResponse, summary="Consultar o clima por CEP")
def consultar_endereco(cep: str, 
                       data_previsao: Optional[date] = Query(None, description="Data da previsão climática no formato AAAA-MM-DD")
                       ):

    resposta_cep = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}")   

    if resposta_cep.status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CEP inválido. Envie 8 dígitos numéricos.")   
    elif resposta_cep.status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CEP não localizado na BrasilAPI")
    elif resposta_cep.status_code == 500:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao consultar serviços externos")
    
    dados_cep = resposta_cep.json()

    lat = float(dados_cep["location"]["coordinates"]["latitude"])
    lng = float(dados_cep["location"]["coordinates"]["longitude"])

    url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}"

    if data_previsao:
        url_clima += f"&start_date={data_previsao}&end_date={data_previsao}&daily=temperature_2m_max,wind_speed_10m_max&timezone=auto"
    else:
        url_clima += "&current_weather=true"

    resposta_clima = requests.get(url_clima)

    if resposta_clima.status_code != 200:
            raise HTTPException(status_code=502, detail="Falha ao consultar o clima.")

    dados_clima = resposta_clima.json()

    return {
        "endereco": dados_cep,
        "clima": dados_clima
    }

         
    
       

