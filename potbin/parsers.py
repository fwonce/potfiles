from potbin.globals import *
from os import path

import abc
import appdirs
import configparser
import sys

__author__ = 'fwonce'


class InvalidSegmentException(Exception):
    """Thrown when a segment cannot be parsed by all the parsers."""

    def __init__(self, msg):
        self.msg = msg


class SegmentParser:
    __metaclass__ = abc.ABCMeta

    # parse the segment and if it doesn't apply here just return None
    @abc.abstractmethod
    def parse(self, seg, expanded_segs):
        return None


class DeclParser(SegmentParser):
    def parse(self, seg, expanded_segs):
        if seg in declared_segs:
            return declared_segs[seg]


class HomeParser(SegmentParser):
    def parse(self, seg, expanded_segs):
        if '$userhome' == seg:
            return path.expanduser('~')


class AppFolderParser(SegmentParser):
    def parse(self, seg, expanded_segs):
        if seg.startswith('$appfolder'):
            argstr = seg.lstrip('$appfolder(').rstrip(')')
            args = [arg.strip(' \'') for arg in argstr.split(',')]
            if 1 == len(args):
                return appdirs.user_data_dir(args[0])
            if 2 == len(args):
                return appdirs.user_data_dir(args[0], args[1])


class IniFileParser(SegmentParser):
    def parse(self, seg, expanded_segs):
        if seg.startswith('$iniparser'):
            argstr = seg.lstrip('$iniparser(').rstrip(')')
            args = [arg.strip(' \'') for arg in argstr.split(',')]
            if 3 == len(args):
                preceeding_path = '/'.join(expanded_segs)
                ini_path = preceeding_path + '/' + args[0]
                if path.exists(ini_path):
                    try:
                        ini = configparser.ConfigParser()
                        ini.read(ini_path)
                        return ini.get(args[1], args[2])
                    except configparser.Error:
                        raise InvalidSegmentException('cannot read' + ini_path)


class PlatformParser(SegmentParser):
    def parse(self, seg, expanded_segs):
        if '$sysplatform' == seg:
            return sys.platform

# Parser singletons
ALL_PARSERS = [
    DeclParser(),
    HomeParser(),
    AppFolderParser(),
    IniFileParser(),
    PlatformParser()
]
