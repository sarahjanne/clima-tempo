import requests

from fastapi import APIRouter, status
from schemas.clima import EnderecoClimaResponse
from fastapi import HTTPException

router = APIRouter(prefix="/clima", tags=["Clima"])

@router.get("/{cep}", response_model=EnderecoClimaResponse, summary="Consultar o clima por CEP")
def consultar_endereco(cep: str):

    resposta = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}")   

    if resposta.status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CEP inválido. Envie 8 dígitos numéricos.")   
    elif resposta.status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CEP não localizado na BrasilAPI")
    elif resposta.status_code == 500:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao consultar serviços externos")

    dados = resposta.json()
    return dados
