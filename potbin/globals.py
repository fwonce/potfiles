__author__ = 'fwonce'

DEFAULT_LOCAL_LOCATION = '~'
PDEC_FILE_DIR = './conf/'
PDEC_FILE_EXT = '.pdec'
declared_segs={}

LINK_MODE_DELIMITER = '>'
COPY_MODE_DELIMITER = '|'

SYNC_DIR_MARKER = '.sync_dir'

IGNORE_FILES = [
    SYNC_DIR_MARKER,
    '.DS_Store'
]