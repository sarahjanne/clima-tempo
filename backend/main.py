from fastapi import FastAPI

from controllers.clima import router as clima_router

app = FastAPI(
    title="ChoveAí",
    description="API de Previsão do Tempo por CEP")


app.include_router(clima_router)