from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from scrapping.data import prepare_selenium_session, notas_semestre

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
    session: str
    username: str
    expiration: datetime


security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    session = prepare_selenium_session(credentials.username, credentials.password)
    if session:
        return User(session=session, username=credentials.username, expiration=datetime.now() + timedelta(minutes=30))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
        headers={"WWW-Authenticate": "Basic"},
    )


@app.get("/notas_semestre")
def get_notas_semestre(credentials: HTTPBasicCredentials = Depends(get_current_user)):
    """
    Pegar notas do semestre atual
    :param credentials: class
    :type credentials: dict
    :return: json
    """
    return notas_semestre(credentials.session)
