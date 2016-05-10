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

        self.__source_kitten = SourceKitten(command=self.source_kitten_binary())

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = self.vim.current.window.cursor[0]
        column = context['complete_position']

        buf = self.vim.current.buffer
        offset = self.vim.call('line2byte', line) + \
            charpos2bytepos(self.vim, context['input'][: column], column) - 1
        source = '\n'.join(buf).encode()

        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".swift")
        fp.write(source)
        fp.flush()
        fp.close()

        client = self.__decide_completer(fp.name)
        try:
            results = client.complete(fp.name, offset)
        finally:
            os.remove(fp.name)

        return self.identifiers_from_result(results)

    def __decide_completer(self, path):
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

    def source_kitten_binary(self):
        path = self.vim.vars['deoplete#sources#swift#source_kitten_binary']
        if os.access(path, mode=os.X_OK):
            return path
        else:
            return self.find_binary_path('sourcekitten')

    def find_binary_path(self, cmd):
        path = shutil.which(cmd, mode=os.X_OK)
        if path is None:
            return error(self.vim, cmd + ' binary not found')

        return path


class SourceKitten(object):
    def __init__(self, command='sourcekitten'):
        self.__command = command

    def complete(self, path, offset):
        command_complete = [
            self.__command,
            'complete',
            '--file', path,
            '--offset', str(offset)
        ]

        stdout_data, stderr_data = SourceKitten.__execute(command_complete)
        result = stdout_data.decode()

        if stderr_data != b'':
            raise Exception((command_complete, stderr_data.decode()))

        return json.loads(result)

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
