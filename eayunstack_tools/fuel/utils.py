import logging
import os
import commands
import time
from prettytable import PrettyTable

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'ERROR': RED,
    'INFO': GREEN
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

BASE_COLOR_FORMAT = "[ %(color_levelname)-17s ] %(message)s" 

BACKUP_DIR = '/var/backup/fuel'

dir_list = {}
file_list = {}

def formatter_message(message):
    message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.color_levelname = levelname_color
        return logging.Formatter.format(self, record)

def color_format():
    color_fmt = formatter_message(BASE_COLOR_FORMAT)
    return ColoredFormatter(color_fmt)

def set_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setFormatter(color_format())
    logger.addHandler(console)
    return logger

def backup_new():
    (stat, out) = commands.getstatusoutput('dockerctl backup')
    return (stat, out)

def backup_list():
    backup_dirs = os.listdir(BACKUP_DIR + '/')
    backup_dirs.sort(compare)
    i = 1
    t = PrettyTable(['ID', 'Create Time', 'File Name'])
    not_backup = 'restore'
    for backup_dir in backup_dirs:
        if not_backup in backup_dir:
            continue
        elif os.path.isfile(BACKUP_DIR + '/' + backup_dir):
            c_time = backup_dir[12:25] + ':' + backup_dir[25:27]
            backup_file = backup_dir
            file_list[i] = backup_file
        else:
            c_time = backup_dir[7:20] + ':' + backup_dir[20:22]
            backup_file = os.listdir(BACKUP_DIR + '/' + backup_dir + '/')
            dir_list[i] = backup_dir
            file_list[i] = backup_file[0]
        # Put the result in a dictory, every sub-dir has only one backup file
        t.add_row([i, c_time, file_list[i]])
        i += 1
    return t

def restore_backup(id):
    backup_list()
    if isinstance(id, int):
        if id in file_list.keys():
            backup_file = BACKUP_DIR + '/' + dir_list[id] + '/' + file_list[id]
            (stat, out) = commands.getstatusoutput('dockerctl restore %s' % (backup_file))
        else:
            print 'The ID does not exist! please retry.'
    else:
        print 'Please enter a integer number'
    return (stat, out)

# Sort the file, the file of most recent content modification will located at the end of the table
def compare(x, y): 
    stat_x = os.stat(BACKUP_DIR + '/' + x)
    stat_y = os.stat(BACKUP_DIR + '/' + y)
    if stat_x.st_mtime > stat_y.st_mtime:
        return 1
    elif stat_x.st_mtime < stat_y.st_mtime:
        return -1
    else:
        return 0

