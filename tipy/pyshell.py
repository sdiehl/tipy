"""
A modified version of the core interactive shell which handles
captures all execution output.
"""

import re
import sys
import argparse
import traceback
from code import InteractiveConsole, softspace
from pprint import pformat

from pygments.formatters import HtmlFormatter, get_formatter_by_name
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from pygments import highlight

passthru_commands = {
    #'dataframe' : lambda df: df.to_html(),
    #'tex'       : lambda sym: '$$%s$$' % latex(sym),
    #'inlinetex' : lambda sym: '$%s$' % latex(sym),
    #'numpy'     : lambda arr: '$$%s$$' % LatexPrinter()._print_ndarray(arr)[1:-2],
    'pprint1'   : lambda obj: highlight_python(pformat(obj, width=1)),
    'pprint'    : lambda obj: highlight_python(pformat(obj)),
    #'json'    :   lambda obj: highlight_json(simplejson.dumps(obj, indent=4))
}

def highlight_python(py_obj):
    _lexer = get_lexer_by_name('python')
    return highlight(py_obj, _lexer, formatter)

def highlight_json(py_obj):
    _lexer = get_lexer_by_name('json')
    return highlight(py_obj, _lexer, formatter)

def highlight_shell(py_obj):
    _lexer = get_lexer_by_name('bash')
    return highlight(py_obj, _lexer, formatter)

def filter_cat(args):
    """
    I can joinz non-empty str inputz?
    """
    ar = filter(lambda x: len(x) > 0, args)
    return '\n'.join(ar)

class FileCacher:
    def __init__(self):
        self.reset()

    def reset(self):
        self.out = []

    def write(self,line):
        self.out.append(line)

    def flush(self):
        output = ''.join(self.out)
        self.reset()
        return output

class Shell(InteractiveConsole):
    def __init__(self):
        self.stdout = sys.stdout
        self.cache = FileCacher()
        InteractiveConsole.__init__(self)
        return

    def get_output(self):
        sys.stdout = self.cache

    def return_output(self):
        sys.stdout = self.stdout

    def push(self,line):
        self.get_output()
        InteractiveConsole.push(self,line)
        self.return_output()
        output = self.cache.flush()
        return output.rstrip()

    def runcode(self, code):
        try:
            exec code in self.locals
        except SystemExit:
            raise
        except Exception:
            print traceback.format_exc()
        else:
            if softspace(sys.stdout, 0):
                print

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            print traceback.format_exc()
            return False

        #if code is not None and len(source) > 0:
            #print type(eval(source))

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code)
        return False

def exec_block(source, style, formatter):
    _lexer = get_lexer_by_name('pycon')

    formatter = get_formatter_by_name(formatter)
    formatter.style = get_style_by_name(style)

    interactions = []
    interp = Shell()

    passthru_output = []
    passthru_mode = False
    passthru_f = None

    for line in source.split('\n'):
        if 'pragma' in line:
            # Everything after pragma
            rawrgs = line.split(':')[1:]
            args = [ a.strip() for a in rawrgs ]
            directive = args[0]
            passthru_f = passthru_commands.get(directive)
            if not passthru_f:
                raise RuntimeError('Pragma `%s` directive unknown.' % directive)
            passthru_mode = True

        elif line.startswith('>>>') and passthru_mode:
            inline = line.split('>>> ')[1]
            try:
                retval = eval(inline, {}, interp.locals)
            except SyntaxError:
                raise RuntimeError('Passthru line must return a value')
            interactions += [(line, '')]
            passthru_output += [passthru_f(retval)]
            # TODO: this turned off does cool stuff
            passthru_mode = False

        elif line.startswith('>>>'):
            inline  = line.split('>>> ')[1]
            output = interp.push(inline)
            interactions += [(line, str(output))]

        elif line.startswith('...'):
            inline  = line.split('... ')[1]
            output = interp.push(inline)
            interactions += [(line, str(output))]

        else:
            inline = line
            output = interp.push(inline)
            interactions += [('', str(output))]

    # TODO: interleave passthru output with the corresponding
    # caller, right now it just appends it on the end.
    show = filter_cat(passthru_output)

    #if not isinstance(show, basestring):
        #if 'sympy' in show.__module__:
            #show = '$%s$' % latex(show, mode='inline')

    output = '\n'.join(filter_cat([a,b]) for a,b in interactions)
    return highlight(output, _lexer, formatter) + show

def preprocess_source(rawsource, style, formatter):
    CODE_REGEX = re.compile(r"```(?P<compiler>\w+)(?P<code>.*?)```", re.MULTILINE | re.DOTALL)

    def preprocess_block(matchobj):
        match    = matchobj.groupdict()
        compiler = match['compiler']
        source   = match['code']

        if compiler == 'pycon':
            return exec_block(source, style, formatter)
        else:
            return 'not python'

    return re.sub(CODE_REGEX, preprocess_block, rawsource, re.U)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', default='-', nargs='?', type=str)
    parser.add_argument('--style', default='colorful', type=str)
    parser.add_argument('--format', default='html', type=str)
    parser.add_argument('--css', action="store_true", help='Router service config')
    parser.add_argument('--preprocess', action="store_true", help='Preprocess a markdown file from stdin')

    args = parser.parse_args()

    if args.css:
        htmlformat = HtmlFormatter(style=args.style)
        sys.stdout.write(htmlformat.get_style_defs('.highlight'))
        sys.exit(0)

    if args.preprocess:
        source = sys.stdin.read()
        processed = preprocess_source(source, args.style, args.format)
        sys.stdout.write(processed)

    if args.source == '-' or not args.source:
        source = sys.stdin.read()
    else:
        source = open(args.source).read()

    stdout = exec_block(source, style=args.style, formatter=args.format)
    sys.stdout.write(stdout)

if __name__ == "__main__":
    main()
