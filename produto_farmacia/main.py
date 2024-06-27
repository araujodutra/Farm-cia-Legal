from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
from datetime import date
import uvicorn

app = FastAPI()

# Caminho absoluto para o diretório dos templates
templates = Jinja2Templates(directory='produto_farmacia/templates')


# Lista inicial de medicamentos
REMEDIOS: List[Dict[str, Any]] = [
    {"nome": "Dipirona", "tipo": "Genérico","preco": 2.5, "quantidade": 6, "data": date(2024, 3, 15)},
    {"nome": "Omeprazol", "tipo": "Similar", "preco": 15.5, "quantidade": 10, "data": date(2027, 11, 10)},
    {"nome": "Anador", "tipo": "Ético", "preco": 4.5, "quantidade": 4, "data": date(2025, 6, 20)},
    {"nome": "Predsin", "tipo": "Ético", "preco": 38.7, "quantidade": 15, "data": date(2024, 8, 7)}
]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": REMEDIOS})

@app.post("/add-remedio", response_class=HTMLResponse)
async def add_remedio(request: Request, nome: str = Form(...), tipo: str = Form(...), preco: float = Form(...), quantidade: int = Form(...), datavencimento: date = Form(...)):
    novo_remedio = {"nome": nome, "tipo": tipo, "preco": preco, "quantidade": quantidade, "data": datavencimento}
    REMEDIOS.append(novo_remedio)
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": REMEDIOS})

@app.get("/search", response_class=HTMLResponse)
async def search_remedio(request: Request, nome: str):
    resultado = [remedio for remedio in REMEDIOS if nome.lower() in remedio["nome"].lower()]
    if not resultado:
        raise HTTPException(status_code=404, detail="Remedio não encontrado.")
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": REMEDIOS, "resultado": resultado})

@app.post("/delete-remedio", response_class=HTMLResponse)
async def delete_remedio(request: Request, nome: str = Form(...)):
    global REMEDIOS
    REMEDIOS = [remedio for remedio in REMEDIOS if remedio["nome"] != nome]
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": REMEDIOS})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)