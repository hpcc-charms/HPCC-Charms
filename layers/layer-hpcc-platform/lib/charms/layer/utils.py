#!/usr/bin/env python3
import os
import sys
import platform
import re
import fileinput

from subprocess import check_call, check_output, CalledProcessError
from pathlib import Path

from charmhelpers import fetch
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG
#from charmhelpers.core import templating


from charms.layer.hpccenv import HPCCEnv

IP_FILE_PATTERN =re.compile("^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*(;)?\s*$")
IP4_PATTERN =re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

class SSHKey(object):
    """
    This is helper class to manage SSH keys and related files
    """
    def __init__(self, user, group, home):
       self.user  = user
       self.group = group
       self.home  = home
   
    def key_dir(self):
       return Path(self.home + '/.ssh')

    def has_key(self):
        return self.ssh_pri_key().exists()

    def generate_key(self):
        sshDir = self.key_dir()
        if not sshDir.exists():
            host.mkdir(sshDir, owner=self.user, group=self.group, perms=0o755)
        priKeyFile = self.private_key()
        (sshDir + '/config').write_lines([
                'Host *',
                '    StrictHostKeyChecking no'
        ], append=True)
        check_call(['ssh-keygen', '-t', 'rsa', '-P', '', '-f', priKeyFile])
        host.chownr(sshDir, self.user, self.group)
        os.chmod(sshDir + '/rd_rsa', 0o600)
        os.chmod(sshDir + '/rd_rsa.pub', 0o644)
        with open(sshDir + '/rd_rsa.pub', 'r') as pubKeyFile:
           pubKey = pubKeyFile.read().replace('\n','')
        self.process_authorized_keys(pubKey)


    def install_key(self, priKey, pubKey):
        sshDir = self.key_dir()
        if not sshDir.exists():
            host.mkdir(sshDir, owner=self.user, group=self.group, perms=0o755)
        elif  pubKey in open(sshDir + '/id_rsa.pub').read():
            return
        Path(sshDir + '/id_rsa').write_text(priKey, append=False)
        Path(sshDir + '/id_rsa.pub').write_text(pubKey, append=False)
        os.chmod(sshDir + '/rd_rsa', 0o600)
        os.chmod(sshDir + '/rd_rsa.pub', 0o644)
        self.process_authorized_keys(pubKey)
          
    def process_authorized_keys(self, pubKey):
        authFile = self.key_dir() + '/authorized_keys'
        if authFile.exists():
            if pubKey in open(authFile).read():
                return
        Path(authFile).write_text(pubKey, append=False)
        os.chmod(authFile, 0o644)

    def pubic_key(self):
        return  self.key_dir() + '/id_rsa.pub'

    def private_key(self):
        return  self.key_dir() + '/id_rsa'


def package_extension():
     # will deal with other linux distro later
     return platform.linux_distribution()[2] + "_amd64.deb" 

def package_install_local_cmd():
     # will deal with other linux distro later
     return "dpkg -i" 

def package_install_repo_cmd():
     # will deal with other linux distro later
     return "apt install -y" 

def package_uninstall_cmd():
     # will deal with other linux distro later
     return "dpkg --purge" 

def batch_install(packages):
     # will deal with other linux distro later
    return fetch.apt_install(fetch.filter_installed_packages(packages))

def has_component(component, ip):
    try:
        if (not os.path.isfile(HPCCEnv.CONFIG_DIR + '/environment.xml')):
            return False

        cmd = [HPCCEnv.HPCC_HOME + '/sbin/configgen',
                  '-env', HPCCEnv.CONFIG_DIR + '/environment.xml',
                  '-t', component, '-listall2']
        print(*cmd)
        output = check_output(cmd)

        if ip.encode() in output:
            return True
       
    except CalledProcessError as e:
        log(e.output, ERROR)

    return False

def update_ip_files(type, unit_id, ip, dir=None):

    out_dir = dir
    if not out_dir:
       out_dir = HPCCEnv.CLUSTER_CURRENT_IPS_DIR 

    if type == 'node':
       ip_file_name = out_dir + '/' + unit_id.split('/')[0]
    elif type == 'support':
       ip_file_name = out_dir + '/support'
    elif type == 'thor' and unit_id.split('/')[0].startswith('master-'):
       ip_file_name = out_dir + '/' + type + unit_id.split('/')[0]
    else:
       ip_file_name = out_dir + '/' + type + '-' +  unit_id.split('/')[0]

    units_and_ips = out_dir + '/units_and_ips'
    
    open(ip_file_name, 'a').close()
    open(units_and_ips, 'a').close()
    
    result = 'UNIT-NOT-FOUND'
    current_ip = ''
    with open (units_and_ips) as file:
       for line in file:
         line_type, line_unit_id, line_ip = line.split()
         if line_unit_id == unit_id:
            if ip == line_ip:
               return False
            else:
               current_ip = line_ip
               result = 'IP-NOT-FOUND'
               break
            
    if result == 'UNIT-NOT-FOUND':
       write_unit_and_ip_to_file(units_and_ips, type, unit_id, ip)
       write_ip_to_file(ip_file_name, ip)
    elif result == 'IP-NOT-FOUND':
       replace_str_in_file(units_and_ips, current_ip, ip)
       replace_str_in_file(ip_file_name, current_ip, ip)

    return True

def write_ip_to_file(file_name, ip, mode='a'):
    f_ips = open(file_name, mode)
    f_ips.write(ip + ";\n")
    f_ips.close()
    return True

def write_unit_and_ip_to_file(file_name, type, unit_id, ip, mode='a'):
    f_ips = open(file_name, mode)
    f_ips.write(type + ' ' + unit_id + ' ' + ip + "\n")
    f_ips.close()
    return True

def replace_str_in_file(file_name, old_str, new_str):
    with fileinput.FileInput(file_name, inplace=True) as file:
         for line in file:  
             line.replace(old_str, new_str)
