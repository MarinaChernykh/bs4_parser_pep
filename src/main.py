import re
import logging
from urllib.parse import urljoin

import requests_cache
from requests import RequestException
from tqdm import tqdm

from constants import (BASE_DIR, DOWNLOADS_DIR, MAIN_DOC_URL, WHATS_NEW_URL,
                       DOWNLOADS_URL, PEPS_URL, EXPECTED_STATUS)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_soup, get_response, find_tag


def whats_new(session):
    """
    Собирает данные об изменениях в версиях Python
    (статьи Whats New In Python на docs.python.org)
    и формирует список с ссылкой на статью, заголовком, автором.
    """
    try:
        soup = get_soup(session, WHATS_NEW_URL)
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {WHATS_NEW_URL}',
            stack_info=True
        )
        return
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_href = find_tag(section, 'a')['href']
        version_link = urljoin(WHATS_NEW_URL, version_href)
        try:
            soup = get_soup(session, version_link)
        except RequestException:
            logging.exception(
                f'Возникла ошибка при загрузке страницы {version_link}',
                stack_info=True
            )
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    """
    Собирает данные о существующих версиях Python
    и их актуальном статусе.
    """
    try:
        soup = get_soup(session, MAIN_DOC_URL)
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {MAIN_DOC_URL}',
            stack_info=True
        )
        return
    ul_tags = soup.select('div.sphinxsidebarwrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """
    Скачивает с docs.python.org pdf-файл с документацией
    по наиболее свежей из актуальных версий Python.
    """
    try:
        soup = get_soup(session, DOWNLOADS_URL)
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {DOWNLOADS_URL}',
            stack_info=True
        )
        return
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(DOWNLOADS_URL, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    try:
        response = get_response(session, archive_url)
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {archive_url}',
            stack_info=True
        )
        return
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """
    Собирает информацию по PEP:
    категории, кол-во PEP по каждой категории,
    общее кол-во стандартов.
    """
    try:
        soup = get_soup(session, PEPS_URL)
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {PEPS_URL}',
            stack_info=True
        )
        return
    peps_list = soup.select('#numerical-index tbody tr')
    total_peps_quantity = len(peps_list)
    results = [('Статус', 'Количество')]
    status_counter = {}
    incorrect_statuses = []

    for pep in tqdm(peps_list):
        first_column_tag = find_tag(pep, 'abbr')
        preview_status = EXPECTED_STATUS[first_column_tag.text[1:]]
        pep_href = find_tag(pep, 'a')['href']
        pep_link = urljoin(PEPS_URL, pep_href)
        try:
            soup = get_soup(session, pep_link)
        except RequestException:
            logging.exception(
                f'Возникла ошибка при загрузке страницы {pep_link}',
                stack_info=True
            )
            continue
        pep_info_table = find_tag(soup, 'dl')
        first_column_tags = pep_info_table.find_all('dt')
        real_status_tag = [
            tag for tag in first_column_tags if tag.text == "Status:"][0]
        real_status = real_status_tag.next_sibling.next_sibling.text

        if real_status not in preview_status:
            info_msg = (f'Несовпадающие статусы:\n{pep_link}\n'
                        f'Статус в карточке: {real_status}\n'
                        f'Ожидаемые статусы: {preview_status}\n')
            incorrect_statuses.append(info_msg)

        status_counter[real_status] = status_counter.get(real_status, 0) + 1

    if incorrect_statuses:
        logging.info(*incorrect_statuses)

    results.extend(sorted(status_counter.items()))
    results.append(('Total', total_peps_quantity))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """
    Главная функция парсера.
    Запускает логирование и нужный режим парсера,
    инициирует вывод результатов.
    """
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
