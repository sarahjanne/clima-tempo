from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BeforeValidator
from schemas.clima import EnderecoClimaResponse
from services.clima import (CepInvalidoError, CepNaoEncontradoError, CepServicoIndisponivelError, ClimaServicoIndisponivelError,consultar_clima_por_cep)

router = APIRouter(prefix="/clima", tags=["Clima"])

templates = Jinja2Templates(directory="templates")


def normalizar_data_vazia(valor: object) -> object:
    return None if valor == "" else valor


@router.get("/pagina", summary="Buscar clima por CEP em uma página HTML")
def pagina_busca_clima(
    request: Request,
    cep: Optional[str] = Query(None, description="CEP com ou sem hífen"),
    data_previsao: Annotated[
        Optional[date],
        BeforeValidator(normalizar_data_vazia),
        Query(description="Data da previsão climática no formato AAAA-MM-DD"),
    ] = None,
):
    if cep:
        cep_limpo = cep.replace("-", "")
        url = f"/clima/pagina/{cep_limpo}"
        if data_previsao:
            url += f"?data_previsao={data_previsao.isoformat()}"
        return RedirectResponse(
            url=url, status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        request=request,
        name="clima.html",
        context={"request": request},
    )

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


@router.get("/pagina/{cep}", summary="Visualizar o clima em uma página HTML")
def visualizar_clima_pagina(
    request: Request,
    cep: str,
    data_previsao: Annotated[
        Optional[date],
        BeforeValidator(normalizar_data_vazia),
        Query(description="Data da previsão climática no formato AAAA-MM-DD"),
    ] = None,
):
    try:
        dados = consultar_clima_por_cep(cep, data_previsao)
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

    resposta = EnderecoClimaResponse.model_validate(dados)
    data_formatada = (
        date.fromisoformat(resposta.clima.data).strftime("%d/%m/%Y")
        if resposta.clima.data
        else ""
    )
    return templates.TemplateResponse(
        request=request,
        name="clima.html",
        context={
            "request": request,
            "endereco": resposta.endereco,
            "clima": resposta.clima,
            "data_previsao": data_previsao.isoformat() if data_previsao else "",
            "data_formatada": data_formatada,
        },
    )

         
    
       

