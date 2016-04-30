import os
import re
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

        self._source_kitten_binary = self.vim.vars['deoplete#sources#swift#source_kitten_binary']

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

        args = [self.source_kitten_binary(), "complete", "--file", fp.name, "--offset", str(offset)]

        process = subprocess.Popen(args,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   start_new_session=True)
        stdout_data, stderr_data = process.communicate()
        result = stdout_data.decode()

        os.remove(fp.name)

        if stderr_data != b'':
            raise Exception((args, stderr_data.decode()))

        results = json.loads(result)

        return self.identifiers_from_result(results)

    def identifiers_from_result(self, result):
        out = []

        candidates = []
        longest_desc_length = 0
        longest_desc = ''
        for complete in result:
            candidates.append(complete)

            desc_len = len(complete['name'])

            if desc_len > longest_desc_length:
                longest_desc = complete['name']
                longest_desc_length = desc_len

        for completion in candidates:
            description = completion['name']
            _type = completion['typeName']
            abbr = description + ' ' + _type.rjust((len(description) - longest_desc_length) + 1)
            info = _type

            candidate = dict(word=description,
                              abbr=abbr,
                              info=info,
                              dup=1
                              )

            out.append(candidate)

        return out

    def calltips_from_result(self, result):
        out = []

        result = result[1:]
        for calltip in result:
            candidate = dict(
                abbr=calltip,
                word=self.parse_function_parameters(calltip),
                info=calltip
            )

            out.append(candidate)

        return out

    def parse_function_parameters(self, decl):
        """Parses the function parameters from a function decl, returns them as a string"""
        last_lparen = decl.rfind('(')
        last_rparen = decl.rfind(')')

        param_list = decl[last_lparen + 1 : last_rparen]
        param_list = param_list.split(' ')
        # take only the names
        param_list = param_list[1::2]

        return ' '.join(param_list)

    def source_kitten_binary(self):
        try:
            if os.path.isfile(self._source_kitten_binary):
                return self._source_kitten_binary
            else:
                raise
        except Exception:
            return self.find_binary_path('sourcekitten')

    def find_binary_path(self, cmd):
        def is_exec(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(cmd)
        if fpath:
            if is_exec(cmd):
                return cmd
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                binary = os.path.join(path, cmd)
                if is_exec(binary):
                    return binary
        return error(self.vim, cmd + ' binary not found')

