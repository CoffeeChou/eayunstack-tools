from utils import restore_backup
from utils import set_logger

#logger = set_logger()

def restore(parser):
    logger = set_logger()
    if parser.ID:
        restore_bck(parser.ID, logger)

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

def restore_bck(id, logger):
    logger.info('Starting Restore ...')
    logger.info('It will take about 30 minutes, Please wait ...\n')
    (stat, out) = restore_backup(id)
    if stat != 0:
        check = """
            * The Fuel version is the same release as the backup.
            * There are no deployments running.
            * At least 11GB free space in /var.
        """
        logger.error('Unexpected Error')
        logger.error('Please check the information below:\n %s', check)
        print out
    else:
        logger.info('Restore successfully completed!\n')

