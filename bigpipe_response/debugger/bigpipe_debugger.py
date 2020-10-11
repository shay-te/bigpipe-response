import os
from pathlib import Path

from ansi2html import Ansi2HTMLConverter

ansi_convert = Ansi2HTMLConverter(inline=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
content = Path(os.path.join(current_dir, 'debugger.html')).read_text()
css = Path(os.path.join(current_dir, 'debugger.css')).read_text()


class BigpipeDebugger(object):

    @staticmethod
    def get_exception_content(error_target, stacktrace: str, traceback: str):
        html = content.format(title=error_target, stacktrace=ansi_convert.convert(stacktrace.strip(), full=False), stacktrace_be=traceback)
        js = ''
        return html, js, css
