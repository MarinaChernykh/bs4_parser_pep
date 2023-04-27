import logging

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException


def get_soup(session, url):
    """Создает DOM-дерево."""
    response = get_response(session, url)
    return BeautifulSoup(response.text, 'lxml')


def get_response(session, url):
    """Отправляет get запрос на url и возвращает ответ."""
    response = session.get(url)
    response.encoding = 'utf-8'
    return response


def find_tag(soup, tag, attrs=None):
    """Производит поиск тега по переданным параметрам."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
