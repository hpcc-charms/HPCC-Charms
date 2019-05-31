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
from charms.reactive import hook, when, when_not

from charms.layer.hpcc_install import HPCCInstallation
from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig
from charms.layer.utils import SSHKey

@hook('install')
# all these should go to hpcc-platform lib/
def install_platform():
    if is_state('platform.installed'):
        return
    hpccInstaller = HPCCInstallation()
    hpccInstaller.install()
    # ssh keys?
    #config = hookenv.config()
    #if config['ssh-key-private']:
    #    install_keys_from_config(config)

    hpcc_config = HPCCConfig()
    hpcc_config.open_ports()

    set_state('platform.installed')

@hook('config-changed')
def config_changed():

    pass #not working correctly

    config = hookenv.config()
    if config.changed('ssh-key-private'):
        install_keys_from_config(config)

    #platform = HPCCSystemsPlatformConfig()
    #if config.changed('hpcc-version') or config.changed('hpcc-type'):
    #   hpcc_installed = platform.installed_platform()
    #   if (config.changed('hpcc-version') != hpcc_installed[0]) or \
    #      (config.changed('hpcc-type') != hpcc_installed[1]) :
    #      remove_state('platform.installed')
    #      platform.uninstall_platform()
    #      platform.install_platform()
    #      set_state('platform.installed')

    set_state('platform.installed')

def install_keys_from_config(config):
    sshKey = SSHKey('hpcc', 'hpcc', '/home/hpcc')
    priKey =  config['ssh-key-private']
    pubKey =  config['ssh-key-public']
    sshKey.install_key(priKey, pubKey)
    set_state('platform.sshkeys.changed')


@when('platform.installed')
@when_not('platform.configured')
@when_not('platform.started')
def configure_platform():
    #hpcc_config = HPCCConfig()
    #platform.open_ports()
    set_state('platform.configured')

# @when_not('platform.configured')?????
@when('platform.configured')
@when_not('platform.started')
@when_not('platform.start.failed')
def start_platform():
    
    config = hookenv.config()
    if config['node-type'] != 'standalone':
       hookenv.status_set('active', 'ready')
       set_state('platform.ready')
       return True

    remove_state('platform.started')
    remove_state('platform.start.failed')
    hpcc_init = HPCCInit()
    if hpcc_init.start():
       set_state('platform.start.failed')
       hookenv.status_set('blocked', 'hpcc start failed')
    else:
       set_state('platform.started')
       hookenv.status_set('active', 'started')

#@when('hpcc-esp.available')     
#def configure_esp(http):
#    http.configure(8010)
