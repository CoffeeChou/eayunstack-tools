# @file restore.py
import logging
import utils


LOG = logging.getLogger(__name__)

def restore(parser):
    if parser.ID:
        restore_bck(parser.ID)

def make(parser):
    '''Fuel Restore'''
    parser.add_argument(
        '-i',
        '--id',
        action = 'store',
        dest = 'ID',
        type = int,
        help = 'Specify the ID you want to restore'
    )
    parser.set_defaults(func=restore)

def restore_bck(id):
    if isinstance(id, int):
        utils.backup_list()
        if id in utils.file_list.keys():
            LOG.info('Starting Restore ...')
            LOG.info('It will take about 30 minutes, Please wait ...\n')
            (stat, out) = utils.restore_backup(id)
            if stat != 0:
                check = """
            * The Fuel version is the same release as the backup.
            * There are no deployments running.
            * At least 11GB free space in /var.
                """
                LOG.error('Unexpected Error')
                LOG.error('Please check the information below:\n %s', check)
                print out
            else:
                LOG.info('Restore successfully completed!\n')
        else:
            LOG.error('The ID does not exist! please try again.\n')
    else:
        LOG.error('Please enter a integer number.\n')


