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

class HPCCConfig (object):

    def __init__(self):
        self.config = hookenv.config()

    def open_ports(self):
        hookenv.status_set('maintenance', 'Open ports')
        #hookenv.open_port(self.config['esp-port'], 'TCP')

        #If this is esp, standalone node
        if ( (self.config['node-type'] == "standalone" ) or
             (self.config['node-type'] == "esp" ) ):
            hookenv.open_port(8010, 'TCP')
            hookenv.open_port(8002, 'TCP')
            hookenv.open_port(8015, 'TCP')
            hookenv.open_port(9876, 'TCP')

            hookenv.open_port(18010, 'TCP')
            hookenv.open_port(18002, 'TCP')
            hookenv.open_port(18008, 'TCP')
