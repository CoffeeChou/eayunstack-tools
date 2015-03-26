from utils import set_logger
from utils import backup_list, backup_new

# Use the default DIR to backup

#logger = set_logger()

def backup(parser):
    logger = set_logger()
    if parser.NEW_BACKUP:
        new_backup(logger)
    if parser.LIST_BACKUP:
        list_backup()

def make(parser):
    '''Fuel Backup'''
    parser.add_argument(
        '-n',
        '--new',
        action = 'store_true',
        dest = 'NEW_BACKUP',
        default = False,
        help = 'Start A New Backup'
    )
    parser.add_argument(
        '-l',
        '--list',
        action = 'store_true',
        dest = 'LIST_BACKUP',
        default = False,
        help = 'List All Backups'
    )
    parser.set_defaults(func=backup)

def new_backup(logger):
    logger.info('Starting Backup ...')
    logger.info('It will take about 30 minutes, Please wait ...')
    (stat, out) = backup_new()
    if stat != 0:
        check = """
            * No deployment tasks are currently running.
            * You have at least 11GB free disk space in /var.
        """
        logger.error('Unexpected Error')
        logger.error('Please check the information below:\n %s', check)
    else:
        logger.info('Backup successfully completed!\n')
        print 'You can use "eayunstack fuel backup [ -l | --list ]" to list your backups\n'

def list_backup():
    t = backup_list()
    print t.get_string(sortby = 'ID')


