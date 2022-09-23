import json
import re
import unicodedata
from typing import Union

from bs4 import BeautifulSoup


def beautiful_string(s):
    return re.sub('[^A-Za-z0-9]+', '',
                  ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')).lower()


class ParseHTML:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def get_table_head(self, type_selector: str, id_selector: str, fetched_selector: str) -> json.dumps:
        result = []
        for element_selector in self.soup.find(type_selector, id=id_selector):
            for element in element_selector.findAll(fetched_selector):
                element = beautiful_string(element.text.strip())
                result.append(element)
        return result

    def table_json_by_id(self, names: Union[list, None], type_selector: str, id_selector: str,
                         fetched_selector: str) -> json.dumps:
        result = []
        for id, element_selector in enumerate(self.soup.find(type_selector, id=id_selector)):
            temporary_dict = {'id': id}
            for key, element in enumerate(element_selector.findAll(fetched_selector)):
                temporary_dict[names[key]] = element.text.strip()
            result.append(temporary_dict)
        return result
