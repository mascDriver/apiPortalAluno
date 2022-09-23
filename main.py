from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from scrapping.data import prepare_selenium_session, notas_semestre, notas_matriz

app = FastAPI(
    title='Api Portal do Aluno UFFS',
    version='0.0.1',
    contact={
        "name": "Diogo Baltazar do Nascimento",
        "url": "https://github.com/mascDriver",
        "email": "diogobaltazardonascimento@outlook.com",
    },
    docs_url='/')


class User(BaseModel):
    name: str
    session: str
    username: str
    expiration: datetime


security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    browser = prepare_selenium_session(credentials.username, credentials.password)
    if browser.session:
        name = browser.driver.find_element(value='frmPrincipal:txtNomeFragCivil').text.strip()
        browser.driver.quit()
        return User(session=browser.session, username=credentials.username, name=name,
                    expiration=datetime.now() + timedelta(minutes=30))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
        headers={"WWW-Authenticate": "Basic"},
    )


@app.post("/login")
def set_login(credentials: HTTPBasicCredentials = Depends(get_current_user)):
    """
    Endpoint para login e retorno de sessao para navegar no sistema
    """
    return dict(session=credentials.session, name=credentials.name)


@app.get("/notas_semestre/{session}")
def get_notas_semestre(session: str):
    """
    Endpoint para acesso a notas do semestre atual
    """
    return notas_semestre(session)


@app.get("/notas_matriz/{session}")
def get_notas_matriz(session: str):
    """
    Endpoint para acesso a todas as notas ja recebida pelo aluno
    """
    return notas_matriz(session)
