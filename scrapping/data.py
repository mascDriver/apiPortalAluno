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

    payload = {'callbacks': [{'type': 'NameCallback', 'output': [{'name': 'prompt', 'value': 'IdUFFS ou CPF'}],
                              'input': [{'name': 'IDToken1', 'value': f'{login}'}]},
                             {'type': 'PasswordCallback', 'output': [{'name': 'prompt', 'value': 'Senha'}],
                              'input': [{'name': 'IDToken2', 'value': f'{senha}'}]}]}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'amlbcookie=01'
    }
    authentication = httpx.post("https://id.uffs.edu.br/id/json/authenticate", headers=headers, json=payload)
    if authentication.is_success:
        browser.driver.get('https://aluno.uffs.edu.br/')
        browser.driver.add_cookie({'name': 'iPlanetDirectoryPro', 'value': authentication.json()['tokenId']})
        browser.driver.get('https://aluno.uffs.edu.br/')
        browser.set_session('JSESSIONID')
        headers['iPlanetDirectoryPro'] = authentication.json()['tokenId']
        browser.set_options(httpx.get(f'https://id.uffs.edu.br/id/json/users/{login}', headers=headers).json())

    else:
        browser.driver.get('https://id.uffs.edu.br/id/XUI/#login/')
        browser.wait_page(TIMEOUT_CONNECTION, 'idToken1', By.ID)
        browser.login(By.ID, 'idToken1', login, 'idToken2', senha, 'loginButton_0')
        browser.wait_page(TIMEOUT_CONNECTION, 'input-username', By.ID)
        browser.set_session('JSESSIONID')
        browser.driver.get(f"https://aluno.uffs.edu.br/;jsessionid={browser.session}")

    if not browser.driver.current_url.endswith('.xhtml'):
        browser.wait_page(TIMEOUT_CONNECTION, 'frmPrincipal:j_idt30:0:lnkMatDesc_')
        if browser.exists_element(selector='frmPrincipal:j_idt30:0:lnkMatDesc_'):
            try:
                browser.driver.find_element(value='frmPrincipal:j_idt30:0:lnkMatDesc_').click()
            except:
                pass
            else:
                browser.set_session('JSESSIONID')
    return browser


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
