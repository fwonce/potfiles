import os
import shutil
import sys

from pathlib import Path
from potbin.parsers import *


__author__ = 'fwonce'


def get_sync_dir_marker_name(dir_name):
    if not dir_name.endswith('/'):
        prefix = dir_name + '/'
    else:
        prefix = dir_name
    return prefix + SYNC_DIR_MARKER


def is_sync_dir(dir_name):
    return path.exists(get_sync_dir_marker_name(dir_name))


def mark_sync_dir_if_needed(cloud):
    """Check if the cloud dir contains a marker file and if not, touch it."""
    if path.isdir(cloud) and not is_sync_dir(cloud):
        marker_file = Path(get_sync_dir_marker_name(cloud))
        marker_file.touch(0o400)


def parse_custom_decl(line):
    pair = line.split('=')
    if 2 != len(pair):
        print('Skipping invalid custom declaration:', line)
        return
    key = pair[0].strip()
    try:
        value = parse_local(pair[1].strip())
        declared_segs[key] = value
        print('Cached custom declaration:', key, '=', value)
    except InvalidSegmentException as e:
        print('Skipping invalid custom declaration:', line, ', due to', e.msg)


def parse_local(local):
    segs = local.split('/')
    expanded_segs = []
    for seg in segs:
        expanded_seg = parse_seg(seg, expanded_segs)
        expanded_segs.append(expanded_seg)
    return '/'.join(expanded_segs)


def parse_seg(seg, expanded_segs):
    # all segments that need further parsing contains '$'
    if not seg.startswith('$'):
        return path.expanduser(seg)
    for parser in ALL_PARSERS:
        parsed_seg = parser.parse(seg, expanded_segs)
        if parsed_seg:
            return parsed_seg
    raise InvalidSegmentException(seg)


def append_basename_if_needed(cloud, local):
    """
        The local path can omit the basename part and this method will do appending smartly.
    """
    cloud_basename = path.basename(cloud)
    if cloud_basename.startswith('_'):
        cloud_basename = '.' + cloud_basename[1:]
    local_basename = path.basename(local)
    if cloud_basename != local_basename:
        if not local.endswith('/'):
            prefix = local + '/'
        else:
            prefix = local
        if path.isfile(cloud) and path.isdir(local):
            return prefix + cloud_basename
        if path.isdir(cloud) and path.isdir(local) and not is_sync_dir(local):
            return prefix + cloud_basename
    return local


def do_link(cloud, local):
    if path.isdir(local) and not path.islink(local):
        # don't delete the local dir, it's always dangerous
        print('The local directory already existed:', local, file=sys.stderr)
        return
    if path.islink(local) and path.realpath(local) == path.realpath(cloud):
        print('Untouched on', cloud, 'and', local)
        return
    if path.exists(local) or path.islink(local):
        # delete the existing normal file target or obsolete link target
        os.remove(local)
    try:
        # uses symlink because there may be directories to be linked
        os.symlink(path.abspath(cloud), local, path.isdir(cloud))
        print('Linked', cloud, 'to', local)
    except OSError:
        sys.exit('Cannot create symlink, make sure you have the right privilege for ' + local)


def do_copy_on_newer(cloud, local):
    # find which one is more recently modified - the newer one
    cloud_mtime = path.getmtime(cloud)
    if path.exists(local):
        local_mtime = path.getmtime(local)
    else:
        local_mtime = 0
    if cloud_mtime == local_mtime:
        print('Untouched on', cloud, 'and', local)
        return
    # TODO directory copy, depending on marker file timestamp
    # uses copy2() instead of copy() to retain mtime when copying
    if cloud_mtime > local_mtime:
        shutil.copy2(cloud, local)
        print('Copied', cloud, 'to', local)
    else:
        shutil.copy2(local, cloud)
        print('Updated', cloud, 'with', local)
