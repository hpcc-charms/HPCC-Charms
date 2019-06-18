#!/usr/bin/env python3

import os
import platform
import yaml
import re
#import Configparser
from subprocess import check_call,check_output,CalledProcessError

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

from charms.reactive.helpers import is_state
from charms.reactive.bus import set_state
from charms.reactive.bus import get_state
from charms.reactive.bus import remove_state
from charms.reactive import hook, when, when_not, set_flag, clear_flag

from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig
from charms.layer.hpccenv import HPCCEnv

@when('endpoint.hpcc-dali.joined')
def publish_dali_server(self):
    dali_server = endpoint_from_flag('endpoint.hpcc-dali.joined')
    dali_server.publish_info()

@when('endpoint.hpcc-dali.cluster-changed')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def cluster_change():
    set_state('cluster.changed')
    clear_flag('endpoint.hpcc-dali.cluster-changed')
    config = hookenv.config()
    if config['auto-envxml']:
       set_flag('endpoint.hpcc-dali.update-env')

@when('endpoint.hpcc-dali.update-env')
@when_not('endpoint.hpcc-dali.cluster-stopped')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def stop_cluster():
    log('Stop other cluster nodes before dali', INFO)
    set_state('stopping.cluster')
    set_flag('endpoint.hpcc-dali.stopping-cluster')
    
@when('endpoint.hpcc-dali.update-env')
@when('endpoint.hpcc-dali.cluster-stopped')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def update_env():

    clear_flag('endpoint.hpcc-dali.cluster-changed')

    hpcc_config = HPCCConfig()
    config = hookenv.config()
    hpcc_config.create_envxml(config, HPCCEnv.CLUSTER_CURRENT_IPS_DIR, 
        HPCCEnv.CONFIG_DIR + '/' + HPCCEnv.ENV_XML_FILE) 

    set_flag('endpoint.hpcc-dali.env-updated')
    set_state('env.updated')

@when('endpoint.hpcc-dali.env-updated')
def fetch_env():
    clear_flag('endpoint.hpcc-dali.env-updated')
    set_flag('endpoint.hpcc-dali.fetch-envxml')


@when('endpoint.hpcc-dali.envxml-fetched')
@when_not('endpoint.hpcc-dali.cluster-started')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def start_cluster():
    # start dali
    hpcc_init = HPCCInit()
    rc = hpcc_init.start()
    if not rc: 
       set_state('start.dali.error')
       return False

    set_state('HPCC.started')

    # start rest of cluster nodes
    clear_flag('endpoint.hpcc-dali.envxml-fetched')
    set_flag('endpoint.hpcc-dali.starting-cluster')

@when('endpoint.hpcc-dali.nodes-started')
def cluster_started():
    clear_flag('endpoint.hpcc-dali.nodes-started')
    clear_flag('endpoint.hpcc-dali.cluster-stopped')
    set_flag('endpoint.hpcc-dali.cluster-started')

@hook('config-changed')
def dali_config_changed():

    config = hookenv.config()
    if  config['update-envxml'] == '': return

    if config.changed('update-envxml'):
        set_flag('endpoint.hpcc-dali.update-env')


@when('endpoint.hpcc-dali.nodes-stopped')
def stop_dali():
    hpcc_init = HPCCInit()
    rc = hpcc_init.stop()
    if not rc: 
       set_state('stop.dali.error')
       return False

    clear_flag('endpoint.hpcc-dali.nodes-stopped')
    set_flag('endpoint.hpcc-dali.cluster-stopped')
    set_state('HPCC stopped')
    return True

@when('endpoint.hpcc-dali.stop-error')
def process_stop_error():
    log('Stop other nodes failed', ERROR)
    set_state('cluster_stop_error')
