from eayunstack_tools.utils import get_node_list
from eayunstack_tools.sys_utils import ssh_connect2
import commands
import re
from eayunstack_tools.logger import StackLOG as LOG


# get node list for rabbitmq cluster
def get_rabbitmq_nodes():
    running_nodes = []
    (s, o) = commands.getstatusoutput('rabbitmqctl cluster_status | grep running_nodes')
    if s == 0:
        p = re.compile(r'{running_nodes,\[(.+)\]},')
        m = p.match(o.strip()).groups()
        running_nodes = []
        nodes = m[0].split(',')
        for node in nodes:
            pp = re.compile(r'\'rabbit@(.+)\'')
            mm = pp.match(node).groups()
            running_nodes.append(mm[0])
    return running_nodes



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
def ceph_check_health():
    def _log(func, msg):
        func('Ceph cluster check faild !')
        # FIXME: cause the log module issue, need to send error msg line 
        # by line
        for l in oo.split('\n'):
            func(l)

    (s, o) = commands.getstatusoutput('ceph health')
    if s != 0:
        return
    else:
        if o == 'HEALTH_OK':
            LOG.info('Ceph cluster check successfully !')
        else:
            (ss, oo) = commands.getstatusoutput('ceph -s')
            if o.startswith('HEALTH_WARN'):
                _log(LOG.warn, oo)
            else:
                _log(LOG.error, oo)


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
        if LOG.enable_debug:
            check_cmd = 'sudo eayunstack --debug doctor cls --all'
        else:
            check_cmd = 'sudo eayunstack doctor cls --all'
    else:
        if LOG.enable_debug:
            check_cmd = 'sudo eayunstack --debug doctor cls -n %s' % check_obj
        else:
            check_cmd = 'sudo eayunstack doctor cls -n %s' % check_obj
    # get controller node list
    node_list = get_node_list('controller')
    # ssh to all controller node to check obj
    if len(node_list) == 0:
        LOG.warn('Node list is null !')
        return
    else:
        if check_obj == 'ceph':
            # only need to check one node for ceph cluster
            ceph_node = node_list[0]
            LOG.info('%s Role: %-10s Node: %-13s %s'
                     % ('*'*15, 'controller', ceph_node, '*'*15))
            ssh_connect2(ceph_node, check_cmd)
        else:
            for node in node_list:
                LOG.info('%s Role: %-10s Node: %-13s %s'
                         % ('*'*15, 'controller', node, '*'*15))
                ssh_connect2(node, check_cmd)
