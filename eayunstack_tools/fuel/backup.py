from utils import backup_list, backup_new
import logging

# Use the default DIR to backup

LOG = logging.getLogger(__name__)

def backup(parser):
    if parser.NEW_BACKUP:
        new_backup()
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

def new_backup():
    LOG.info('Starting Backup ...')
    LOG.info('It will take about 30 minutes, Please wait ...')
    (stat, out) = backup_new()
    if stat != 0:
        check = """
            * No deployment tasks are currently running.
            * You have at least 11GB free disk space in /var.
        """
        LOG.error('Unexpected Error')
        LOG.error('Please check the information below:\n %s', check)
    else:
        LOG.info('Backup successfully completed!\n')
        print 'You can use "eayunstack fuel backup [ -l | --list ]" to list your backups\n'

def list_backup():
    t = backup_list()
    print t.get_string(sortby = 'ID')


