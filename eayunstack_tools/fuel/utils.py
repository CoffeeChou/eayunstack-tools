# @file utils.py
import os
import commands
import time
from prettytable import PrettyTable
import logging

LOG = logging.getLogger(__name__)

BACKUP_DIR = '/var/backup/fuel'

dir_list = {}
file_list = {}

def backup_new():
    (stat, out) = commands.getstatusoutput('dockerctl backup')
    return (stat, out)

def backup_list():
    backup_dirs = os.listdir(BACKUP_DIR + '/')
    backup_dirs.sort(compare)
    i = 1
    t = PrettyTable(['ID', 'Create Time', 'File Name'])
    # when taking restore, there will be dirs named 'restore'. will not list 'restore' dir.
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
    backup_file = BACKUP_DIR + '/' + dir_list[id] + '/' + file_list[id]
    (stat, out) = commands.getstatusoutput('dockerctl restore %s' % (backup_file))
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

