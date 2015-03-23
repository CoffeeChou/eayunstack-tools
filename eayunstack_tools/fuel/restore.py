def restore(parser):
    print 'Not implemented'


def make(parser):
    '''Fuel Restore'''
    parser.add_argument(
        dest='PATH_TO_BACKUP',
        help='The path you took backup before',
    )
    parser.set_defaults(func=restore)
