import json

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from selenium.webdriver.common.by import By

from scrapping.bs4 import ParseHTML
from scrapping.selenium import Browser

TIMEOUT_CONNECTION = 5


def notas_matriz(session: str, login=None, senha=None):
    if not session:
        browser = prepare_selenium_session(login, senha)
        session = browser.session
    response = get_html(session, 'https://aluno.uffs.edu.br/aluno/restrito/academicos/acompanhamento_matriz.xhtml')
    if response.status_code != 200:
        browser = Browser()
        browser.driver.get(f'https://aluno.uffs.edu.br/aluno/index_graduacao.xhtml;jsessionid={session}')
        if browser.exists_element(By.PARTIAL_LINK_TEXT, 'Acompanhamento da Matriz'):
            browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'Acompanhamento da Matriz').click()
            browser.set_session('JSESSIONID')

            response = get_html(browser.session,
                                'https://aluno.uffs.edu.br/aluno/restrito/academicos/acompanhamento_matriz.xhtml')

            if response.status_code != 200:
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

    data = parse.table_json_by_id(
        ['ccr', 'turma', 'plano_de_ensino', 'total_de_faltas', 'frequencia', 'media_final', 'notas'],
        'tbody', 'frmPrincipal:tblTurmas_data', 'td'
    )
    return data


def get_html(session: str, url: str) -> httpx.get:
    cookies = httpx.Cookies()
    cookies.set('JSESSIONID', session)
    response = httpx.get(url, cookies=cookies, timeout=None)
    return response


def prepare_selenium_session(login, senha) -> Browser:
    browser = Browser()
    browser.driver.get('https://id.uffs.edu.br/id/XUI/#login/')
    browser.wait_page(TIMEOUT_CONNECTION, 'idToken1', By.ID)
    browser.login(By.ID, 'idToken1', login, 'idToken2', senha, 'loginButton_0')
    browser.wait_page(TIMEOUT_CONNECTION, 'input-username', By.ID)
    browser.set_session('JSESSIONID')
    browser.driver.get(f"https://aluno.uffs.edu.br/;jsessionid={browser.session}")
    browser.wait_page(TIMEOUT_CONNECTION, 'ATIVA', By.PARTIAL_LINK_TEXT)
    if browser.exists_element(By.PARTIAL_LINK_TEXT, 'ATIVA'):
        try:
            browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'ATIVA').click()
        except:
            pass
    if browser.exists_element(By.PARTIAL_LINK_TEXT, 'Notas do Semestre'):
        browser.driver.find_element(By.PARTIAL_LINK_TEXT, 'Notas do Semestre').click()
        browser.set_session('JSESSIONID')
        return browser

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
    )


def notas_semestre_detalhada(session: str, ccr_id: int) -> json.dumps:
    browser = Browser()
    browser.driver.get(f'https://aluno.uffs.edu.br/aluno/restrito/academicos/notas_semestre.xhtml;jsessionid={session}')
    if browser.driver.current_url.startswith('https://id.uffs.edu.br/id/XUI/#login'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid",
        )
    browser.wait_page(TIMEOUT_CONNECTION, f'frmPrincipal:tblTurmas:{ccr_id}:btnNotas', By.ID)
    browser.driver.find_element(By.ID, f'frmPrincipal:tblTurmas:{ccr_id}:btnNotas').click()
    browser.wait_page(TIMEOUT_CONNECTION,
                      "//input[@class='ui-datatable-data' and @id='frmDialogNota:dtbAvaliacao_data']", By.XPATH)
    soup = BeautifulSoup(browser.driver.page_source, features="html.parser")
    parse = ParseHTML(soup)
    nps = parse.table_json_by_id(
        ['data', 'avaliacao', 'peso', 'nota', 'rec', 'nota_final'], 'tbody', 'frmDialogNota:dtbAvaliacao_data', 'td'
    )
    if browser.exists_element(By.XPATH, '//*[@id="frmDialogNota:dtbAvaliacao_row_0"]/td[8]/span'):
        num_nps = len(nps)
        for n in range(num_nps):
            browser.driver.find_element(By.XPATH,
                                        value=f'//*[@id="frmDialogNota:dtbAvaliacao_row_{n}"]/td[8]/span').click()

        browser.wait_page(TIMEOUT_CONNECTION, 'frmDialogNota:dtbAvaliacao:0:dtbInstrumentos_data', By.ID)
        soup = BeautifulSoup(browser.driver.page_source, features="html.parser")
        parse = ParseHTML(soup)

        for n in range(num_nps):
            nps[n]['instrumentos'] = parse.table_json_by_id(
                ['data', 'instrumento', 'peso', 'nota', 'rec', 'nota_rec', 'nota_final'], 'tbody',
                f'frmDialogNota:dtbAvaliacao:{n}:dtbInstrumentos_data', 'td'
            )
    return nps
