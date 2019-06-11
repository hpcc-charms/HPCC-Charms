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

@when('endpoint.hpcc-dali.cluster-changed')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def cluster_change():
    set_state('cluster.changed')
    clear_flag('endpoint.reverseproxy.cluster-changed')
    set_flag('endpoint.reverseproxy.update-env')

@when('endpoint.hpcc-dali.update-env')
@when_not('endpoint.hpcc-dali.changed.node-ip')
def update_env():

    clear_flag('endpoint.reverseproxy.cluster-changed')
    set_flag('endpoint.reverseproxy.update-environment')

    hpcc_config = HPCCConfig()
    config = hookenv.config()
    hpcc_config.create_envxml(config, HPCCEnv.CLUSTER_CURRENT_IPS_DIR, 
        HPCCEnv.CONFIG_DIR + '/' + HPCCEnv.ENV_XML_FILE) 

    set_state('env.updated')


@hook('config-changed')
def dali_config_changed():

    config = hookenv.config()
    if  config['update-envxml'] == '': return

    if config.changed('update-envxml'):
       hpcc_config = HPCCConfig()
       hpcc_config.create_envxml(config, HPCCEnv.CLUSTER_CURRENT_IPS_DIR, 
           HPCCEnv.CONFIG_DIR + '/' + HPCCEnv.ENV_XML_FILE) 

    set_state('env.updated')


#@when('endpoint.hpcc-dali.joined')
#def add_ip_to_cluster():
    #ip = hookenv.remote_unit[]

#@when('endpoint.hpcc-dali.departed')
#@when('endpoint.hpcc-dali.broken')
#def remove_ip_from_cluster():
#   pass
