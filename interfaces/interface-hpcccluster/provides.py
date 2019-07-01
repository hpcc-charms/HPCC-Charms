#!/usr/bin/env python3

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag, scopes
from charms.reactive import Endpoint
from charms.reactive.decorators import when, when_any, when_all, when_not

from charmhelpers import fetch
#from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG

from charms.layer.utils import (
     update_ip_files
)

class HPCCClusterProvides(Endpoint):

    scope = scopes.GLOBAL

    def publish_info(self, port=2380, hostname=None): 
        """
        Publish the port and hostname of the website over the relationship so
        it is accessible to the remote units at the other side of the
        relationship.

        If no hostname is provided, the unit's private-address is used.
        Etcd port for client: 2379, for server 2380
        """
        for relation in self.relations:
            relation.to_publish['hostname'] = hostname or hookenv.unit_get('private-address')
            relation.to_publish['port'] = port

    @when_any('endpoint.{endpoint_name}.changed.node-ip', 
              'endpoint.{endpoint_name}.changed.node-id')
    def process_node_ip_(self):
        log('process changed node_ip', INFO)
        result = True
        for relation in self.relations:
            for unit in relation.units:
                ip = unit.received['node-ip']
                id = unit.received['node-id']
                type = unit.received['node-type']
                if ip is None or id is None or type is None:
                   result = False
                   break
                log('node ip:' + ip, INFO) 
                log('node id: ' + id, INFO) 
                log('node type: ' + type, INFO)

                # add/modify cluster ip file
                update_ip_files(type, id, ip)
            if not result:
               break

        if result:
           self.publish_info()
           set_flag(self.expand_name('endpoint.{endpoint_name}.cluster-changed'))

           # clear following may not able to collect un-published nodes' ip 
           clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-ip'))
           clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-id'))
        

    #@when_any('endpoint.{endpoint_name}.changed.dali-state')
    #def new_dali_state(self):
    #    set_flag(self.expand_name('endpoint.{endpoint_name}.new-dali-state'))
    #    clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.dali-state'))

    #def get_dali_state(self):
    #    dali_state = []
    #
    #    # If admin unit save dali unit info following loop is un-necessary
    #    # Still need to find api can get received data from remote_unit_name, etc
    #    for relation in self.relations:
    #        done = False
    #        for unit in relation.units:
    #            node_type = unit.received['node-type']
    #            if (node_type == "dali"): 
    #                state = unit.received['dali-state'],
    #                dali_state['state'] =  state,
    #                dali_state['relation_id'] =  relation.relation_id,
    #                dali_state['remote_unit_name'] =  unit.unit_name
    #                done = True
    #            else:
    #                continue
    #        if done:
    #           break
    #    return dali_state

    @when('endpoint.{endpoint_name}.changed.node-state')
    @when('endpoint.{endpoint_name}.wait-nodes-stopped')
    @when_not('endpoint.{endpoint_name}.nodes-stopped')
    def process_stop_nodes(self):
        log('All nodes state changee', INFO)
        units_data = self.get_relation_data('node-state')
        all_nodes_stopped = True
        for unit_data in units_data:
            if not unit_data['state']:
               log('Some nodes node-state have not changed', INFO)
               all_nodes_stopped = False
               break
 
            if unit_data['state'] != 'stopped':
               log('Expect unit state:  stopped, but get ' + unit_data['state'], INFO)
               #set_flag(self.expand_name('endpoint.{endpoint_name}.stop-error'))
               return False

        if all_nodes_stopped:
           set_flag(self.expand_name('endpoint.{endpoint_name}.nodes-stopped'))
           clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-state'))


    def get_relation_data(self, data_name):
        units_data  = []
        for relation in self.relations:
            for unit in relation.units:
                state = unit.received[data_name]
                units_data.append({
                    'state': state,
                    'relation_id': relation.relation_id,
                    'remote_unit_name': unit.unit_name
                })
        return units_data

    def publish_relation_data(self, name, value): 
        log('Publish relation data: name=' + name  + ' value=' + value, INFO)
        for relation in self.relations:
            relation.to_publish[name] = value
        #clear_flag(self.expand_name('endpoint.{endpoint_name}.new-dali-state'))
        #clear_flag(self.expand_name('endpoint.{endpoint_name}.new-node-state'))
    

    @when('endpoint.{endpoint_name}.stopping-cluster')
    def stop_cluster(self):
        self.publish_relation_data('cluster-action', 'stop-node') 
        clear_flag(self.expand_name('endpoint.{endpoint_name}.stopping-cluster'))

    @when('endpoint.{endpoint_name}.starting-cluster')
    def start_cluster(self):
        self.publish_relation_data('cluster-action', 'start-node') 
        clear_flag(self.expand_name('endpoint.{endpoint_name}.starting-cluster'))
        #clear_flag('endpoint.{endpoint_name}.starting-cluster')

    @when('endpoint.{endpoint_name}.fetch-envxml')
    def fetch_envxml(self):
        self.publish_relation_data('cluster-action', 'fetch-envxml') 
        clear_flag(self.expand_name('endpoint.{endpoint_name}.fetch-envxml'))

    @when('endpoint.{endpoint_name}.changed.node-state')
    @when('endpoint.{endpoint_name}.wait-fetch-envxml')
    @when_not('endpoint.{endpoint_name}.envxml-fetched')
    def process_fetch_envxml(self):
        units_data = self.get_relation_data('node-state')
        all_nodes_fetched_envxml = True
        for unit_data in units_data:
            if not unit_data['state']:
               log('Some nodes node-state have not changed', INFO)
               all_nodes_fetched_envxml = False
               break
 
            if unit_data['state'] != 'envxml-fetched':
               log('Expect unit state:  envxml-fetched, but get ' + unit_data['state'], INFO)
               return False

        if all_nodes_fetched_envxml:
           clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-state'))
           set_flag(self.expand_name('endpoint.{endpoint_name}.envxml-fetched'))

    @when('endpoint.{endpoint_name}.changed.node-state')
    @when('endpoint.{endpoint_name}.wait-nodes-started')
    @when_not('endpoint.{endpoint_name}.nodes-started')
    def process_start_nodes(self):
        log('All nodes state changee', INFO)
        units_data = self.get_relation_data('node-state')
        all_nodes_started = True
        for unit_data in units_data:
            if not unit_data['state']:
               log('Some nodes node-state have not changed', INFO)
               all_nodes_stopped = False
               break
 
            if unit_data['state'] != 'started':
               log('Expect unit state:  started, but get ' + unit_data['state'], INFO)
               #set_flag(self.expand_name('endpoint.{endpoint_name}.start-error'))
               return False

        if all_nodes_started:
           clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-state'))
           set_flag(self.expand_name('endpoint.{endpoint_name}.nodes-started'))
