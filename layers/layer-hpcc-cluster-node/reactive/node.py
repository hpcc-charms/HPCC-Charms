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
from charmhelpers.core.hookenv import status_set
from charms.reactive.bus import set_state
from charms.reactive.bus import get_state
from charms.reactive.bus import remove_state
from charms.reactive import (
     hook, when, when_not, set_flag, clear_flag, 
     endpoint_from_name, endpoint_from_flag
)

from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig
from charms.layer.hpccenv import HPCCEnv
from charms.layer.utils import has_component


@when('endpoint.hpcc-node.stop-node')
def stop_node():
    hpcc_init = HPCCInit()
    rc = hpcc_init.stop()
    if not rc:
       status_set('blocked', 'stop.error')
       return False

    clear_flag('endpoint.hpcc-node.stop-node')
    clear_flag('endpoint.hpcc-node.node-wait')
    set_flag('endpoint.hpcc-node.node-stopped')
    return True

@when('endpoint.hpcc-node.start-node')
def start_node():
    hpcc_init = HPCCInit()
    rc = hpcc_init.start()
    if not rc:
       status_set('blocked', 'start.error')
       return False

    clear_flag('endpoint.hpcc-node.node-stopped')
    clear_flag('endpoint.hpcc-node.start-node')
    clear_flag('endpoint.hpcc-node.node-wait')
    set_flag('endpoint.hpcc-node.node-started')
    status_set('active', 'HPCC started') 
    return True

@when('endpoint.hpcc-node.fetch-envxml')
def fetch_envxml():

    relation_id = hookenv.relation_id()
    if not relation_id:
       return True

    status_set('maintenance', 'fetch-envxml')

    log('relation_id: ' + relation_id, INFO)
    dali_ip = hookenv.relation_get('dali-hostname', hookenv.local_unit(), relation_id)
    if not dali_ip:
       # Wait dali_ip retrived
       return True
    log('dali_ip: ' + dali_ip, INFO)

    os.system("su hpcc -c \"scp -o StrictHostKeyChecking=no " + dali_ip + ":/etc/HPCCSystems/environment.xml /etc/HPCCSystems/\"")


    # open port
    hpcc_config =  HPCCConfig()
    config = hookenv.config()
    if (config['node-type'] == "esp" ):
        hpcc_config.open_ports()

    if ( (config['node-type'] == "node" )  or
         (config['node-type'] == "support" ) ):
         if has_component('esp', hookenv.unit_private_ip()):
            hpcc_config.open_ports()


    clear_flag('endpoint.hpcc-node.fetch-envxml')
    clear_flag('endpoint.hpcc-node.node-wait')
    set_flag('endpoint.hpcc-node.envxml-fetched')
    status_set('maintenance', 'envxml-fetched')
    return True


