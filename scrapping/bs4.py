import json
from typing import Union

from bs4 import BeautifulSoup


class ParseHTML:
    def __init__(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def table_json_by_id(self, names: Union[list, None], type_selector: str, id_selector: str,
                         fetched_selector: str) -> json.dumps:
        result = []
        for element_selector in self.soup.find(type_selector, id=id_selector):
            temporary_dict = {}
            for key, element in enumerate(element_selector.findAll(fetched_selector)):
                temporary_dict[names[key]] = element.text.strip()
            result.append(temporary_dict)
        return result
