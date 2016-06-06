import os
import re
import shutil
import subprocess
import sys
import json
import tempfile

from .base import Base

from deoplete.util import charpos2bytepos
from deoplete.util import error

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'Swift'
        self.mark = '[Swift]'
        self.filetypes = ['swift']
        self.input_pattern = r'(?:\b[^\W\d]\w*|[\]\)])(?:\.(?:[^\W\d]\w*)?)*\(?'
        self.rank = 500
        self.encoding = self.vim.options['encoding']

        try:
            self.__source_kitten = SourceKitten(
                path=vim.vars['deoplete#sources#swift#source_kitten_binary']
            )
        except SourceKittenNotFound as exception:
            error(vim, '{} binary not found'.format(exception.path))

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = self.vim.current.window.cursor[0]
        column = context['complete_position']

        buf = self.vim.current.buffer
        offset = self.vim.call('line2byte', line) + \
            charpos2bytepos(self.encoding, context['input'][: column], column) - 1
        source = '\n'.join(buf).encode()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".swift") as fp:
            fp.write(source)
            path = fp.name

        completer = self.__choose_completer(path)
        try:
            results = completer.complete(path, offset)
        finally:
            os.remove(path)

        return self.identifiers_from_result(results)

    def __choose_completer(self, path):
        return self.__source_kitten

    def identifiers_from_result(self, result):
        def convert(candidate):
            description = candidate['sourcetext']
            _type = candidate['typeName']
            abbr = '{} {}'.format(candidate['name'], _type)
            info = _type

            return dict(
                word=description,
                abbr=abbr,
                info=info,
                dup=1
            )

        return [convert(candidate) for candidate in result]


class SourceKitten(object):
    def __init__(self, path=None):
        self.__command = SourceKitten.validate_command(path)

    def complete(self, path, offset):
        command_complete = [
            self.__command,
            'complete',
            '--file', path,
            '--offset', str(offset)
        ]

        stdout_data, stderr_data = SourceKitten.__execute(command_complete)
        if stderr_data != b'':
            raise SourceKittenCompletionFailed(path, offset, stderr.decode())

        return json.loads(stdout_data.decode())

    @staticmethod
    def __execute(command):
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        return process.communicate()

    @staticmethod
    def validate_command(path):
        if os.access(path, mode=os.X_OK):
            return path

        default = shutil.which('sourcekitten', mode=os.X_OK)
        if default is None:
            raise SourceKittenNotFound(default)

        return default


class SourceKittenCompletionFailed(Exception):
    def __init__(self, path, offset, error):
        self.__path = path
        self.__offset = offset
        self.__error = error

    @property
    def path(self):
        return self.__path

    @property
    def offset(self):
        return self.__offset

    @property
    def error(self):
        return self.__error


class SourceKittenNotFound(Exception):
    def __init__(self, path):
        self.__path = path

    @property
    def path(self):
        return self.__path
