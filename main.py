from fastapi import FastAPI

from controllers.clima import router as clima_router

app = FastAPI(
    title="ChoveAí",
    description="API de Previsão do Tempo por CEP")


@app.get("/")
def raiz():
    return {"status": "ok", "app": "ChoveAí"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


app.include_router(clima_router)