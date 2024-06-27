from fastapi import FastAPI, Request, Form,Depends,Query,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date
import uvicorn
from sqlmodel import SQLModel, create_engine,Field,Session,select

app = FastAPI()

templates = Jinja2Templates(directory='produto_farmacia/templates')

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Remedio(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nome: str
    tipo: str
    preco: float
    quantidade: int
    datavencimento: date

def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def create_remedio(db: Session, nome: str, tipo: str, preco: float, quantidade: int, datavencimento: date):
    remedio = Remedio(nome=nome, tipo=tipo, preco=preco, quantidade=quantidade, datavencimento=datavencimento)
    db.add(remedio)
    db.commit()
    db.refresh(remedio)
    return remedio

def get_remedios(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Remedio).offset(skip).limit(limit).all()

def get_db():
    with Session(engine) as session:
        yield session

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    REMEDIOS = db.exec(select(Remedio)).all()
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": Remedio})

@app.post("/add-remedio", response_class=HTMLResponse)
async def add_remedio(request: Request, nome: str = Form(...), tipo: str = Form(...), preco: float = Form(...), quantidade: int = Form(...), datavencimento: date = Form(...), db: Session = Depends(get_db)):
    create_remedio(db, nome, tipo, preco, quantidade, datavencimento)
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": db.query(Remedio).all()})

@app.get("/search", response_class=HTMLResponse)
async def search_remedio(request: Request, nome: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    resultados = db.exec(select(Remedio).where(Remedio.nome.contains(nome))).all()
    return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": resultados})

@app.post("/delete-remedio/{remedio_id}", response_class=HTMLResponse)
async def delete_remedio(remedio_id: int, request: Request, db: Session = Depends(get_db)):
    remedio = db.get(Remedio, remedio_id)
    if remedio:
        db.delete(remedio)
        db.commit()
        return templates.TemplateResponse("home.html", {"request": request, "REMEDIOS": db.query(Remedio).all()})
    else:
        raise HTTPException(status_code=404, detail="Remédio não encontrado.")

if __name__ == "__main__":
    create_database()
    uvicorn.run(app, host="127.0.0.1", port=8000)