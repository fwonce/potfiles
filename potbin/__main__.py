#!/usr/bin/env python3
#
# The syntax for the resource file (`resources.pdec`):
#
# - Each line consists of cloud/local path pair.
# - Supported path pair delimiter:
#   - `|`: a vertical bar, means the cloud file is copied to the local path
#   - `>`: means the cloud file is linked (symlink) to the local path
# - Supported local path placeholders:
#   - $userhome:
#       Home directory (This must be put at the beginning)
#   - $appfolder(appname, appauther):
#       AppData folder for given appname
#   - $iniparser(filename, keys):
#       Parsing the ini file to get a path segment. e.g., Firefox profile sub path - Profiles/xxxx.xxxx
# - Basename-Auto-Inferring: local path can omit the basename if it's the same with the one in the cloud path.
#   - When used under Unix, the leading underscore of the cloud path will be replaced with a dot.
#   - Directories cannot use this feature.

from operator import *
from potbin.helpers import *


def process_pdec_file(file):
    print("Processing pdec file:", file)
    try:
        pdec = open(file, 'r')
    except (FileNotFoundError, PermissionError):
        sys.exit('File ' + RESOURCES_LIST + ' cannot be found or read.')
    with pdec:
        for line in pdec:
            line = line.strip()
            # ignore comment lines
            if not line or line.startswith('#'):
                continue
            if line.startswith('$'):
                parse_custom_decl(line)
                continue
            if contains(line, COPY_MODE_DELIMITER):
                delimiter = COPY_MODE_DELIMITER
            elif contains(line, LINK_MODE_DELIMITER):
                delimiter = LINK_MODE_DELIMITER
            else:
                print('Skipping invalid line:', line)
                continue
            pair = line.split(delimiter)
            if 2 != len(pair):
                print('Skipping invalid line:', line)
                continue

            cloud = pair[0].strip()
            local = pair[1].strip()
            if not path.exists(cloud):
                print('Skipping invalid cloud path:', cloud)
                continue
            mark_sync_dir_if_needed(cloud)
            try:
                local = parse_local(local)
            except InvalidSegmentException as e:
                print('Skipping invalid local path:', local, ', due to', e.msg)
                continue
            local = append_basename_if_needed(cloud, local)

            if LINK_MODE_DELIMITER == delimiter:
                do_link(cloud, local)
            elif COPY_MODE_DELIMITER == delimiter:
                do_copy_on_newer(cloud, local)


def main():
    for file in os.listdir(PDEC_FILE_DIR):
        if file.endswith(PDEC_FILE_EXT):
            process_pdec_file(PDEC_FILE_DIR + file)


if __name__ == "__main__":
    main()
