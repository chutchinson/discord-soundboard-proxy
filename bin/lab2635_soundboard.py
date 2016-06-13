#!/usr/bin/python

import os
import sys

from optparse import OptionParser
from soundboard import proxy


def get_option_parser():

    parser = OptionParser(
        'usage: %prog [configuration_file]')

    opts = parser.add_option_group(
        'Configuration',
        'Configuration options')

    opts.add_option('-c', '--config',
                    default='./config.yaml',
                    dest='configfile',
                    help='configuration file path')

    return parser


def main():

    parser = get_option_parser()
    options, args = parser.parse_args()

    if not os.path.isfile(options.configfile):
        sys.stderr.write('missing configuration file')
        sys.exit(1)

    try:
        soundboard = proxy.DiscordSoundboardProxy()
        soundboard.configure(options.configfile)
        soundboard.run()
    except ValueError as e:
        sys.stderr.write('invalid configuration: %s' % str(e))
        sys.exit(1)
    except Exception as e:
        sys.stderr.write('unhandled error: %s' % str(e))
        sys.exit(1)
    finally:
        print("done")
        sys.exit(0)

if __name__ == '__main__':
    main()

