from pathlib import Path
from urllib.parse import urljoin


MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOADS_URL = urljoin(MAIN_DOC_URL, 'download.html')
PEPS_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
RESULTS_DIR = 'results'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

OUTPUT_CHOICES = (PRETTY_OUTPUT, FILE_OUTPUT)
