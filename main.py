from fastapi import FastAPI

from grade.views import router_grade

tags_metadata = [
    {
        "name": "Grade",
        "description": "Bloco para acesso as notas em formato json",
    },
]

app = FastAPI(
    title='Api Portal do Aluno UFFS',
    version='0.0.1',
    contact={
        "name": "Diogo Baltazar do Nascimento",
        "url": "https://github.com/mascDriver",
        "email": "diogobaltazardonascimento@outlook.com",
    },
    docs_url='/', openapi_tags=tags_metadata)

app.include_router(router_grade)
