# @file utils.py
import os
import logging
import collections
from eayunstack_tools.logger import fmt_excep_msg

LOG = logging.getLogger(__name__)

BACKUP_DIR = '/var/backup/fuel'


class BackupDB(object):
    def __init__(self, db='/.fuel.db'):
        self.db = db
        self.f_item = self._read_from_dir()
        self._init_db()

    def max_id(self, d=None):
        '''find the max id stored in db'''
        max = 0
        if d is None:
            d = self.read_all()
        for i in d.keys():
            if max <= i:
                max = i
        return max

    def _init_db(self):
        def _find_k(d, v):
            for k in d.keys():
                if d[k] == v:
                    return k

        # The filename is seen in db, but file not exists, delete it from db
        db_item = self.read_all()
        r = set(db_item.values()) - set(self.f_item)
        for f in r:
            db_item.pop(_find_k(db_item, f))

        # The file exists, but not found in db, add to db
        for d in self.f_item:
            if d not in db_item.values():
                db_item[self.max_id(db_item) + 1] = d

        # write to db
        with open(self.db, 'w') as f:
            self.write_all(db_item)

    def _read_from_dir(self, order=True):
        """Read from backup directory"""
        def cmp(x, y):
            stat_x = os.stat(x)
            stat_y = os.stat(y)
            if stat_x.st_ctime < stat_y.st_ctime:
                return 1
            elif stat_x.st_ctime > stat_y.st_ctime:
                return -1
            else:
                return 0
        ret = []
        for root, dirs, files in os.walk(BACKUP_DIR):
            for f in files:
                if f.endswith('.tar.lrz'):
                    f = os.path.join(root, f)
                    ret.append(f)
        if order:
            ret.sort(cmp)
        return ret

    def read(self, backup_id):
        db_item = self.read_all()
        return db_item[backup_id]

    def read_all(self):
        ret = collections.OrderedDict()
        try:
            with open(self.db, 'r') as f:
                for l in f:
                    if l.lstrip().startswith('#'):
                        continue
                    if len(l.split()) != 2:
                        continue
                    _id = int(l.split()[0])
                    f = l.split()[1]
                    ret[_id] = f
        except IOError:
            # do nothing, because user first run this script, file has not
            # been created
            return ret
        except Exception as e:
            LOG.error('open fuel datebase error: %s', fmt_excep_msg(e))
        return ret

    def write_all(self, db_item):
        with open(self.db, 'w') as f:
            f.write('# DO NOT EDIT THIS FILE BY HAND -- '
                    'YOUR CHANGES WILL BE OVERWRITTEN\n')
            for k, v in db_item.iteritems():
                f.write('%s %s\n' % (k, v))

    def write(self, f, db_id=None):
        db_item = self.read_all()
        if f not in db_item.values():
            if db_id is None:
                db_id = self.max_id()
            db_item[db_id] = f
            # Just write all item to file, no need to write with append flag
            self.write_all(db_item)

    def latest_backupfile(self):
        f = self._read_from_dir()
        return f[-1]


def latest_backup():
    """Get The Latest Backup File"""
    # The latest backup file means the new backup file
    # Use sorted() method to sort by filename
    backup_dirs = sorted(os.listdir(BACKUP_DIR + '/'))
    not_backup = 'restore'
    if len(backup_dirs) != 0:
        i = 1
        while True:
            if not_backup in backup_dirs[-i]:
                i += 1
            elif os.path.isfile(BACKUP_DIR + '/' + backup_dirs[-i]):
                # FIXME: Did not consider isfile
                i += 1
            else:
                latest_backup = os.listdir(BACKUP_DIR + '/' +
                                           backup_dirs[-i] + '/')[0]
                return latest_backup


def write_db(backup_id, backup_file):
    # append
    try:
        with open('/tmp/tools.db', 'a') as db:
            db.writelines('%s' % backup_id + ' ' + '%s\n' % backup_file)
    except Exception:
        LOG.error('Write to db error!')