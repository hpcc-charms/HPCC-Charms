#!/usr/bin/env python3

#import os
#import platform
#import yaml
#import re

## python 2.7
##import ConfigParser
## python 3
##import Configparser

#from subprocess import check_call,check_output,CalledProcessError
 
#from charmhelpers import fetch
#from charmhelpers.core import host
from charmhelpers.core import hookenv

   
class JujuEnv:
   STATUS_MSG = {
             'NODE_JOINED' : 'a new node joined',
             'NODE_DAPARTED' : 'a node departed',
             'CLUSTER_CHANGED' : 'cluster nodes are changed',
             'CLUSTER_CONFIGURED': 'cluster is ready to restart',
             'CLUSTER_STARTED' : 'cluster is started',
             'CLUSTER_STOPPED' : 'cluster is stopped',
             'DALI_STARTED'    : 'dali is started',
             'DALI_STOPPED'    : 'dali is stopped',
             'CLUSTER_START'   : 'starting cluster',
             'CLUSTER_RESTART' : 'resstarting cluster',
             'DALI_START'      : 'starting dali',
             'DALI_RESTART'    : 'restarting dali',
             'CLUSTER_STOP'    : 'stopping cluster',
             'DALI_STOP'       : 'stopping dali',
             'NODE_ACTION_ERR' : 'node action error',
             'NODE_CONFIGURED' : 'node is ready to restart',
             'NODE_STARTED'    : 'node is started',
             'NODE_STOPPED'    : 'node is stopped',
             'STARTING'        : 'starting',
             'RESTARTING'      : 'restarting',
             'STARTED'         : 'started',
             'STOPPED'         : 'stopped',
             'INSTALL_PLUGIN'  : 'install plugins',
             'PLUGIN_AVAILABLE': 'plugins available',
   }


def get_all_remote(conv, key):
    """
    Current conversation method get_remote implementation only
    return one value. But sometime we want get all remote key/value
    for conversation scope GLOBAL and SERVICE
    conv is the conversation to work with .
    This need to be called in a relation hook handler
    """
    values = {} 
    cur_rid = hookenv.relation_id()
    departing = hookenv.hook_name().endswith('-relation-departed')
    for relation_id in conv.relation_ids:
       units = hookenv.related_units(relation_id)
       if departing and cur_rid == relation_id:
          # Work around the fact that Juju 2.0 doesn't include the
          # departing unit in relation-list during the -departed hook,
          # by adding it back in ourselves.
          units.append(hookenv.remote_unit())
       for unit in units:
          if unit not in units:
             continue
          value = hookenv.relation_get(key, unit, relation_id)
          if value:
             values[unit] =  value
    return values

def all_related_units(relation_ids):
    units = []
    for relation_id in relation_ids:
       units.extend(hookenv.related_units(relation_id))

    return units

