#!/usr/bin/env python3

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag
from charms.reactive import Endpoint

class HPCCClusterRequires(Endpoint):

    scope = scopes.GLOBAL

    @when_any('endpoint.{endpoint_name}.changed.hostname',
              'endpoint.{endpoint_name}.changed.port')
    def new_cluster_admin(self): 
        set_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-admin'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.hostname'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.port'))

    @when_not('endpoint.{endpoint_name}.joined')
    def broken(self):
        clear_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-admin'))

    def cluster_admin(self):
        admin = []
        # Only one cluster admin unit at remote side
        relation = self.relations[0]
        unit = relation.units[0]
        hostname = unit.received['hostname']
        port = unit.received['port']

        admin['hostname']         = hostname       
        admin['port']             = port      
        admin['relation_id']      =  relation.relation_id
        admin['remote_unit_name'] =  unit.unit_name

        return admin  
   
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
