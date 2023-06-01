from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from grade.models import User
from scrapping.data import prepare_selenium_session

security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    browser = prepare_selenium_session(credentials.username, credentials.password)
    if browser.session:
        name = ''.join(browser.options.get('cn', 'Aluno'))
        browser.driver.quit()
        return User(session=browser.session, username=credentials.username, name=name,
                    expiration=datetime.now() + timedelta(minutes=30))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
        headers={"WWW-Authenticate": "Basic"},
    )
