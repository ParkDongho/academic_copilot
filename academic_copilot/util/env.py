import os

S2_API_KEY         = os.environ.get('S2_API_KEY', None)

PAPER_INFO_PATH    = os.environ.get('PAPER_INFO_PATH', None)
PAPER_IMG_PATH   = os.environ.get('PAPER_IMG_PATH', None)
JOURNAL_LIST_PATH  = os.environ.get('JOURNAL_LIST_PATH', None)
CITATION_INFO_PATH = os.environ.get('CITATION_INFO_PATH', None)
REFERENCE_INFO_PATH = os.environ.get('REFERENCE_INFO_PATH', None)
NEW_PAPER_LIST     = os.environ.get('NEW_PAPER_LIST', None)

ORIGINAL_PAPER_PATH = os.environ.get('ORIGINAL_PAPER_PATH', None)
ORIGINAL_PAPER_INFO_PATH = os.environ.get('ORIGINAL_PAPER_INFO_PATH', None)

MAX_RETRIES = os.environ.get('MAX_RETRIES', 5)