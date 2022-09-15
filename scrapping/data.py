import json

import httpx
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from scrapping.bs4 import ParseHTML
from scrapping.selenium import Browser


def notas_semestre(session: str, login=None, senha=None) -> json.dumps:
    NAMES = ['ccr', 'turma', 'plano_de_ensino', 'total_de_faltas', 'frequencia', 'media_final', 'notas']
    if not session:
        session = prepare_selenium_session(login, senha)
    response = get_html(session, 'https://aluno.uffs.edu.br/aluno/restrito/academicos/notas_semestre.xhtml')
    soup = BeautifulSoup(response.content, features="html.parser")
    parse = ParseHTML(soup)

    data = parse.table_json_by_id(NAMES, 'tbody', 'frmPrincipal:tblTurmas_data', 'td')
    return data


def get_html(session: str, url: str) -> httpx.get:
    cookies = httpx.Cookies()
    cookies.set('JSESSIONID', session)
    response = httpx.get(url, cookies=cookies)
    return response


def prepare_selenium_session(login, senha) -> str:
    browser = Browser(ChromeDriverManager().install())
    browser.driver.get('https://id.uffs.edu.br/id/XUI/#login/')
    browser.wait_page(10, 'idToken1', By.ID)
    browser.login(By.ID, 'idToken1', login, 'idToken2', senha, 'loginButton_0')
    browser.wait_page(10, 'input-username', By.ID)
    browser.driver.get(f"https://aluno.uffs.edu.br/;jsessionid={browser.driver.session_id}")
    try:
        browser.wait_page(10, 'ATIVA', By.PARTIAL_LINK_TEXT)
        browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'ATIVA').click()
    except:
        pass
    browser.set_session('JSESSIONID')
    return browser.session
