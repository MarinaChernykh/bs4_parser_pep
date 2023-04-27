import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (LOG_DIR, LOG_FILE, LOG_DT_FORMAT,
                       LOG_FORMAT, OUTPUT_CHOICES)


def configure_argument_parser(available_modes):
    """Конфигурация режимов работы парсера."""
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=OUTPUT_CHOICES,
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    """Конфигурация логгирования."""
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 ** 6, backupCount=5
    )

    logging.basicConfig(
        datefmt=LOG_DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
