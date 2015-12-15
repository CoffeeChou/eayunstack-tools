import socket
import commands
import logging
import paramiko
import os
import subprocess
import traceback
import json
from eayunstack_tools.logger import StackLOG as LOG


def ssh_connect(hostname, commands,
                key_file=os.environ['HOME'] + '/.ssh/id_rsa',
                ssh_port=22, username='root', timeout=2):
    # Temporarily disable INFO level logging
    logging.disable(logging.INFO)
    # need use rsa key, if use dsa key replace 'RSA' to 'DSS'
    key = paramiko.RSAKey.from_private_key_file(key_file)
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        s.connect(hostname, ssh_port, username=username,
                  pkey=key, timeout=timeout)
        stdin, stdout, stderr = s.exec_command(commands)
        result_out = stdout.read()
        result_err = stderr.read()
    except paramiko.ssh_exception.AuthenticationException:
        result_out = result_err = ''
        LOG.error('Can not connect to %s, Authentication (publickey) '
                  'failed !' % (hostname))
    except socket.timeout:
        result_out = result_err = ''
        LOG.error('Can not connect to %s, Connect time out !' % (hostname))
    except socket.error:
        result_out = result_err = ''
        LOG.error('Can not connect to %s, Connect Destination Host Unreachable !' %(hostname))
    finally:
        s.close()
        logging.disable(logging.NOTSET)
    return result_out, result_err


def ssh_connect2(hostname, commands):
    """exec ssh command and print the result """
    out, err = ssh_connect(hostname, commands)
    if out:
        LOG.info(out, remote=True)
    elif err:
        LOG.info(err, remote=True)
    return out, err


def scp_connect(hostname, local_path, remote_path,
                key_file=os.environ['HOME'] + '/.ssh/id_rsa', username='root',
                port=22, timeout=2):
    logging.disable(logging.INFO)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        key = paramiko.RSAKey.from_private_key_file(key_file)
        ssh.connect(hostname=hostname, username=username, port=port,
                    pkey=key, timeout=timeout)
        sftp = ssh.open_sftp()
        try:
            sftp.chdir(os.path.dirname(remote_path))
        except IOError:
            sftp.mkdir(os.path.dirname(remote_path))
        sftp.put(local_path, remote_path)
        sftp.close()
    except socket.timeout:
        LOG.error('Can not connect to %s, connection timeout !' % hostname)
    except socket.error:
        LOG.error('Can not connect to %s !' % hostname)
    except paramiko.ssh_exception.AuthenticationException:
        LOG.error('SSH Authentication failed for user %s !' % username)
    except IOError as msg:
        LOG.error('IOError: %s' % msg)
    finally:
        ssh.close()
        logging.disable(logging.NOTSET)

def scp_connect2(hostname, local_path, remote_path,
                username, password, port=22, timeout=2):
    success = False
    logging.disable(logging.INFO)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, username=username, password=password,
                    port=port, timeout=timeout)
        sftp = ssh.open_sftp()
        try:
            sftp.chdir(os.path.dirname(remote_path))
        except IOError:
            sftp.mkdir(os.path.dirname(remote_path))
        sftp.put(local_path, remote_path)
        sftp.close()
        success = True
    except socket.timeout:
        LOG.error('Can not connect to %s, connection timeout !' % hostname)
    except socket.error:
        LOG.error('Can not connect to %s !' % hostname)
    except paramiko.ssh_exception.AuthenticationException:
        LOG.error('SSH Authentication failed for user %s !' % username)
    except IOError as msg:
        LOG.error('IOError: %s' % msg)
    finally:
        ssh.close()
        logging.disable(logging.NOTSET)
        return success


def ping(peer):
    (status, out) = commands.getstatusoutput('ping -c 1 %s' % (peer))
    if status == 0:
        LOG.debug('%s reached' % peer)
    else:
        LOG.error('%s can not be reached!' % peer)

def run_command(cmd, shell=True, cwd=None):
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        (stdout, stderr) = proc.communicate()
        stdout = stdout.rstrip('\n')
        returncode = proc.returncode
    except Exception as e:
        LOG.error("Cannot execute command '%s': %s : %s" %
                          (cmd, str(e), traceback.format_exc()))
        stdout = None
        stderr = str(e)
        returncode = 1
    return (stdout, stderr, returncode)

def run_command_on_node(host_id, cmd):
    docker_container = 'fuel-core-6.0.1-astute'
    local_cmd = 'docker exec ' \
              + docker_container \
              + ' mco rpc --with-identity ' \
              + str(host_id) \
              + ' --agent execute_shell_command --action execute ' \
              + '--argument cmd="' \
              + cmd \
              + '" -j'
    (out, err, returncode) = run_command(local_cmd)
    stdout = stderr = exitcode = None
    if returncode == 0 and err == '' and out != '':
        res = json.loads(out)[0]
        data = res['data']
        stdout = data['stdout']
        stderr = data['stderr']
        exitcode = data['exit_code']
    else:
        exitcode = 1
    return (stdout, stderr, exitcode)

