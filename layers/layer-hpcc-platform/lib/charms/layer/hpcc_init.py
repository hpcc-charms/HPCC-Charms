#!/usr/bin/env python3

import os
import platform
import yaml
import re
# python 2.7
#import ConfigParser
# python 3
#import Configparser
from subprocess import check_call,check_output,CalledProcessError

from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG
#from charmhelpers.core import templating

import charms.layer.utils
import charms.layer.hpccenv
from charms.layer.hpccenv import HPCCEnv

class HPCCInit (object):

    def __init__(self):
        self.config = hookenv.config()
        #log("config.yaml:", INFO)

    def start(self):
        hookenv.status_set('maintenance', 'Starting HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init start', INFO)
        try:
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'start'])
            log(output, INFO)
        except CalledProcessError as e:
            log(e.output, ERROR)
            return False

        return True

    def stop(self):
        hookenv.status_set('maintenance', 'Stopping HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init stop', INFO)
        try:
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'stop'])
            log(output, INFO)
        except CalledProcessError as e:
            log(e.output, ERROR)
            hookenv.status_set('maintenance', 'Error in stopping HPCC')
            return False

        hookenv.status_set('active', 'HPCC stopped')
        return True

    def restart(self):
        hookenv.status_set('maintenance', 'Restarting HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init stop', INFO)
        try:
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'restart'])
            log(output, INFO)
        except CalledProcessError as e:
            log(e.output, ERROR)
            return False

        return True

    def is_running(self):
        try:
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'status'], shell=True)
            log(output, INFO)
        except CalledProcessError as e:
            log(e.output, INFO)
            return False

        return True
