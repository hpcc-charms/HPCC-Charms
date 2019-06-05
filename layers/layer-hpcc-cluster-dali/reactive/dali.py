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

from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig


#@when('endpoint.hpcc-dali.joined')
#def add_ip_to_cluster():
    #ip = hookenv.remote_unit[]

#@when('endpoint.hpcc-dali.departed')
#@when('endpoint.hpcc-dali.broken')
#def remove_ip_from_cluster():
#   pass
