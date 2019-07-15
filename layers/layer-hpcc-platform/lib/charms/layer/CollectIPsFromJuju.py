#!/usr/bin/python3
import os
import sys
import json

from  charms.layer.CollectIPs import CollectIPs

class CollectIPsFromJuju (CollectIPs):

    def __init__(self):
        '''
        constructor
        '''
        super(CollectIPs, self).__init__()

    def retrieveIPsFromCloud(self, input_fn):
        self.clean_dir(self._out_dir)
        with open(input_fn) as pods_ip_file:
           lines = pods_ip_file.readlines()

        for line in lines:
            full_node_name,node_ip = line.split(' ')
            node_name =  full_node_name.split('/')[0]
            if ( node_name.startswith('node')     or
                 node_name.startswith('dali')      or
                 node_name.startswith('esp')       or
                 node_name.startswith('thor')      or
                 node_name.startswith('roxiemaster')   or
                 node_name.startswith('roxie')     or
                 node_name.startswith('eclcc')     or
                 node_name.startswith('scheduler') or
                 node_name.startswith('backup')    or
                 node_name.startswith('sasha')     or
                 node_name.startswith('dropzone')  or
                 node_name.startswith('support')   or
                 node_name.startswith('spark')     or
                 node_name.startswith('ldap')):
                #print("node name: " + node_name)
                #print("node ip: " + node_ip)
                self.write_to_file(self._out_dir, node_name, node_ip + ";")

if __name__ == '__main__':

    cip = CollectIPsFromJuju()
    cip.main()
