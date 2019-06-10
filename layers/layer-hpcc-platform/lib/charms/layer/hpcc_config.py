#!/usr/bin/env python3

import os
import sys
import platform
import yaml
import re
import getopt
import glob
# python 2.7
#import ConfigParser
# python 3
#import Configparser
from subprocess import check_call,check_output,CalledProcessError

from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG
#from charmhelpers.core import templating

from charms.layer.utils import has_component
import charms.layer.hpccenv
from charms.layer.hpccenv import HPCCEnv

class HPCCConfig (object):

    def __init__(self):
        self.config = hookenv.config()

    def open_ports(self):
        hookenv.status_set('maintenance', 'Open ports')
        #hookenv.open_port(self.config['esp-port'], 'TCP')

        #If this is esp, standalone node
        if ( (self.config['node-type'] == "standalone" ) or
             (self.config['node-type'] == "esp" ) ):
            hookenv.open_port(8010, 'TCP')
            hookenv.open_port(8002, 'TCP')
            hookenv.open_port(8015, 'TCP')
            hookenv.open_port(9876, 'TCP')

            hookenv.open_port(18010, 'TCP')
            hookenv.open_port(18002, 'TCP')
            hookenv.open_port(18008, 'TCP')
        else:
            if has_component('esp', hookenv.unit_private_ip()):
                hookenv.open_port(8010, 'TCP')
                hookenv.open_port(8002, 'TCP')
                hookenv.open_port(8015, 'TCP')
                hookenv.open_port(9876, 'TCP')

                hookenv.open_port(18010, 'TCP')
                hookenv.open_port(18002, 'TCP')
                hookenv.open_port(18008, 'TCP')
            else:
                hookenv.close_port(8010, 'TCP')
                hookenv.close_port(8002, 'TCP')
                hookenv.close_port(8015, 'TCP')
                hookenv.close_port(9876, 'TCP')

                hookenv.close_port(18010, 'TCP')
                hookenv.close_port(18002, 'TCP')
                hookenv.close_port(18008, 'TCP')
         
    def create_envxml(self, configs, ip_dir, out_file):
        node_ips_file = ip_dir + '/node'
        if os.path.isfile(node_ips_file):
           return self.create_simple_envxml(configs, node_ips_file, out_file)
        else:
           return self.create_complex_envxml(configs, ip_dir, out_file)
       

    def create_simple_envxml(self, configs, ip_file, out_file):

        support_nodes = configs['support-node'] 

        if 'esp-nodes' in configs:
            esp_nodes = configs['esp-nodes'] 
        else:
            esp_nodes = 1

        if 'roxie-nodes' in configs:
            roxie_nodes = configs['roxie-nodes'] 
        else:
            roxie_nodes = 1

        if 'thor-nodes' in configs:
            thor_nodes = configs['thor-nodes'] 
        else:
            thor_nodes = 1

        return self.create_default_envxml(configs, ip_file, out_file, 
            support_nodes, esp_nodes, roxie_nodes, thor_nodes)
          

    def create_default_envxml(self, configs, ip_file, out_file, 
            support_nodes, esp_nodes, roxie_nodes, thor_nodes): 

        cmd = []
        cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen')
        cmd.append('-env', out_file, '-ipfile', ip_file)
        cmd.append('-supportnodes', support_nodes) 
        cmd.append('-espnodes', esp_nodes) 
        #if esp_nodes > 0:
            #cmd.append('-override', 'esp', '@method', 'htpasswd') 

        cmd.append('-roxienodes', roxie_nodes) 
        if roxie_nodes > 0:
           if 'roxie-channels' in configs: 
               cmd.append('-roxieChannelsPerSlave', configs['roxie-channels']) 
           if 'roxie-on-demand' in configs:
               cmd.append('-roxieondemand', configs['roxie-on-demand']) 
           cmd.append('-override', 'roxie', '@copyResources', 'true')

        cmd.append('-thornodes', thor_nodes) 
        if thor_nodes > 0:
           if 'slave-per-node' in configs:
               cmd.append('-slavesPerNode', configs['slaves-per-node']) 
           if 'thor-channels' in configs:
               cmd.append('-thorChannelsPerSlave', configs['thor-channels']) 
           cmd.append('-override', 'thor', '@replicateOutputs','true') 
           cmd.append('-override', 'thor','@replicateAsync', 'true')       

        cmd.append('-assign_ips', 'dali', hookenv.unit-get('private-address')) 

        try:
            output = check_output(cmd, shell=True)
        except CalledProcessError as e:
            log(e.output, ERROR)
            return False

        if ((roxie_node) > 0 and ('cloud-type' in configs) and 
            (configs['cloud-type'] == 'aws')):
            cmd = []
            cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen2')
            cmd.append('-env-in', out_file, '-env-out', out_file)
            cmd.append('-cloud', configs['cloud-type']) 
            try:
                output = check_output(cmd, shell=True)
            except CalledProcessError as e:
                log(e.output, ERROR)
                return False

        return True

    def create_complex_envxml(self, configs, ip_dir, out_file):
        # Dali and Support nodes
        if os.path.isfile('ip_dir/support'):
           support_nodes = len(open(ip_dir/support).readlines())
        else:
           log("Missing support nodes.", ERROR)
           return False

        esp_ip_files = glob.glob(ip_dir/'esp*') 
        if len(esp_ip_files):
           esp_nodes = 0 
        else:
           if 'esp-nodes' in configs:
               esp_nodes = configs['esp-nodes'] 
           else:
               esp_nodes = 1

        rc = self.create_default_envxml(configs, ip_dir/support, out_file, 
            support_nodes, esp_nodes, 0, 0)

        if rc == False: return rc

        try:
            #Add esp
            if len(esp_ip_files):
               self.add_esp_envxml(configs, ip_dir, out_file)
        
            # Add Roxie
            roxie_ip_files = glob.glob(ip_dir/'roxie*') 
            if len(roxie_ip_files):
               self.add_roxie_envxml(configs, ip_dir, out_file)

            # Add Thor
            thor_ip_files = glob.glob(ip_dir/'thor*') 
            if len(thor_ip_files):
               self.add_thor_envxml(configs, ip_dir, out_file)

        except Exception as e:
            log(e.output, ERROR)
            return False

        return True

    def add_esp_envxml(self, configs, ip_dir, env_file):
        cmd = []
        cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen2')
        cmd.append('-env-in', env_file, '-env-out', env_file)

        esp_ip_files = glob.glob(ip_dir/'esp-*') 
        for esp_ip_file in esp_ip_files:
            ip_file = os.path.basename(roxie_ip_file)            
            comp, name = ip_file.split('-')            
            cmd.append('-add-node', comp + '#' + name + '@ipfile=' + esp_ip_file)

        try:
            output = check_output(cmd, shell=True)
        except CalledProcessError as e:
            raise Exception(e.output)

        return True

    def add_roxie_envxml(self, configs, ip_dir, env_file):
        cmd = []
        cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen2')
        cmd.append('-env-in', env_file, '-env-out', env_file)

        roxie_ip_files = glob.glob(ip_dir/'roxie-*') 
        for roxie_ip_file in roxie_ip_files:
            ip_file = os.path.basename(roxie_ip_file)            
            comp, name = ip_file.split('-')            
            cmd.append('-add-node', comp + '#' + name + '@ipfile=' + roxie_ip_file)
            # Will deal with roxieChannelsPerSlave and roxieondemand later
            cmd.append('-mod', comp + '#' + name + '@copyResources=true')

            # Add topology. Will deal input eclagent, scheduluer and eclcc later. Probably from etcd which set in  
            # each roxie application config.yaml
            cmd.append('-add-topology', 'topology:cluster@name=' + name + ':eclagent@process=myeclagent:eclscheduler@process=myeclscheduler:eclccserver@process=myeclccserver:roxie@process=' + name)
   
       # cloud. Make sure esp done already
        if 'cloud-type' in configs and (configs['cloud-type'] == 'aws'):
            cmd = []
            cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen2')
            cmd.append('-env-in', out_file, '-env-out', out_file)
            cmd.append('-cloud', configs['cloud-type']) 

        try:
            output = check_output(cmd, shell=True)
        except CalledProcessError as e:
            raise Exception(e.output)

        return True

    def add_thor_envxml(self, configs, ip_dir, env_file):
        cmd = []
        cmd.append(HPCCEnv.HPCC_HOME + '/sbin/envgen2')
        cmd.append('-env-in', env_file, '-env-out', env_file)

        thor_ip_files = glob.glob(ip_dir/'thor-*') 
        for thor_ip_file in thor_ip_files:
            ip_file = os.path.basename(thor_ip_file)            
            comp, name = ip_file.split('-')            

            master_file = ip_dir + '/thormaster-' + name
            if not os.path.isfile(master_file):
               raise Exception('Missing expected thor master file ' + master_file)
            with open(master_file, 'r') as file:
                master_ip = file.readlines()
                master_ip = master_ip.strip()

            cmd.append('-add-node', comp + '#' + name + 'master@ip=' + master_ip + ':slave@ipfile=' + thor_ip_file)
            # Will deal with thorChannelsPerSlave and slavesPerNode later
            cmd.append('-mod', comp + '#' + name + '@replicateOutputs=true^replicateAsync=true')       

            # Add topology. Will deal input eclagent, scheduluer and eclcc later. Probably from etcd which set in  
            # each roxie application config.yaml
            cmd.append('-add-topology', 'topology:cluster@name=' + name + ':eclagent@process=myeclagent:eclscheduler@process=myeclscheduler:eclccserver@process=myeclccserver:thor@process=' + name)
        try:
            output = check_output(cmd, shell=True)
        except CalledProcessError as e:
            raise Exception(e.output)

        return True

def usage():
    print("Usage hpcc_config.py [option(s)]\n")
    print("  -?, --help               print help")
    print("  -c  --chksum             script file md5 checksum")
    print("\n");


if __name__ == '__main__':

    ip_dir  = HPCCEnv.CLUSTER_CURRENT_IPS_DIR
    ip_file = ''
    output  =  '/etc/HPCCSystems/environment.xml'

    try:
        opts, args = getopt.getopt(sys.argv[1:],":d:f:o",
            ["help", "ip-dir","ip-file","output"])

    except getopt.GetoptError as err:
        print(str(err))
        usage()
        exit(0)

    for arg, value in opts:
        if arg in ("-?", "--help"):
           usage()
           exit(0)
        elif arg in ("-d", "--ip-dir"):
           ip_dir = value
        elif arg in ("-f", "--ip-file"):
           ip_file = value
        elif arg in ("-o", "--output"):
           output = value
        else:
           print("\nUnknown option: " + arg)
           usage()
           exit(0)

    hpcc_config = HPCCConfig()
    configs = hookenv.config()
    
    hpcc_config.create_envxml(configs, ip_dir, out_file)
