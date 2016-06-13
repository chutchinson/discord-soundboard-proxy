import sys

__version__ = '0.0.1'

if sys.version_info < (3, 0):
    sys.stderr.write('unsupported Python version\n')
