from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from scrapping.data import notas_semestre, notas_matriz, notas_semestre_detalhada
from grade.crud import get_current_user

router_grade = APIRouter()


@router_grade.post("/login", tags=['Grade'])
def set_login(credentials: HTTPBasicCredentials = Depends(get_current_user)):
    """
    Endpoint para login e retorno de sessao para navegar no sistema
    """
    return dict(session=credentials.session, name=credentials.name)


@router_grade.get("/notas_semestre/{session}", tags=['Grade'])
def get_notas_semestre(session: str):
    """
    Endpoint para acesso a notas do semestre atual
    """
    return notas_semestre(session)


@router_grade.get("/notas_semestre/{ccr_id}/detalhada/{session}", tags=['Grade'])
def get_notas_semestre(session: str, ccr_id: int):
    """
    Endpoint para acesso a notas detalhadas do semestre atual
    """
    return notas_semestre_detalhada(session, ccr_id)


@router_grade.get("/notas_matriz/{session}", tags=['Grade'])
def get_notas_matriz(session: str):
    """
    Endpoint para acesso a todas as notas ja recebida pelo aluno
    """
    return notas_matriz(session)
