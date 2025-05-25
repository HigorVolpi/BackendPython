import uvicorn
from fastapi import FastAPI
from autenticacao.routers import autenticacao


app = FastAPI()

app.include_router(autenticacao.router)

@app.get("/")
async def root():
    return {"Hello World"}


if __name__ == "__main__":
    uvicorn.run(app)