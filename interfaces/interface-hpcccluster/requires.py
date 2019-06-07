#!/usr/bin/env python3

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag, scopes
from charms.reactive import Endpoint
from charms.reactive.decorators import when, when_any, when_all, when_not

from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG


class HPCCClusterRequires(Endpoint):

    scope = scopes.GLOBAL

    @when_any('endpoint.{endpoint_name}.changed.hostname',
              'endpoint.{endpoint_name}.changed.port')
    def new_cluster_dali(self): 
        set_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-dali'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.hostname'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.port'))

    @when('endpoint.{endpoint_name}.joined')
    def publish_node_private_ip(self):
        relation = self.relations[0]
        relation.to_publish['private-ip'] = hookenv.unit_private_ip()
        relation.to_publish['unit-id'] = hookenv.local_unit()

    @when_not('endpoint.{endpoint_name}.joined')
    def broken(self):
        clear_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-dali'))

    def cluster_dali(self):
        dali = []
        # Only one cluster dali unit at remote side
        relation = self.relations[0]
        unit = relation.units[0]
        hostname = unit.received['hostname']
        port = unit.received['port']

        dali['hostname']         = hostname       
        dali['port']             = port      
        dali['relation_id']      =  relation.relation_id
        dali['remote_unit_name'] =  unit.unit_name

        return dali  
   
    def publish_node_type(self, type):
        relation = self.relations[0]
        relation.to_publish['node-type'] = type

    @when_any('endpoint.{endpoint_name}.changed.action')
    def new_action(self):
        set_flag(self.expand_name('endpoint.{endpoint_name}.new-action'))

    def publish_node_state(self, state): 
        relation in self.relations[0]
        relation.to_publish['node-state'] = state
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.action'))
