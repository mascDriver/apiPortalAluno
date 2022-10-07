import json

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from selenium.webdriver.common.by import By

from scrapping.bs4 import ParseHTML
from scrapping.selenium import Browser


def notas_matriz(session: str, login=None, senha=None):
    if not session:
        browser = prepare_selenium_session(login, senha)
        session = browser.session
    response = get_html(session, 'https://aluno.uffs.edu.br/aluno/restrito/academicos/acompanhamento_matriz.xhtml')
    if response.status_code == 302:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid",
        )
    soup = BeautifulSoup(response.content, features="html.parser")
    parse = ParseHTML(soup)

    NAMES = parse.get_table_head('div', 'frmPrincipal:tblAcompanhamento', 'th')
    data = parse.table_json_by_id(NAMES, 'tbody', 'frmPrincipal:tblAcompanhamento_data', 'td')
    return data


def notas_semestre(session: str, login=None, senha=None) -> json.dumps:
    NAMES = ['ccr', 'turma', 'plano_de_ensino', 'total_de_faltas', 'frequencia', 'media_final', 'notas']
    if not session:
        browser = prepare_selenium_session(login, senha)
        session = browser.session
    response = get_html(session, 'https://aluno.uffs.edu.br/aluno/restrito/academicos/notas_semestre.xhtml')
    if response.status_code == 302:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid",
        )
    soup = BeautifulSoup(response.content, features="html.parser")
    parse = ParseHTML(soup)

    data = parse.table_json_by_id(NAMES, 'tbody', 'frmPrincipal:tblTurmas_data', 'td')
    return data


def get_html(session: str, url: str) -> httpx.get:
    cookies = httpx.Cookies()
    cookies.set('JSESSIONID', session)
    response = httpx.get(url, cookies=cookies, timeout=None)
    return response


def prepare_selenium_session(login, senha) -> Browser:
    browser = Browser()
    browser.driver.get(
        'https://id.uffs.edu.br/id/XUI/#login/&realm=/&forward=true&spEntityID=uffs%3Aportalaluno%3Asp&goto=%2FSSORedirect%2FmetaAlias%2Fidp%3FReqID%3Da44j2fde4f5fd58b3j680e7ej96ddi7%26index%3Dnull%26acsURL%3Dhttps%253A%252F%252Faluno.uffs.edu.br%253A443%252Faluno%252Fsaml%252FSSO%26spEntityID%3Duffs%253Aportalaluno%253Asp%26binding%3Durn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Abindings%253AHTTP-POST&AMAuthCookie=')
    browser.wait_page(2, 'idToken1', By.ID)
    browser.login(By.ID, 'idToken1', login, 'idToken2', senha, 'loginButton_0')
    browser.wait_page(2, 'input-username', By.ID)
    browser.set_session('JSESSIONID')
    browser.driver.get(f"https://aluno.uffs.edu.br/;jsessionid={browser.session}")
    try:
        browser.wait_page(1, 'ATIVA', By.PARTIAL_LINK_TEXT)
        browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'ATIVA').click()
    except:
        pass
    browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'Acompanhamento da Matriz').click()
    browser.set_session('JSESSIONID')
    return browser
