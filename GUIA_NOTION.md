# ChoveAí: explicação completa do projeto

Este documento explica o estado atual do projeto `clima-tempo`. Ele pode ser importado no Notion como arquivo Markdown.

## 1. O que a aplicação faz

A aplicação é uma API criada com FastAPI que:

1. Recebe um CEP.
2. Consulta o endereço na BrasilAPI.
3. Extrai latitude e longitude do endereço.
4. Consulta o clima na Open-Meteo.
5. Permite informar uma data específica por meio do parâmetro `data_previsao`.
6. Adapta as respostas externas para um formato próprio usando Pydantic.
7. Retorna endereço e clima em uma resposta padronizada.

## 2. Organização do projeto

```text
clima-tempo/
├── main.py
├── pyproject.toml
├── controllers/
│   └── clima.py
├── services/
│   ├── __init__.py
│   └── clima.py
├── schemas/
│   └── clima.py
└── .vscode/
    └── settings.json
```

### Responsabilidade de cada camada

- `main.py`: cria a aplicação FastAPI e registra as rotas.
- `controllers/`: define os endpoints e traduz erros da aplicação para respostas HTTP.
- `services/`: concentra as regras de negócio e as chamadas para APIs externas.
- `schemas/`: define, valida e adapta os formatos dos dados.
- `pyproject.toml`: configura o projeto e suas dependências.
- `.vscode/settings.json`: define o gerenciador de ambiente e pacotes usado pelo VS Code.

## 3. Fluxo completo de uma requisição

Uma chamada como esta:

```text
GET /clima/01001000?data_previsao=2026-09-24
```

segue este caminho:

1. O FastAPI recebe a requisição em `controllers/clima.py`.
2. `cep` é lido como parâmetro da URL.
3. `data_previsao` é lida como parâmetro opcional da query.
4. FastAPI converte `data_previsao` de texto para `datetime.date`.
5. O controller chama `consultar_clima_por_cep`.
6. O service consulta a BrasilAPI.
7. O service extrai latitude e longitude.
8. O service monta a URL da Open-Meteo.
9. Se houver data, usa `start_date` e `end_date`.
10. Se não houver data, solicita o clima atual.
11. O service retorna um dicionário com `endereco` e `clima`.
12. O `response_model` valida e adapta os dados usando `EnderecoClimaResponse`.
13. O FastAPI devolve o JSON final.

## 4. Arquivo `main.py`

Código atual:

```python
from fastapi import FastAPI

from controllers.clima import router as clima_router

app = FastAPI(
    title="ChoveAí",
    description="API de Previsão do Tempo por CEP")


app.include_router(clima_router)
```

### Explicação linha por linha

- **Linha 1 — `from fastapi import FastAPI`**
  - Importa a classe `FastAPI` da biblioteca FastAPI.
  - Essa classe é usada para criar o objeto principal da aplicação.

- **Linha 2 — linha em branco**
  - Apenas separa visualmente os imports.

- **Linha 3 — `from controllers.clima import router as clima_router`**
  - Importa o objeto `router` criado em `controllers/clima.py`.
  - `as clima_router` cria um nome mais descritivo para esse objeto dentro de `main.py`.

- **Linha 4 — linha em branco**
  - Separa os imports da criação da aplicação.

- **Linha 5 — `app = FastAPI(`**
  - Cria a aplicação FastAPI.
  - O objeto criado é armazenado na variável `app`.
  - O Uvicorn usará essa variável para iniciar o servidor.

- **Linha 6 — `title="ChoveAí",`**
  - Define o título da API.
  - Esse título aparece na documentação interativa em `/docs`.

- **Linha 7 — `description="API de Previsão do Tempo por CEP")`**
  - Define a descrição exibida na documentação.
  - O parêntese fecha a criação do objeto `FastAPI`.

- **Linhas 8 e 9 — linhas em branco**
  - Melhoram a leitura e não executam nenhuma ação.

- **Linha 10 — `app.include_router(clima_router)`**
  - Registra no objeto principal todas as rotas definidas em `clima_router`.
  - Sem essa linha, o endpoint de clima não faria parte da aplicação.

## 5. Arquivo `controllers/clima.py`

Código atual:

```python
from datetime import date
from typing import Optional
from fastapi import APIRouter, status
from schemas.clima import EnderecoClimaResponse
from fastapi import HTTPException, Query
from services.clima import (CepInvalidoError, CepNaoEncontradoError, 
                            CepServicoIndisponivelError, ClimaServicoIndisponivelError,
                            consultar_clima_por_cep)

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
```

### Explicação linha por linha

- **Linha 1 — `from datetime import date`**
  - Importa o tipo `date` da biblioteca padrão do Python.
  - Ele representa uma data sem horário, como `2026-09-24`.

- **Linha 2 — `from typing import Optional`**
  - Importa `Optional`, usado para indicar que uma variável pode ter um tipo ou ser `None`.
  - Neste arquivo, `Optional[date]` significa `date` ou `None`.

- **Linha 3 — `from fastapi import APIRouter, status`**
  - Importa `APIRouter`, usado para agrupar rotas.
  - Importa `status`, que fornece nomes legíveis para códigos HTTP.

- **Linha 4 — `from schemas.clima import EnderecoClimaResponse`**
  - Importa o schema que representa o formato final da resposta.
  - Ele será usado no parâmetro `response_model` da rota.

- **Linha 5 — `from fastapi import HTTPException, Query`**
  - `HTTPException` permite devolver erros HTTP controlados.
  - `Query` configura parâmetros de consulta, como `data_previsao`.

- **Linhas 6 a 8 — importação do service**
  - Importa as exceções criadas pelo service.
  - Importa `consultar_clima_por_cep`, que contém a lógica de negócio.
  - O controller não faz mais chamadas diretas para `requests`.

- **Linha 9 — linha em branco**
  - Separa os imports da configuração da rota.

- **Linha 10 — `router = APIRouter(...)`**
  - Cria um agrupador de rotas.
  - `prefix="/clima"` adiciona `/clima` ao início das rotas desse router.
  - `tags=["Clima"]` agrupa o endpoint com o nome `Clima` na documentação.

- **Linha 11 — linha em branco**
  - Separa a configuração do router da definição da rota.

- **Linha 12 — decorador `@router.get(...)`**
  - Registra a função seguinte como uma rota HTTP GET.
  - `/{cep}` define `cep` como parâmetro obrigatório no caminho.
  - `response_model=EnderecoClimaResponse` determina o formato da resposta.
  - `summary` define o título curto exibido no Swagger.
  - Como o router possui prefixo `/clima`, o caminho final é `/clima/{cep}`.

- **Linha 13 — `def consultar_endereco(...)`**
  - Declara a função executada quando a rota é chamada.
  - `cep: str` informa que o CEP será tratado como texto.
  - CEP é texto porque pode conter zeros à esquerda.

- **Linha 14 — `data_previsao: Optional[date]`**
  - Define um parâmetro opcional de data.
  - Se o usuário enviar `2026-09-24`, o FastAPI converte o texto para `date`.
  - Se não enviar, o valor será `None`.

- **Linha 15 — `Query(None, description=...)`**
  - Define o valor padrão como `None`.
  - Informa ao FastAPI que o parâmetro é uma query string.
  - A descrição aparece na documentação em `/docs`.
  - O parâmetro é usado assim: `?data_previsao=2026-09-24`.

- **Linhas 16 e 17 — fechamento da assinatura**
  - Fecham a definição dos parâmetros da função.

- **Linha 18 — `try:`**
  - Inicia um bloco que pode gerar as exceções específicas do service.

- **Linha 19 — `return consultar_clima_por_cep(...)`**
  - Chama o service passando o CEP e a data.
  - Retorna o resultado para o FastAPI.
  - A validação final será feita pelo `response_model`.

- **Linha 20 — `except CepInvalidoError:`**
  - Captura o erro lançado quando a BrasilAPI considera o CEP inválido.

- **Linha 21 — `raise HTTPException(`**
  - Converte o erro interno do service em uma resposta HTTP.

- **Linha 22 — `status_code=status.HTTP_400_BAD_REQUEST`**
  - Devolve o status HTTP `400`.
  - Indica que o cliente enviou dados inválidos.

- **Linha 23 — `detail=...`**
  - Define a mensagem que será enviada no corpo da resposta.

- **Linha 24 — `)`**
  - Fecha a criação da `HTTPException`.

- **Linha 25 — `except CepNaoEncontradoError:`**
  - Captura o erro para um CEP que não foi localizado.

- **Linhas 26 a 29 — resposta `404`**
  - Cria uma `HTTPException` com status `404`.
  - O status significa que o recurso procurado não foi encontrado.
  - A mensagem informa que o CEP não existe na BrasilAPI.

- **Linha 30 — `except CepServicoIndisponivelError:`**
  - Captura uma falha da BrasilAPI.

- **Linhas 31 a 34 — resposta `500`**
  - Retorna `500 Internal Server Error`.
  - Esse status informa uma falha no serviço externo ou no processamento interno.

- **Linha 35 — `except ClimaServicoIndisponivelError:`**
  - Captura falhas da API Open-Meteo.

- **Linhas 36 a 39 — resposta `502`**
  - Retorna `502 Bad Gateway`.
  - Esse status é adequado quando a aplicação funciona, mas uma API externa falha.

### Papel do controller

O controller é a camada HTTP. Ele conhece FastAPI, rotas, query parameters e códigos HTTP. Ele não precisa conhecer os detalhes de como as APIs externas são chamadas.

## 6. Arquivo `services/clima.py`

Código atual:

```python
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
```

### Explicação linha por linha

- **Linha 1 — `from datetime import date`**
  - Importa o tipo usado na anotação de `data_previsao`.

- **Linha 2 — linha em branco**
  - Separa imports.

- **Linha 3 — `import requests`**
  - Importa a biblioteca usada para fazer requisições HTTP para as APIs externas.

- **Linhas 4 e 5 — linhas em branco**
  - Separam os imports da declaração das exceções.

- **Linha 6 — `class CepInvalidoError(Exception):`**
  - Cria um erro específico para CEP inválido.
  - Ele herda de `Exception`, a classe base dos erros comuns do Python.

- **Linha 7 — `pass`**
  - Define um corpo vazio para a classe.
  - A classe não precisa de lógica; seu nome já identifica o tipo do problema.

- **Linha 9 — `class CepNaoEncontradoError(Exception):`**
  - Representa um CEP que não foi encontrado.

- **Linha 10 — `pass`**
  - Mantém essa exceção sem comportamento adicional.

- **Linha 12 — `class CepServicoIndisponivelError(Exception):`**
  - Representa uma falha ou indisponibilidade da BrasilAPI.

- **Linha 13 — `pass`**
  - Corpo vazio da exceção personalizada.

- **Linha 15 — `class ClimaServicoIndisponivelError(Exception):`**
  - Representa uma falha na consulta à Open-Meteo.

- **Linha 16 — `pass`**
  - Corpo vazio da exceção personalizada.

- **Linha 19 — definição de `consultar_clima_por_cep`**
  - Declara a função principal do service.
  - Recebe `cep` como texto.
  - Recebe `data_previsao` como `date` ou `None`.
  - Retorna um dicionário.

- **Linha 20 — chamada à BrasilAPI**
  - Monta a URL usando o CEP recebido.
  - `requests.get` executa uma requisição HTTP GET.
  - A resposta fica guardada em `resposta_cep`.

- **Linhas 22 e 23 — status `400`**
  - Verificam se a BrasilAPI retornou `400`.
  - Nesse caso, lançam `CepInvalidoError`.
  - `raise` interrompe a execução normal da função.

- **Linhas 24 e 25 — status `404`**
  - Verificam se o CEP não foi encontrado.
  - Lançam `CepNaoEncontradoError`.

- **Linhas 26 e 27 — status `500`**
  - Verificam uma falha da BrasilAPI.
  - Lançam `CepServicoIndisponivelError`.

- **Linha 29 — `dados_cep = resposta_cep.json()`**
  - Converte o corpo JSON da resposta para estruturas Python, normalmente dicionários e listas.
  - O resultado contém os dados do endereço e as coordenadas.

- **Linha 30 — acesso às coordenadas**
  - Entra no campo `location` e depois no campo `coordinates`.
  - O resultado é armazenado em `coordenadas`.

- **Linha 31 — conversão da latitude**
  - Lê a latitude e converte o valor para `float`.
  - Exemplo: `-23.5505`.

- **Linha 32 — conversão da longitude**
  - Lê a longitude e converte o valor para `float`.

- **Linhas 34 a 37 — montagem inicial da URL climática**
  - Define o endpoint de previsão da Open-Meteo.
  - Inclui latitude e longitude como parâmetros.
  - Os parênteses permitem dividir uma string longa em várias linhas.
  - O prefixo `f` permite inserir os valores das variáveis na string.

- **Linha 39 — `if data_previsao:`**
  - Verifica se o usuário informou uma data.
  - Um objeto `date` preenchido é considerado verdadeiro.
  - `None` é considerado falso.

- **Linhas 40 a 43 — consulta para uma data específica**
  - `start_date` define o início do período.
  - `end_date` define o fim do período.
  - Como as duas datas são iguais, a consulta representa apenas um dia.
  - `daily=temperature_2m_max,wind_speed_10m_max` solicita temperatura máxima e velocidade máxima do vento.
  - `timezone=auto` permite que a Open-Meteo escolha o fuso horário adequado às coordenadas.

- **Linhas 44 e 45 — consulta do clima atual**
  - Quando não existe data, solicita `current_weather=true`.
  - Nesse caso, a resposta contém as condições atuais em vez de uma previsão diária.

- **Linha 47 — chamada à Open-Meteo**
  - Executa a requisição usando a URL montada.
  - A resposta fica em `resposta_clima`.

- **Linhas 49 e 50 — validação da resposta climática**
  - Verificam se o status não é `200`.
  - Qualquer status diferente de `200` gera `ClimaServicoIndisponivelError`.

- **Linhas 52 a 55 — retorno do service**
  - Retorna um dicionário com duas chaves: `endereco` e `clima`.
  - `endereco` contém a resposta original da BrasilAPI.
  - `clima` contém a resposta original da Open-Meteo.
  - O controller não precisa conhecer a estrutura interna das chamadas externas.

### Por que o service usa exceções próprias?

O service não lança `HTTPException`, porque essa classe pertence ao FastAPI e à camada HTTP. Em vez disso, o service lança erros com nomes próprios. O controller decide como cada erro será apresentado ao cliente.

Essa separação permite reutilizar o service em outro contexto, como um script, uma tarefa agendada ou outro tipo de interface.

## 7. Arquivo `schemas/clima.py`

Código atual:

```python
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

            return {
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

            return {
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
```

### Explicação linha por linha

- **Linha 1 — `from typing import Any`**
  - Importa `Any`, que representa um valor de tipo desconhecido ou variável.
  - É usado porque os validadores recebem o JSON externo antes da conversão final.

- **Linha 2 — importação do Pydantic**
  - `BaseModel` cria schemas com validação.
  - `Field` permite configurar campos, como o padrão do CEP.
  - `model_validator` cria funções executadas durante a validação do modelo.

- **Linhas 4 a 8 — classe `Endereco`**
  - Define o formato interno do endereço.
  - `logradouro`, `bairro`, `cidade` e `estado` são textos obrigatórios.
  - Como não existe `Optional`, todos esses campos precisam estar presentes após a adaptação.

- **Linhas 10 a 12 — classe `Coordenadas`**
  - Define latitude e longitude como números decimais.

- **Linha 14 — classe `EnderecoResponse`**
  - Representa a resposta de endereço que a API da aplicação expõe.

- **Linha 15 — campo `cep`**
  - Define o CEP como texto.
  - `Field(...)` indica que o campo é obrigatório.
  - O padrão aceita `01001000` e `01001-000`.
  - `\d{5}` exige cinco números no início.
  - `-?` permite hífen opcional.
  - `\d{3}` exige três números no final.

- **Linha 16 — `endereco: Endereco`**
  - Informa que o campo `endereco` deve seguir o schema `Endereco`.

- **Linha 17 — `coordenadas: Coordenadas`**
  - Informa que o campo deve seguir o schema `Coordenadas`.

- **Linha 19 — `@model_validator(mode="before")`**
  - Executa o método seguinte antes da validação normal dos campos.
  - Isso permite transformar o formato da BrasilAPI antes de Pydantic validar o resultado.

- **Linha 20 — `@classmethod`**
  - Permite chamar o método pela classe.
  - É necessário para o formato usado pelo validador.

- **Linha 21 — definição de `adaptar_dados_brasilapi`**
  - Recebe os dados externos.
  - `dados: Any` aceita o JSON original.
  - `-> Any` informa que o método pode devolver os dados transformados ou originais.

- **Linha 22 — teste dos dados**
  - Verifica se a entrada é um dicionário.
  - Verifica se existe a chave `street`, usada pela BrasilAPI.
  - Esse teste evita transformar dados que já estejam no formato final.

- **Linha 23 — `location = dados.get(...)`**
  - Obtém a localização.
  - Se não existir, usa um dicionário vazio.

- **Linha 24 — `coordinates = location.get(...)`**
  - Obtém as coordenadas dentro da localização.
  - Se não existirem, usa um dicionário vazio.

- **Linhas 26 a 36 — dicionário adaptado**
  - Renomeia `street` para `logradouro`.
  - Renomeia `neighborhood` para `bairro`.
  - Mantém os nomes `city` e `state` adaptados para `cidade` e `estado`.
  - Converte latitude e longitude para `float`.
  - A estrutura final passa a coincidir com os schemas próprios da aplicação.

- **Linha 37 — `return dados`**
  - Se os dados não tiverem o formato esperado da BrasilAPI, eles são devolvidos sem transformação.
  - Depois disso, o Pydantic tentará validá-los normalmente.

- **Linhas 39 a 45 — classe `ClimaResponse`**
  - Define o formato climático padronizado da aplicação.
  - A temperatura é `float`.
  - As unidades, velocidade e indicação de período são textos.

- **Linha 47 — validador `adaptar_dados_meteo`**
  - Também é executado antes da validação normal.
  - Seu objetivo é converter dois formatos possíveis da Open-Meteo para um formato único.

- **Linha 50 — teste de tipo**
  - Se os dados não forem um dicionário, não tenta acessá-los como dicionário.
  - Devolve o valor para que a validação normal trate o caso.

- **Linha 53 — teste de `current_weather`**
  - Identifica a resposta usada quando nenhuma data foi informada.

- **Linhas 54 e 55 — dados atuais e unidades**
  - Separam os valores atuais das unidades correspondentes.
  - `.get(..., {})` evita erro quando a chave não existir.

- **Linhas 57 a 62 — adaptação do clima atual**
  - `temperature` vira `temperatura`.
  - `windspeed` vira `velocidade_vento`.
  - As unidades são traduzidas para os nomes do schema.
  - `is_day == 1` vira `Dia`; caso contrário, vira `Noite`.
  - Os valores numéricos são convertidos para `float`.

- **Linha 63 — `elif "daily" in dados`**
  - Caso não seja uma resposta de clima atual, verifica se é uma resposta diária.

- **Linhas 64 e 65 — leitura dos dados diários**
  - Obtém os dados diários e suas unidades.

- **Linha 67 — lista de temperaturas**
  - Obtém a lista de temperaturas máximas.
  - Se não existir, usa `[0.0]` como valor padrão.

- **Linha 69 — lista de velocidades do vento**
  - Obtém a lista de velocidades máximas do vento.
  - Se não existir, usa `[0.0]`.

- **Linhas 71 a 77 — adaptação da previsão diária**
  - Seleciona o primeiro item das listas, porque a consulta solicita apenas um dia.
  - Usa `0.0` se a lista estiver vazia.
  - Traduz as chaves externas para os nomes do schema.
  - Define `dia_noite` como `dia todo`, pois a previsão diária representa o dia inteiro.

- **Linha 78 — `return dados`**
  - Devolve dados desconhecidos sem transformação para a validação normal tratar.

- **Linhas 80 a 83 — classe `EnderecoClimaResponse`**
  - Define o modelo completo da resposta.
  - `endereco` precisa ser um `EnderecoResponse`.
  - `clima` precisa ser um `ClimaResponse`.

### Papel dos schemas

Os schemas não fazem chamadas HTTP. Eles garantem que a resposta final tenha um formato consistente, mesmo que BrasilAPI e Open-Meteo usem nomes e estruturas diferentes.

## 8. Arquivo `services/__init__.py`

Esse arquivo está vazio de propósito. A existência dele informa ao Python que `services` pode ser tratado como um pacote e permite imports como:

```python
from services.clima import consultar_clima_por_cep
```

## 9. Arquivo `pyproject.toml`

Trecho principal:

```toml
[project]
name = "climatempo"
version = "0.1.0"
description = ""
authors = [
    {name = "Sarah Janne",email = "sarahjanne.enos@hotmail.com"}
]
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "requests (>=2.32.0,<3.0.0)",
    "uvicorn (>=0.53.0,<0.54.0)"
]


[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

### Explicação

- `[project]`: inicia a configuração principal do projeto.
- `name`: nome do pacote.
- `version`: versão atual.
- `description`: descrição curta do pacote.
- `authors`: informações da autoria.
- `requires-python = ">=3.11"`: exige Python 3.11 ou superior.
- `dependencies`: lista as bibliotecas necessárias.
- `fastapi`: framework usado para criar a API.
- `requests`: biblioteca usada para chamar as APIs externas.
- `uvicorn`: servidor ASGI usado para executar a aplicação.
- `[build-system]`: define como o projeto pode ser construído.
- `poetry-core`: componente responsável pela construção usando o padrão Poetry.
- `build-backend`: define o backend de construção do pacote.

## 10. Arquivo `.vscode/settings.json`

Código atual:

```json
{
    "python-envs.defaultEnvManager": "ms-python.python:poetry",
    "python-envs.defaultPackageManager": "ms-python.python:poetry"
}
```

### Explicação

- `python-envs.defaultEnvManager`: informa ao VS Code que o gerenciador padrão de ambientes Python é o Poetry.
- `python-envs.defaultPackageManager`: informa que o Poetry também será usado como gerenciador de pacotes.
- As chaves ficam dentro de `{}` porque o arquivo usa o formato JSON.

## 11. Documentação da API

Depois de iniciar o servidor, acesse:

```text
http://127.0.0.1:8000/docs
```

A rota aparecerá como:

```text
GET /clima/{cep}
```

Os parâmetros são:

- `cep`: obrigatório e vem no caminho da URL.
- `data_previsao`: opcional e vem na query string.

Exemplo sem data:

```text
GET /clima/01001000
```

Nesse caso, a aplicação consulta o clima atual.

Exemplo com data:

```text
GET /clima/01001000?data_previsao=2026-09-24
```

Nesse caso, a aplicação consulta a previsão diária para a data informada.

## 12. Como executar

No PowerShell, dentro da pasta do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Ou diretamente pelo Python do ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## 13. Resumo da separação de responsabilidades

```text
Requisição HTTP
      |
      v
Controller: recebe CEP e data, trata HTTP
      |
      v
Service: consulta BrasilAPI e Open-Meteo
      |
      v
Schemas: adapta e valida os dados
      |
      v
Resposta JSON padronizada
```

A regra principal é:

- Controller conhece HTTP.
- Service conhece regras de negócio e integrações.
- Schema conhece formatos e validação de dados.
- `main.py` conhece a montagem da aplicação.
