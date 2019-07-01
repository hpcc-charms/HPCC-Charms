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

from charmhelpers.core.hookenv import status_set


class HPCCClusterRequires(Endpoint):

    scope = scopes.GLOBAL

    @when_any('endpoint.{endpoint_name}.changed.hostname',
              'endpoint.{endpoint_name}.changed.port')
    def new_cluster_dali(self): 
        self.cluster_dali()
        set_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-dali'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.hostname'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.port'))

    @when('endpoint.{endpoint_name}.joined')
    @when_not('endpoint.{endpoint_name}.ip-published')
    def publish_node_private_ip(self):
        relation = self.relations[0]
        relation.to_publish['node-ip'] = hookenv.unit_private_ip()
        log('unit private ip: ' + hookenv.unit_private_ip(), INFO)
        relation.to_publish['node-id'] = hookenv.local_unit()
        log('unit id: ' + hookenv.local_unit(), INFO)
        relation.to_publish['node-type'] = hookenv.config()['node-type']
        log('unit type: ' + hookenv.config()['node-type'], INFO)
        status_set('active', hookenv.local_unit().split('/')[0] + '.joined')
        set_flag(self.expand_name('endpoint.{endpoint_name}.ip-published'))

    @when_not('endpoint.{endpoint_name}.joined')
    def broken(self):
        clear_flag(self.expand_name('endpoint.{endpoint_name}.new-cluster-dali'))

    def cluster_dali(self):
        # Only one cluster dali unit at remote side
        relation = self.relations[0]
        unit = relation.units[0]
        hostname = unit.received['hostname']
        port = unit.received['port']
        log('set dali hostname: ' + hostname, INFO)
        hookenv.relation_set(**{
           'dali-hostname': hostname,       
           'dali-etcd-port': port,      
           'dali-relation-id': relation.relation_id,
        })

    #       'dali-unit_name': unit.unit_name
   
    #def publish_node_type(self, type):
    #    relation = self.relations[0]
    #    relation.to_publish['node-type'] = type

    @when('endpoint.{endpoint_name}.changed.cluster-action')
    def new_action(self):
        action = self.get_relation_data('cluster-action')
        if not action: return

        log('New cluster action: ' + action, INFO)
        set_flag(self.expand_name('endpoint.{endpoint_name}.' + action))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.cluster-action'))

    def get_relation_data(self, name):
        relation = self.relations[0]
        unit = relation.units[0]
        return  unit.received[name]

    def publish_relation_data(self, name, value): 
        relation = self.relations[0]
        relation.to_publish[name] = value 

    @when('endpoint.{endpoint_name}.node-stopped')
    @when_not('endpoint.{endpoint_name}.node-wait')
    def process_node_stopped(self): 
        log('Publish node-state relation data: stopped', INFO)
        self.publish_relation_data('node-state', 'stopped') 
        set_flag(self.expand_name('endpoint.{endpoint_name}.node-wait'))

    @when('endpoint.{endpoint_name}.node-started')
    @when_not('endpoint.{endpoint_name}.node-wait')
    def process_node_started(self): 
        log('Publish node-state relation data: started', INFO)
        self.publish_relation_data('node-state', 'started') 
        set_flag(self.expand_name('endpoint.{endpoint_name}.node-wait'))


    @when('endpoint.{endpoint_name}.envxml-fetched')
    @when_not('endpoint.{endpoint_name}.node-wait')
    def process_envxml_fetched(self): 
        log('Publish node-state relation data: envxml-fetched', INFO)
        self.publish_relation_data('node-state', 'envxml-fetched') 
        set_flag(self.expand_name('endpoint.{endpoint_name}.node-wait'))
