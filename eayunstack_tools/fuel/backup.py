def backup(parser):
    print 'Not implemented'


def make(parser):
    '''Fuel Backup'''
    parser.add_argument(
        '-n',
        '--new',
        action='store_const',
        const='new_backup',
        help='Start A New Backup'
    )
    parser.add_argument(
        '-l',
        '--list',
        action='store_const',
        const='list_backup',
        help='List All Backups'
    )
    parser.set_defaults(func=backup)
