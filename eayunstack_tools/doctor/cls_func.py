from eayunstack_tools.utils import get_node_list, ssh_connect
import commands
import re
import logging

LOG = logging.getLogger(__name__)

# get masters or slaves node list for rabbitmq cluster
def get_rabbitmq_nodes(role):
    if role not in ['masters', 'slaves']: return
    role = role.capitalize()
    (s, o) = commands.getstatusoutput('pcs status resources | grep %s' % role)
    if s != 0 or o is None:
        return
    else:
        p = re.compile(r'     %s: \[ (.+) \]' % role)
        m = p.match(o).groups()
        return m[0].split()


# get running node list for mysql cluster
def get_mysql_nodes():
    running_nodes = []
    (s, o) = commands.getstatusoutput('crm_resource --locate --resource clone_p_mysql 2> /dev/null | grep "running on"')
    if s != 0 or o is None:
        return
    else:
        for entry in o.split('\n'):
            running_nodes.append(entry.split()[5])
    return running_nodes

# get running node list for haproxy cluster
def get_haproxy_nodes():
    running_nodes = []
    (s, o) = commands.getstatusoutput('crm_resource --locate --resource clone_p_haproxy 2> /dev/null | grep "running on"')
    if s != 0 or o is None:
        return
    else:
        for entry in o.split('\n'):
            running_nodes.append(entry.split()[5])
    return running_nodes

# get ceph cluster status
def get_ceph_health():
    (s, o) = commands.getstatusoutput('ceph health')
    if s != 0:
        return False
    else:
        if o == 'HEALTH_OK':
            return True
        else:
            return False

# get ceph osd status
def get_ceph_osd_status():
    (s, o) = commands.getstatusoutput('ceph osd tree')
    if s != 0 or o is None:
        return
    else:
        return o

# check all nodes
def check_all_nodes(check_obj):
    if check_obj is 'all':
        check_cmd = 'eayunstack doctor cls --all'
    else:
        check_cmd = 'eayunstack doctor cls -n %s' % check_obj
    # get controller node list
    node_list = get_node_list('controller')
    # ssh to all controller node to check obj
    if len(node_list) == 0:
        LOG.warn('Node list is null !')
        return
    else:
        for node in node_list:
            LOG.info('%s Node: %-13s %s' % ('*'*20, node, '*'*20))
            result_out,result_err = ssh_connect(node, check_cmd)
            print result_out