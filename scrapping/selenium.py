from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self):
        self.driver = self.prepare_browser()
        self.session = None

    def prepare_browser(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        try:
            browser = webdriver.Chrome(options=chrome_options)
        except:
            browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        return browser

    def wait_page(self, timeout: int, selector: str, type_selector: By) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located((type_selector, selector)))
            return True
        except TimeoutException:
            return False

    def login(self, type_selector: By, selector_login: str, value_login: str, selector_pass: str, value_pass: str,
              selector_submit: str) -> None:
        self.driver.find_element(type_selector, selector_login).send_keys(value_login)
        self.driver.find_element(type_selector, selector_pass).send_keys(value_pass)
        self.driver.find_element(type_selector, selector_submit).click()

    def set_session(self, name: str) -> None:
        for cookie in self.driver.get_cookies():
            #JSESSIONID
            if cookie['name'] == name:
                self.session = cookie['value']
