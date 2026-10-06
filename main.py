from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from controllers.clima import router as clima_router

app = FastAPI(
    title="ChoveAí",
    description="API de Previsão do Tempo por CEP")


app.include_router(clima_router)


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return RedirectResponse(url="/clima/pagina")