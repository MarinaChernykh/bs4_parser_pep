import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, RESULTS_DIR, DATETIME_FORMAT,
                       PRETTY_OUTPUT, FILE_OUTPUT)


def default_output(results, cli_args):
    """Выводит данные в консоль без таблицы."""
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    """Выводит данные в консоль в виде таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Сохраняет данные в csv файл в папку results."""
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


OUTPUT_FORMAT = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
}


def control_output(results, cli_args):
    """
    Запускает функцию вывода данных в соответствии
    с указанным в параметрах команды способом.
    """
    OUTPUT_FORMAT.get(cli_args.output, default_output)(results, cli_args)
