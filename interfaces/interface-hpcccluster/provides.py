#!/usr/bin/env python3

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag, scopes
from charms.reactive import Endpoint
from charms.reactive.decorators import when_any, when_all, when_not

class HPCCClusterProvides(Endpoint):

    scope = scopes.GLOBAL

    def publish_info(self, port, hostname=None): 
        """
        Publish the port and hostname of the website over the relationship so
        it is accessible to the remote units at the other side of the
        relationship.

        If no hostname is provided, the unit's private-address is used.
        Etcd port for client: 2379, for server 2380
        """
        for relation in self.relations:
            relation.to_publish['hostname'] = hostname or hookenv.unit_get('private_address')
            relation.to_publish['port'] = port

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

    @when_all('endpoint.{endpoint_name}.changed.node-state')
    def new_node_state(self):
        set_flag(self.expand_name('endpoint.{endpoint_name}.new-node-state'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed.node-state'))

    def get_node_state(self):
        nodes_state  = []
        for relation in self.relations:
            for unit in relation.units:
                state = unit.received['node-state']
                nodes_state.append({
                    'state'            : state,
                    'relation_id'      : relation.relation_id,
                    'remote_unit_name' : unit.unit_name
               }) 
        return nodes_state

    def publish_cluster_action(self, action): 
        for relation in self.relations:
            relation.to_publish['cluster-action'] = action
        #clear_flag(self.expand_name('endpoint.{endpoint_name}.new-dali-state'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.new-node-state'))
    

