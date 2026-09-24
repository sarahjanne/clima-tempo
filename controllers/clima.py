from datetime import date
from typing import Optional
from fastapi import APIRouter, status
from schemas.clima import EnderecoClimaResponse
from fastapi import HTTPException, Query
from services.clima import (CepInvalidoError, CepNaoEncontradoError, CepServicoIndisponivelError, ClimaServicoIndisponivelError,consultar_clima_por_cep)

router = APIRouter(prefix="/clima", tags=["Clima"])

@router.get("/{cep}", response_model=EnderecoClimaResponse, summary="Consultar o clima por CEP")
def consultar_endereco(cep: str, 
                       data_previsao: Optional[date] = Query(None, description="Data da previsão climática no formato AAAA-MM-DD")
                       ):
    try:
        return consultar_clima_por_cep(cep, data_previsao)
    except CepInvalidoError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CEP inválido. Envie 8 dígitos numéricos.",
        )
    except CepNaoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CEP não localizado na BrasilAPI",
        )
    except CepServicoIndisponivelError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao consultar serviços externos",
        )
    except ClimaServicoIndisponivelError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao consultar o clima.",
        )

         
    
       

